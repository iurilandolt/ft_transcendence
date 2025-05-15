from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseForbidden
from .models import User, Ladderboard
from .apps import custom_activate
from pong.models import CompletedGame
from tournaments.models import Tournament
from tournaments.views import get_tournament_list, get_user_tournament_history

from rest_framework.decorators import api_view, authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication

import logging

logger = logging.getLogger('pong')


@ensure_csrf_cookie
@require_http_methods(["GET"])
def index(request):
	if not request.session.session_key:
		request.session.save()
	return render(request, 'index.html')


@require_http_methods(["GET"])
def home_view(request):
	custom_activate(request)    
	context = {
		'stats': {
			"players" : User.objects.count(),
			"games" : CompletedGame.objects.count(),
			"champions" : Tournament.objects.filter(status='COMPLETED').count(),
		}
	}
	return render(request, 'views/home-view.html', context)

@require_http_methods(["GET"])
def not_found_view(request):
	return render(request, 'views/not-found-view.html')

 
@require_http_methods(["GET"])
def nav_menu(request):
	custom_activate(request)
	return render(request, 'menus/nav-menu.html')

 
@api_view(['GET'])
@authentication_classes([]) 
def login_menu(request):
    custom_activate(request)
    
    context = {
        'is_authenticated': False,
        'username': '',
        'profile_pic': '/static/images/nologin-thumb.png',
    }

    user = User.from_jwt_request(request)
    if user:
        context.update({
            'is_authenticated': True,
            'username': user.username,
            'profile_pic': str(user.profile_pic),
            'friends': {
                'pending_received': user.pending_received_requests,
            }
        })
    
    return render(request, 'menus/login-menu.html', context)

 
@api_view(['GET'])
@authentication_classes([]) 
def login_view(request):
	custom_activate(request)
	user : User = User.from_jwt_request(request)
	if not user:
		return render(request, 'views/login-view.html')
	return redirect('home-view')


@api_view(['GET'])
@authentication_classes([]) 
def register_view(request):
	custom_activate(request)
	user : User = User.from_jwt_request(request)
	if not user:
		return render(request, 'views/register-view.html')
	return redirect('home-view')

 
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def pong_view(request):
	custom_activate(request)
	user : User = User.from_jwt_request(request)
	if not user:
		return HttpResponseForbidden()
	return render(request, 'views/pong-view.html')


@api_view(['GET'])
@authentication_classes([JWTAuthentication]) 
def tournament_view(request):
	custom_activate(request)
	user : User = User.from_jwt_request(request)
	if not user:
		return HttpResponseForbidden()
	context = {
		**get_tournament_list(user),
		'tournament_history': get_user_tournament_history(user)
	}
	return render(request, 'views/tournament-view.html', context)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def ladderboard_view(request, page=None):
	custom_activate(request)
	user : User = User.from_jwt_request(request)
	if not user:
		return HttpResponseForbidden()

	custom_activate(request)
	users_per_page = 5
	total_users = Ladderboard.objects.count()
	total_pages = max(1, (total_users + users_per_page - 1) // users_per_page)

	try:
		page_num = int(page) if page is not None else 1
		if page_num < 1 or page_num > total_pages:
			page_num = 1
	except (ValueError, TypeError):
		page_num = 1

	start = (page_num - 1) * users_per_page
	leaderboard = Ladderboard.get_leaderboard(start, users_per_page)
	
	context = {
		'leaderboard': leaderboard,
		'current_page': page_num,
		'total_pages': range(1, total_pages + 1),
		'start_index': (page_num - 1) * users_per_page, 
	}
	
	return render(request, 'views/ladderboard-view.html', context)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def twoFactor_view(request):
    custom_activate(request)
    user = User.from_jwt_request(request)
    if not user or user.is_42_user or user.two_factor_enable:
        return redirect('home-view')        
    return render(request, 'views/twoFactor-view.html')


@require_http_methods(["GET"])
def language_menu(request):
	custom_activate(request)
	return render(request, 'menus/language-menu.html')

def pass_reset_view(request):
	custom_activate(request)
	if request.user.is_authenticated:
		return redirect('home-view')
	return render(request, 'registration/password-reset-view.html')

def pass_reset_confirm_view(request):
	custom_activate(request)
	if request.user.is_authenticated:
		return redirect('home-view')
	return render(request, 'registration/password-reset-confirm-view.html')

