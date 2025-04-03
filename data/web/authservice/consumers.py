from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from backend.models import User
import json, logging, time

logger = logging.getLogger('pong')

class LoginMenuConsumer(AsyncJsonWebsocketConsumer):
	active_users = []
	instances = []

	async def connect(self):
		if not self.scope["user"].is_authenticated:
			await self.close()
			return
		
		self.user : User = self.scope["user"]
		logger.debug(f"Connecting {self.user}")
		self.last_ping = None

		if self.user in self.active_users:
			await self.close()
			return
				
		await self.accept()


	async def receive(self, text_data):
		data = json.loads(text_data)
		if 'action' not in data:
			return
		
		match data['action']:
			case 'connect':
				if self.user not in self.active_users:
					self.active_users.append(self.user)
					self.instances.append(self)
					self.user.status = True
					await database_sync_to_async(self.user.save)()
					self.last_ping = time.time()
					await self.broadcast({'event': 'pong',})
			case 'ping':
				self.last_ping = time.time()
				await self.broadcast({'event': 'pong',})
				

	async def disconnect(self, close_code):
		if not self.scope["user"].is_authenticated:
			return

		if self.user in self.active_users:
			self.active_users.remove(self.user)

			# if the user model was updated since this consumer was created, the user object in this scope is outdated
			# saving it would overwrite the database with the old user objects data
			updated_user = await database_sync_to_async(User.objects.get)(uuid=self.user.uuid)

			updated_user.status = False
			await database_sync_to_async(updated_user.save)()

		if self in self.instances:
			self.instances.remove(self)

		
	async def broadcast(self, message):
		await self.send(json.dumps(message))

	async def broadcast_notification(self):
		await self.broadcast({'event': 'notification',})


