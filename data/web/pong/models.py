from django.db import models
from django.contrib.postgres.fields import ArrayField
import random, secrets, time

class Game(models.Model):
	game_id = models.CharField(max_length=100, unique=True)
	player1_username = models.CharField(max_length=150)
	player1_sets = models.IntegerField(default=0)
	player2_username = models.CharField(max_length=150)
	player2_sets = models.IntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		abstract = True

class OngoingGame(Game):
	@classmethod
	def create_game(cls, game_id, username1, username2=None):
		return cls.objects.create(
			game_id=game_id,
			player1_username=username1,
			player2_username=username2
		)

	@classmethod
	def player_in_game(cls, username):
		return cls.objects.filter(
			models.Q(player1_username=username) | 
			models.Q(player2_username=username)
		).values_list('game_id', flat=True).first()

	@classmethod
	def delete_game(cls, game_id):
		cls.objects.filter(game_id=game_id).delete()

	@classmethod
	def update_score(cls, game_id : str, player1_sets : int, player2_sets : int):
		game = cls.objects.get(game_id=game_id)
		if not game:
			return
		game.player1_sets = player1_sets
		game.player2_sets = player2_sets
		game.save()

class CompletedGame(Game):
	winner_username = models.CharField(max_length=150)
	completed_at = models.DateTimeField(auto_now_add=True)

	@classmethod
	def create_from_ongoing(cls, ongoing_game, winner: str):
		return cls.objects.create(
			game_id=ongoing_game.game_id,
			player1_username=ongoing_game.player1_username,
			player2_username=ongoing_game.player2_username,
			player1_sets=ongoing_game.player1_sets,
			player2_sets=ongoing_game.player2_sets,
			winner_username=winner
		)
	

class Tournament(models.Model):
	TOURNAMENT_STATUS = [
		('REGISTERING', 'Registering'),
		('IN_PROGRESS', 'In Progress'),
		('COMPLETED', 'Completed'),
	]

	tournament_id = models.CharField(max_length=100, unique=True)
	max_players = models.IntegerField(default=6)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	winner = models.CharField(max_length=150, null=True)
	players = ArrayField(models.CharField(max_length=150), default=list)
	rounds = ArrayField(ArrayField(models.JSONField(default=dict), default=list), default=list)
	current_round = models.IntegerField(default=0)
	status = models.CharField(
		max_length=20,
		choices=TOURNAMENT_STATUS,
		default='REGISTERING'
	)

	@classmethod
	def create_tournament(cls, tournament_id: str, players: list):
		return cls.objects.create(
			tournament_id=tournament_id,
			players=players,
			rounds=[], 
			current_round=0
		)
	
	@classmethod
	def player_in_tournament(cls, username: str) -> bool:
		return cls.objects.filter(
			players__contains=[username],
			status__in=['REGISTERING', 'IN_PROGRESS']
		).exists()
	

	def generate_game_id(self) -> str:
		timestamp = int(time.time())
		token = secrets.token_hex(4)
		return f"tg:{timestamp}:{token}"


	def start_tournament(self):
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
		self.status = 'IN_PROGRESS'
		self.save()
		return True

	# @classmethod
	# def add_round_matches(cls, tournament_id: str, matches: list):
	# 	tournament = cls.objects.get(tournament_id=tournament_id)
	# 	tournament.rounds = tournament.rounds + [matches]
	# 	tournament.current_round += 1
	# 	tournament.save()


	# def start_tournament(self):
	# 	if self.status != 'REGISTERING' or len(self.players) != self.max_players:
	# 		return False
			
	# 	if self.max_players % 2 != 0:
	# 		return False
			
	# 	import random
	# 	players = self.players.copy()
	# 	random.shuffle(players)
		
	# 	matches = []
	# 	for i in range(0, len(players), 2):
	# 		matches.append({
	# 			'player1': players[i],
	# 			'player2': players[i + 1],
	# 			'winner': None,
	# 			'game_id': None,
	# 			'status': 'PENDING'
	# 		})
		
	# 	self.rounds = [matches]
	# 	self.status = 'IN_PROGRESS'
	# 	self.save()
	# 	return True