from django.db import models
from backend.models import User
from backend.signals import tournament_started_signal, tournament_updated_signal
from django.contrib.postgres.fields import ArrayField, HStoreField
from django.db.models import JSONField
from django.utils import timezone
import random, secrets, time, logging

logger = logging.getLogger('pong')

class Tournament(models.Model):
	TOURNAMENT_STATUS = [
		('REGISTERING', 'Registering'),
		('IN_PROGRESS', 'In Progress'),
		('COMPLETED', 'Completed'),
	]

	tournament_id = models.CharField(max_length=100, unique=True)
	max_players = models.IntegerField(default=4)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	winner = models.CharField(max_length=150, null=True)
	winner_id = models.CharField(max_length=150, null=True)
	players = ArrayField(models.CharField(max_length=150), default=list)
	player_ids = HStoreField()
	rounds = JSONField(default=list)
	current_round = models.IntegerField(default=0)
	current_round_created_at = models.DateTimeField(auto_now_add=True)
	status = models.CharField(
		max_length=20,
		choices=TOURNAMENT_STATUS,
		default='REGISTERING'
	)

	@classmethod
	def map_players(cls, user):
		return {str(user.uuid): user.username}
	

	@classmethod
	def create_tournament(cls, tournament_id: str, players: list):
		
		player_mapping = {}
		for username in players:
			user = User.objects.get(username=username)
			player_mapping.update(cls.map_players(user))

		return cls.objects.create(
			tournament_id=tournament_id,
			players=players,
			player_ids=player_mapping,
			rounds=[], 
			current_round=0
		)
	
	@classmethod
	def player_in_tournament(cls, player_id : str) -> bool: # check for uuid instead
		return cls.objects.filter(
			player_ids__has_key=player_id,
			status__in=['REGISTERING', 'IN_PROGRESS']
		).exists()
	
	@classmethod
	def update_user_rank(cls, uuid):
		if uuid:
			try:
				user = User.objects.get(uuid=uuid)
				user.rank = user.rank + 5
				user.save()
			except User.DoesNotExist:
				pass

	def generate_game_id(self) -> str:
		timestamp = int(time.time())
		token = secrets.token_hex(4)
		return f"tg:{timestamp}:{token}"


	def start_tournament(self) -> bool:
		if self.status != 'REGISTERING' or len(self.players) != self.max_players:
			return False
			
		if self.max_players % 2 != 0:
			return False
			
		players = self.players.copy()
		random.shuffle(players)
		
		matches = []
		for i in range(0, len(players), 2):
			matches.append({
				'player1': players[i],
				'player2': players[i + 1],
				'winner': None,
				'game_id': self.generate_game_id(),
				'status': 'PENDING'
			})
		
		self.rounds = [matches]
		self.current_round_created_at = timezone.now()
		self.status = 'IN_PROGRESS'
		self.save()
		tournament_started_signal.send(sender=self, instance=self)
		return True


	def create_next_round(self) -> bool:
		if self.status != 'IN_PROGRESS':
			return False

		current_round = self.rounds[self.current_round]
		
		if not all(match['status'] == 'COMPLETED' for match in current_round):
			return False

		players = [match['winner'] for match in current_round]
		if len(players) == 1:
			self.status = 'COMPLETED'
			self.winner = players[0]

			self.winner_id = next((uuid for uuid, username in self.player_ids.items() 
					if username == players[0]), None)

			self.update_user_rank(self.winner_id)
			self.save()
			return True

		next_round = []
		for i in range(0, len(players), 2):
			if i + 1 < len(players):
				next_round.append({
					'player1': players[i],
					'player2': players[i + 1],
					'winner': None,
					'game_id': self.generate_game_id(),
					'status': 'PENDING'
				})
			else:
				# no opponent gets bye
				next_round.append({
					'player1': players[i],
					'player2': None,
					'winner': players[i],
					'game_id': None,
					'status': 'COMPLETED'
				})
		
		self.rounds.append(next_round)
		self.current_round += 1
		self.current_round_created_at = timezone.now()
		self.save()
		tournament_updated_signal.send(sender=self, instance=self)
		return True