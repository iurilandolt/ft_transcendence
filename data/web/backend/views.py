from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import ensure_csrf_cookie
import json


@ensure_csrf_cookie
def index(request):
	if not request.session.session_key:
		request.session.save()
	return render(request, 'index.html')


def home_view(request):
		return render(request, 'views/home-view.html')


def pong_view(request):
	if request.user.is_authenticated:
		return render(request, 'views/pong-view.html')
	return HttpResponseForbidden('Not authenticated')


def profile_view(request):
	if request.user.is_authenticated:
		return render(request, 'views/profile-view.html')
	return HttpResponseForbidden('Not authenticated')


def login_view(request):
	if request.user.is_authenticated:
		return redirect('home-view')
	return render(request, 'views/login-view.html')


def register_view(request):
	if request.user.is_authenticated:
		return redirect('home-view')
	return render(request, 'views/register-view.html')

