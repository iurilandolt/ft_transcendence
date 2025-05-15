from django.urls import path
from . import views

urlpatterns = [
	path('tournament-view/create/', views.tournament_create, name='tournament-view'),
	path('tournament-view/join/', views.tournament_join, name='tournament-join'),
	path('tournament-view/leave/', views.tournament_leave, name='tournament-leave'),
]