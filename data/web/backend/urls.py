from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('home-view/', views.home_view, name='home-view'),
	path('profile-view/', views.profile_view, name='profile-view'),
	path('pong-view/', views.pong_view, name='pong-view'),
	path('login-view/', views.login_view, name='login-view'),
	path('register-view/', views.register_view, name='register-view'),
	path('tournament-view/', views.tournament_view, name='tournament-view'),
	
	path('tournament-view/create/', views.tournament_create, name='tournament-view'),
	path('tournament-view/join/', views.tournament_join, name='tournament-join'),
	path('tournament-view/list/', views.tournament_list, name='tournament-list'),
	path('tournament-view/leave/', views.tournament_leave, name='tournament-leave'),
]


