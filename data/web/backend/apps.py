from django.apps import AppConfig

from django.utils.translation import activate

class BackendConfig(AppConfig):
	default_auto_field = 'django.db.models.BigAutoField'
	name = 'backend'

	def ready(self):
		import backend.signals
		
		# from backend.models import Ladderboard
		# Ladderboard.initialize_all()

def custom_activate(request): 
	from .models import User
	user : User = User.from_jwt_request(request)
	if user:
		activate(user.language)
	else:
		activate(request.session.get('django_language', 'en'))