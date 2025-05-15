from .models import Tournament
from pong.models import OngoingGame ,CompletedGame
from django.apps import apps
from django.utils import timezone
from channels.db import database_sync_to_async
import asyncio, time, logging

logger = logging.getLogger('pong')

class TournamentManager:
	running = False
	task = None


	def start(self, loop):
		if not self.running:
			self.running = True
			self.loop = loop
			self.loop.create_task(self.poll_tournaments())
			logger.info('Tournament manager started')


	def stop(self):
		if self.running:
			self.running = False
			logger.info('Tournament manager stopped')


	async def poll_tournaments(self):
		while self.running:
			try:
				Tournament = apps.get_model('tournaments', 'Tournament')
				tournaments = await self.get_active_tournaments()
				for tournament in tournaments:
					await self.process_tournament(tournament)
			except Exception as e:
				logger.error(f'Error processing tournaments: {str(e)}')
			
			await asyncio.sleep(1) # should be 1 :)


	async def process_tournament(self, tournament : Tournament):
		if not tournament.rounds:
			return
		
		timed_out = await self.round_timeout(tournament)
		if timed_out:
			return

		current_round = tournament.rounds[tournament.current_round]
		for match in current_round:
			completed_game = await self.get_completed_game(match['game_id'])
			if completed_game:
				await self.complete_match(tournament, completed_game)
		#self.debug_tournament_rounds(tournament)


	@database_sync_to_async
	def complete_match(self, tournament : Tournament, completed_game: CompletedGame) -> bool:
		if tournament.status != 'IN_PROGRESS':
			return False

		current_round = tournament.rounds[tournament.current_round]
		for match in current_round:
			# tournament.create_next_round()
			if match['game_id'] == completed_game.game_id and match['status'] == 'PENDING':
				match['status'] = 'COMPLETED'
				match['winner'] = completed_game.winner_username
				tournament.save()
				tournament.create_next_round()
				return True	
		return False


	@database_sync_to_async
	def get_active_tournaments(self):
		return list(Tournament.objects.filter(status='IN_PROGRESS'))
	
	@database_sync_to_async
	def get_completed_game(self, game_id: str):
		return CompletedGame.find_by_id(game_id)

	@database_sync_to_async
	def round_timeout(self, tournament: Tournament) -> bool:
		if tournament.status != 'IN_PROGRESS' or not tournament.rounds:
			return False
			
		current_time = timezone.now()
		round_time = tournament.current_round_created_at
		time_diff = (current_time - round_time).total_seconds()
		
		if time_diff < 120:
			return False
		
		current_round = tournament.rounds[tournament.current_round]
		
		for match in current_round:
			if match['status'] == 'COMPLETED':
				continue
			game_id = match['game_id']
			ongoing_game = OngoingGame.objects.filter(game_id=game_id).exists()
			completed_game = CompletedGame.find_by_id(game_id)
			
			if not ongoing_game and not completed_game:
				logger.info(f"Tournament {tournament.tournament_id} timed out - match {game_id} never started")
				tournament.delete()
				return True
			
		return False


	# def debug_tournament_rounds(self, tournament):
	# 	logger.info(f'Processing tournament {tournament.tournament_id}')
	# 	logger.info(f"""
	# 		=========== Tournament Details ============
	# 		Tournament ID: {tournament.tournament_id}
	# 		Status: {tournament.status}
	# 		Players: {tournament.players}
	# 		Current Round: {tournament.current_round}
	# 		Max Players: {tournament.max_players}
	# 		Winner: {tournament.winner or 'None yet'}
	# 		Created: {tournament.created_at}
	# 		Updated: {tournament.updated_at}
	# 		=========================================""")

	# 	if tournament.rounds and tournament.current_round < len(tournament.rounds):
	# 		current_round = tournament.rounds[tournament.current_round]
	# 		logger.info(f"""
	# 		---------- Current Round Matches ----------
	# 		Round: {tournament.current_round + 1}
	# 		Matches:""")
			
	# 		for i, match in enumerate(current_round):
	# 			logger.info(f"""
	# 			Match {i+1}:
	# 			- Player 1: {match.get('player1', 'N/A')}
	# 			- Player 2: {match.get('player2', 'N/A')}
	# 			- Status: {match.get('status', 'N/A')}
	# 			- Winner: {match.get('winner', 'None yet')}
	# 			- Game ID: {match.get('game_id', 'N/A')}
	# 				""")



			
