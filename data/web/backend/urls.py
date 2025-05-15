from django.urls import path, re_path

from . import views



urlpatterns = [
	path('', views.index, name='index'),
	path('not-found-view/', views.not_found_view, name='not-found-view'),
	path('home-view/', views.home_view, name='home-view'),
	path('pong-view/', views.pong_view, name='pong-view'),
	path('login-view/', views.login_view, name='login-view'),
	path('register-view/', views.register_view, name='register-view'),
	path('tournament-view/', views.tournament_view, name='tournament-view'),
	path('nav-menu/', views.nav_menu, name='nav-menu'),
	path('login-menu/', views.login_menu, name='login-menu'),
	path('two-factor-view/', views.twoFactor_view, name='twofactor-view'),
	path('pass-reset-view/', views.pass_reset_view, name='pass-reset-view'),
	path('pass-reset-confirm-view/', views.pass_reset_confirm_view, name='pass-reset-confirm-view'),

	path('ladderboard-view/', views.ladderboard_view, name='ladderboard-view'),
	path('ladderboard-view/<str:page>/', views.ladderboard_view, name='ladderboard-view-page'),

	path('language-menu/', views.language_menu, name='language-menu'),
]


