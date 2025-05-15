from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import get_user
import json
import logging

logger = logging.getLogger('pong')

@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
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



@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
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



@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
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



@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
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



@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
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