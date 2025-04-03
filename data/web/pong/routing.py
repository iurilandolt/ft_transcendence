from django.urls import path
from .consumers import SinglePongConsumer, MultiPongConsumer, AIConsumer
from .lobby import QuickLobby, TournamentLobby

pong_websocket_urlpatterns = [
    path('wss/spong/', SinglePongConsumer.as_asgi()),
    path('wss/mpong/', QuickLobby.as_asgi()),
	path('wss/mpong/tournament/<str:game_id>/', TournamentLobby.as_asgi()),
	path('wss/mpong/game/<str:game_id>/', MultiPongConsumer.as_asgi()),
	path('wss/aipong/', AIConsumer.as_asgi()),
]