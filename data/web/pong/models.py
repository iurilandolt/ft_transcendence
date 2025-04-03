from django.db import models
from backend.models import User
from django.contrib.postgres.fields import ArrayField, HStoreField
from django.contrib.postgres.operations import HStoreExtension
import random, secrets, time



class Game(models.Model):
	game_id = models.CharField(max_length=100, unique=True)
	player_ids = HStoreField()
	player1_username = models.CharField(max_length=150)
	player1_sets = models.IntegerField(default=0)
	player2_username = models.CharField(max_length=150)
	player2_sets = models.IntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)

	@classmethod
	def find_by_id(cls, game_id: str):
		try:
			return cls.objects.get(game_id=game_id)
		except cls.DoesNotExist:
			return None

	@classmethod
	def map_players(cls, user):
		return {str(user.uuid): user.username}
	
	@classmethod
	def get_username_from_uuid(cls, uuid_str):
		try:
			user = User.objects.get(uuid=uuid_str)
			return user.username
		except User.DoesNotExist:
			return None

	class Meta:
		abstract = True

class OngoingGame(Game):
	@classmethod
	def create_game(cls, game_id, player1_id, player2_id=None):
		user1 = User.objects.get(uuid=player1_id)
		player_mapping = cls.map_players(user1)
		
		player2_username = None
		if player2_id:
			user2 = User.objects.get(uuid=player2_id)
			player_mapping.update(cls.map_players(user2))
			player2_username = user2.username
		
		return cls.objects.create(
			game_id=game_id,
			player_ids=player_mapping,
			player1_username=user1.username,
			player2_username=player2_username
		)

	@classmethod
	def player_in_game(cls, player_id):
		return cls.objects.filter(
			player_ids__has_key=player_id
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
	winner_id = models.CharField(max_length=150, null=True)
	completed_at = models.DateTimeField(auto_now_add=True)

	@classmethod
	def create_from_ongoing(cls, ongoing_game, winner: str):
		
		winner_id = next((uuid for uuid, username in ongoing_game.player_ids.items() 
					if username == winner), None)

		loser_id = next((uuid for uuid, username in ongoing_game.player_ids.items() 
					if uuid != winner_id), None)

		cls.update_user_rank(winner_id, loser_id)
		return cls.objects.create(
			game_id=ongoing_game.game_id,
			player_ids=ongoing_game.player_ids,
			player1_username=ongoing_game.player1_username,
			player2_username=ongoing_game.player2_username,
			player1_sets=ongoing_game.player1_sets,
			player2_sets=ongoing_game.player2_sets,
			winner_username=winner,
			winner_id=winner_id 
		)
	
	@classmethod
	def update_user_rank(cls, w_uuid, l_uuid):
		if w_uuid and l_uuid:
			try:
				winner = User.objects.get(uuid=w_uuid)
				winner.rank = winner.rank + 1
				winner.save()
				loser = User.objects.get(uuid=l_uuid)
				loser.rank = max(0, loser.rank - 1)
				loser.save()

			except User.DoesNotExist:
				pass
				
	@classmethod
	def is_duplicate_id(cls, game_id):
		return cls.objects.filter(game_id=game_id).exists()
	
