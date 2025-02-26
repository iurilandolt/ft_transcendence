from channels.generic.websocket import AsyncWebsocketConsumer
from .db_api import GameDB
import json, time, secrets, logging

logger = logging.getLogger('pong')
class QuickLobby(AsyncWebsocketConsumer):
	queued_players = {}

	def generate_game_id(self) -> str:
		timestamp = int(time.time())
		token = secrets.token_hex(4)
		return f"qg:{timestamp}:{token}"


	def get_username(self):
		return self.scope["user"].username if self.scope["user"].is_authenticated else None


	async def connect(self):
		if not self.scope["user"].is_authenticated:
			await self.close()
			return
		self.player_id = self.get_username()

		if ongoing_game := await GameDB.player_in_game(self.player_id):
			
			reconnect_data = {
				'event': 'match_found',
				'state': {
					# 'game_id': ongoing_game,
					'game_url': f'wss/mpong/game/{ongoing_game}/',
				}
			}
			await self.accept()
			await self.send(json.dumps(reconnect_data))
			await self.close()
			return

		await self.accept()
		
		self.queued_players[self.player_id] = self
		await self.broadcast_player_count()
		await self.try_match_players()


	async def disconnect(self, close_code):
		if hasattr(self, 'player_id') and self.player_id in self.queued_players:
			del self.queued_players[self.player_id]
			await self.broadcast_player_count()


	async def receive(self, text_data):
		data = json.loads(text_data)
		if 'action' not in data:
			return


	async def try_match_players(self):
		if len(self.queued_players) >= 2:
			players = list(self.queued_players.keys())[:2]
			game_id = f"{self.generate_game_id()}"
			
			match_data = {
				'event': 'match_found',
				'state': {
					'game_id': game_id,
					'game_url': f'wss/mpong/game/{game_id}/',
				}
			}
			
			for i in range(len(players)):
				player = self.queued_players[players[i]]
				await player.send(json.dumps(match_data))
				del self.queued_players[players[i]]
				await player.close()


	async def broadcast_player_count(self):
		for player in self.queued_players.values():
			await player.send(json.dumps({
				'event': 'player_count',
				'state': {
					'player_count': len(self.queued_players)
				}
			}))

# class Tournament:
# 	def __init__(self, tournament_id: str, players: list):
# 		self.tournament_id = tournament_id
# 		self.players = players
# 		self.round = 0
# 		self.matches = {}


# 	def generate_game_id(self) -> str:
# 		timestamp = int(time.time())
# 		token = secrets.token_hex(4)
# 		return f"tg:{timestamp}:{token}"


# 	async def start(self):
# 		await TournamentDB.create_tournament(self.tournament_id, self.players)
# 		await self.create_round_matches()
# 		await TournamentDB.add_round_matches(self.tournament_id, self.matches[self.round])


# 	async def create_round_matches(self):
# 		self.round += 1
# 		for i in range(0, len(self.players), 2):

# 			if i + 1 >= len(self.players):
# 				break
			
# 			match = {
# 				'game_id': self.generate_game_id(),
# 				'player1': self.players[i],
# 				'player2': self.players[i + 1],
# 				'winner': None
# 			}
# 			self.matches[self.round].append(match)
	



# class TournamentLobby(AsyncWebsocketConsumer):
# 	queued_players = {}
# 	active_tournaments = {}


# 	def generate_tournament_id(self) -> str:
# 		timestamp = int(time.time())
# 		token = secrets.token_hex(4)
# 		return f"t:{timestamp}:{token}"
	

# 	def get_username(self):
# 		return self.scope["user"].username if self.scope["user"].is_authenticated else None
	

# 	async def connect(self):
# 		if not self.scope["user"].is_authenticated:
# 			await self.close()
# 			return
# 		self.player_id = self.get_username()
# 		await self.accept()
# 		self.queued_players[self.player_id] = self
# 		self.broadcast_player_count()
# 		self.try_create_tournament()


# 	async def disconnect(self, close_code):
# 		if hasattr(self, 'player_id') and self.player_id in self.queued_players:
# 			del self.queued_players[self.player_id]


# 	async def try_create_tournament(self):
# 		if len(self.queued_players) >= 6:
# 			players = list(self.queued_players.keys())[:6]
# 			tournament_id = f"{self.generate_tournament_id()}"
			
# 			tournament_data = {
# 				'event': 'tournament_found',
# 				'state': {
# 					'tournament_id': tournament_id,
# 				}
# 			}
			
# 			for i in range(len(players)):
# 				player = self.queued_players[players[i]]
# 				await player.send(json.dumps(tournament_data))
# 				del self.queued_players[players[i]]
# 				await player.close()


# 	async def broadcast_player_count(self):
# 		for player in self.queued_players.values():
# 			await player.send(json.dumps({
# 				'event': 'player_count',
# 				'state': {
# 					'player_count': len(self.queued_players)
# 				}
# 			}))