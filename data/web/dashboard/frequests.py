from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from backend.models import User
from .models import get_user
import json
import logging

logger = logging.getLogger('pong')

@login_required
@require_http_methods(["POST"])
def send_friend_request(request):
	if not request.user.is_authenticated:
		return HttpResponseForbidden('Not authenticated')
	
	data = json.loads(request.body)
	sender = request.user
	recipient = get_user(data.get('username'))
	if recipient is None:
		return JsonResponse({
			'status': 'error',
			'message': 'User not found'
		}, status=404)

	success, message = sender.send_friend_request(recipient.uuid)

	if success:
		return JsonResponse({
			'status': 'success',
			'message': message
		})
	else:
		return JsonResponse({
			'status': 'error',
			'message': message
		}, status=400)

@login_required
@require_http_methods(["POST"])
def cancel_friend_request(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden('Not authenticated')
    
    data = json.loads(request.body)
    sender = request.user
    recipient = get_user(data.get('username'))
    if recipient is None:
        return JsonResponse({
            'status': 'error',
            'message': 'User not found'
        }, status=404)

    success, message = sender.cancel_friend_request(recipient.uuid)

    if success:
        return JsonResponse({
            'status': 'success',
            'message': message
        })
    else:
        return JsonResponse({
            'status': 'error',
            'message': message
        }, status=400)


@login_required
@require_http_methods(["POST"])
def accept_friend_request(request):
	if not request.user.is_authenticated:
		return HttpResponseForbidden('Not authenticated')
	data = json.loads(request.body)
	recipient = request.user
	sender = get_user(data.get('username'))
	if sender is None:
		return JsonResponse({
			'status': 'error',
			'message': 'User not found'
		}, status=404)

	success, message = recipient.accept_friend_request(sender.uuid)

	if success:
		return JsonResponse({
			'status': 'success',
			'message': message
		})
	else:
		return JsonResponse({
			'status': 'error',
			'message': message
		}, status=400)


@login_required
@require_http_methods(["POST"])
def reject_friend_request(request):
	if not request.user.is_authenticated:
		return HttpResponseForbidden('Not authenticated')
	
	data = json.loads(request.body)
	recipient = request.user
	sender = get_user(data.get('username'))
	if sender is None:
		return JsonResponse({
			'status': 'error',
			'message': 'User not found'
		}, status=404)

	success, message = recipient.reject_friend_request(sender.uuid)

	if success:
		return JsonResponse({
			'status': 'success',
			'message': message
		})
	else:
		return JsonResponse({
			'status': 'error',
			'message': message
		}, status=400)


@login_required
@require_http_methods(["POST"])
def remove_friend(request):
	if not request.user.is_authenticated:
		return HttpResponseForbidden('Not authenticated')
	
	data = json.loads(request.body)
	user = request.user
	friend = get_user(data.get('username'))
	if friend is None:
		return JsonResponse({
			'status': 'error',
			'message': 'User not found'
		}, status=404)

	success, message = user.remove_friend(friend.uuid)

	if success:
		return JsonResponse({
			'status': 'success',
			'message': message
		})
	else:
		return JsonResponse({
			'status': 'error',
			'message': message
		}, status=400)