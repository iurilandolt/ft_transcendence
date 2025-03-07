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
					'game_url': f'wss/mpong/game/{ongoing_game}/',
					'player_id': self.player_id
				}
			}
			await self.accept()
			await self.send(json.dumps(reconnect_data))
			await self.close()
			return
		
		if await GameDB.is_duplicate_game_id(self.generate_game_id()):
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
			
			for i in range(len(players)):
				player = self.queued_players[players[i]]
				match_data = {
					'event': 'match_found',
					'state': {
						'game_id': game_id,
						'game_url': f'wss/mpong/game/{game_id}/',
						'player_id': players[i]  # Send the player ID specific to each consumer
					}
				}
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

class TournamentLobby(QuickLobby):

	def generate_game_id(self) -> str:
		return self.scope['url_route']['kwargs']['game_id']

	async def try_match_players(self):
		if len(self.queued_players) < 2:
			return
			
		game_id = self.generate_game_id()
		tournament_players = [player_id for player_id, ws in self.queued_players.items()
			if ws.scope['url_route']['kwargs']['game_id'] == game_id][:2]
		
		if len(tournament_players) >= 2:
			for player_id in tournament_players:
				player = self.queued_players[player_id]
				match_data = {
					'event': 'match_found',
					'state': {
						'game_id': game_id,
						'game_url': f'wss/mpong/game/{game_id}/',
						'player_id': player_id  # Send the player ID specific to each consumer
					}
				}
				await player.send(json.dumps(match_data))
				del self.queued_players[player_id]
				await player.close()