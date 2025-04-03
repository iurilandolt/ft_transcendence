from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods


@ensure_csrf_cookie
def index(request):
	if not request.session.session_key:
		request.session.save()
	return render(request, 'index.html')


def home_view(request):
		return render(request, 'views/home-view.html')


def nav_menu(request):
	return render(request, 'menus/nav-menu.html')


@require_http_methods(["GET"])
def login_menu(request):
	context = {
		'is_authenticated': request.user.is_authenticated,
		'username': request.user.username if request.user.is_authenticated else '',
		'profile_pic': request.user.profile_pic if request.user.is_authenticated else '/static/images/nologin-thumb.png',
	}
	if request.user.is_authenticated:
		context['friends'] = {
			'pending_received': request.user.pending_received_requests,
		}
	return render(request, 'menus/login-menu.html', context)


def pong_view(request):
	if request.user.is_authenticated:
		return render(request, 'views/pong-view.html')
	return HttpResponseForbidden('Not authenticated')


# def profile_view(request):
# 	if request.user.is_authenticated:
# 		return render(request, 'views/profile-view.html', {'user': request.user})
# 	return HttpResponseForbidden('Not authenticated')


def login_view(request):
	if request.user.is_authenticated:
		return redirect('home-view')
	return render(request, 'views/login-view.html')


def register_view(request):
	if request.user.is_authenticated:
		return redirect('home-view')
	return render(request, 'views/register-view.html')


def tournament_view(request):
	if request.user.is_authenticated:
		return render(request, 'views/tournament-view.html')
	return HttpResponseForbidden('Not authenticated')



