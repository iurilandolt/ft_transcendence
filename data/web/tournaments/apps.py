from django.apps import AppConfig
import sys, threading, asyncio, logging, os

logger = logging.getLogger('pong')
class TournamentsConfig(AppConfig):
	default_auto_field = 'django.db.models.BigAutoField'
	name = 'tournaments'

	def ready(self):
		if 'runserver' not in sys.argv:
			return
		
		if not os.environ.get('RUN_MAIN'):
			logger.debug(f"Skipping tournament manager in outer process {os.getpid()}")
			return
		logger.info(f"Starting tournament manager in main process {os.getpid()}")
		
		from .tournaments import TournamentManager
		def start_manager():
			logger.info(f"ready() method called in process {os.getpid()}")
			try:
				loop = asyncio.new_event_loop()
				asyncio.set_event_loop(loop)
				manager = TournamentManager()
				manager.start(loop)
				loop.run_forever()
			except Exception as e:
				logger.error(f"Error in tournament manager loop: {str(e)}")
			finally:
				loop.close()
				logger.info("Tournament manager loop closed")		
			
		
		thread = threading.Thread(target=start_manager, daemon=True)
		thread.start()