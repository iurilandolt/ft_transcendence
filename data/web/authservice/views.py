from django.shortcuts import redirect
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_backends
from backend.models import User
from datetime import datetime

from pong.models import OngoingGame
from tournaments.models import Tournament
from django_otp.plugins.otp_totp.models import TOTPDevice

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

from backend.forms import UserRegistrationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from io import BytesIO
from authservice.forms import CustomPasswordResetForm
import json, requests, qrcode, base64, logging


logger = logging.getLogger('pong')


@require_http_methods(["POST"])
def register_request(request):
    user = User.from_jwt_request(request)
    if user:
        return JsonResponse({'error': 'Already authenticated'}, status=403)
    data = json.loads(request.body)
    form = UserRegistrationForm(data)
    if form.is_valid():
        form.save()  # clean + password validation + password hashing = done
        return JsonResponse({'message': 'Registration successful'})
    return JsonResponse(form.errors, status=400)



@require_http_methods(["POST"])
def login_request(request):
	user : User = User.from_jwt_request(request)
	if user:
		return JsonResponse({'error': 'Already authenticated'}, status=403)
	data = json.loads(request.body)
	username = data.get('username')
	password = data.get('password')
	user = authenticate(request, username=username, password=password)
	if user is not None:
		#implement 2FA check here
		if user.two_factor_enable:
			return JsonResponse({
				'autenticated': '2fa enabled',
				'user': {
					'uuid': str(user.uuid),
					'username': str(user.username),
					'profile_pic': str(user.profile_pic),
				}}, status=201)
		# login(request, user)
		user.last_login = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		user.save()
		refresh : RefreshToken = RefreshToken.for_user(user)
		return JsonResponse({
			'message': 'Login successful',
			'tokens': {
				'access': str(refresh.access_token),
				'refresh': str(refresh),
			},
			'user': {
				'uuid': str(user.uuid),
				'username': str(user.username),
				'profile_pic': str(user.profile_pic),
			}
		})
	return JsonResponse({'error': 'Invalid credentials'}, status=401)


@api_view(['POST'])
def login_refresh_request(request):
	try:
		refresh_token = request.data.get('refresh')
		if not refresh_token:
			return JsonResponse({
				'success': False,
				'message': 'Refresh token required'
			}, status=400)

		refresh = RefreshToken(refresh_token)
		user_id = refresh['user_id']
		
		user = User.objects.get(id=user_id)
		if not user.is_active:
			refresh.blacklist()
			return JsonResponse({
				'success': False,
				'message': 'User account is inactive'
			}, status=401)
			
		return JsonResponse({
			'success': True,
			'access': str(refresh.access_token)
		})
	
	except Exception as e:
		logger.error(f"Refresh token error: {str(e)}")
		return JsonResponse({
			'success': False,
			'message': 'Invalid refresh token'
		}, status=401)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def logout_request(request):
	try:
		refresh_token = request.data.get('refresh_token')
		if refresh_token:
			token = RefreshToken(refresh_token)
			token.blacklist()
		return JsonResponse({'message': 'Logout successful'})
	except Exception as e:
		logger.error(f"Logout error: {str(e)}")
		return JsonResponse({'error': 'Invalid token'}, status=400)



@require_http_methods(["GET"])
def check_auth(request):
	user = User.from_jwt_request(request)
	if user:
		return JsonResponse({
			'isAuthenticated': True,
			'user': {
				'uuid': str(user.uuid),
				'username': str(user.username),
				'profile_pic': str(user.profile_pic),
			}
		})
	return JsonResponse({'isAuthenticated': False})



@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request):
	try:
		data = json.loads(request.body)
		user : User = request.user

		current_password = data.get('current_password')
		new_password = data.get('new_password')
		if not current_password or not new_password:
			return JsonResponse({'error': 'Both current and new passwords are required'}, status=400)

		if len(new_password) < 8:
					return JsonResponse({'error': 'New password must be at least 8 characters long'}, status=400)

		if not user.check_password(current_password):
			return JsonResponse({'error': 'Current password is incorrect'}, status=400)

		try:
			validate_password(new_password, user)
		except ValidationError as e:
			return JsonResponse({'error': e.messages[0]}, status=400)

		user.set_password(new_password)
		user.save()

		update_session_auth_hash(request, user)

		return JsonResponse({'success': True, 'message': 'Password changed successfully'})

	except json.JSONDecodeError:
		return JsonResponse({'error': 'Invalid JSON data'}, status=400)
	except Exception as e:
		logger.error(f"Error changing password: {str(e)}")
		return JsonResponse({'error': 'An error occurred while changing the password'}, status=500)



@require_http_methods(["GET"])
def get_host(request):
	host = settings.WEB_HOST
	return JsonResponse({
		'host': host,
	})


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_2fa(request):
    try:
        data = json.loads(request.body)
        two_factor_enable = data.get('two_factor_enable', False)

        # Update the user's two_factor_enable field
        request.user.two_factor_enable = two_factor_enable
        request.user.save()

        return JsonResponse({
            'success': True,
            'message': f"Two-factor authentication {'enabled' if two_factor_enable else 'disabled'}"
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': "Invalid request format"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_account(request):
	try:
		user : User = request.user
		data = json.loads(request.body)
		password = data.get('password')
		uuid = str(user.uuid)

		if  not user.is_42_user and (not password or not user.check_password(password)):
			raise ValueError('Password is incorrect')

		if Tournament.player_in_tournament(uuid) or OngoingGame.player_in_game(uuid):
			raise RuntimeError('User is in a game or tournament')

		refresh_token : RefreshToken = request.data.get('refresh_token')
		if refresh_token:
			token = RefreshToken(refresh_token)
			token.blacklist()

		returned = user.delete_account()
		if returned:			
			return JsonResponse({'success': True, 'message': 'Account deleted successfully'})
		
	except Exception as e:
		logger.error(f"Error deleting account: {str(e)}")
		return JsonResponse({'error': str(e)}, status=400)
	
	return JsonResponse({'error': 'Invalid request'}, status=400)
		
	

@require_http_methods(["POST"])
def login42(request):
	data = json.loads(request.body)
	code = data.get('code')
	if not code:
		logger.error('Authorization code not found in request')
		return JsonResponse({'error': 'Invalid request'}, status=400)
	host = settings.WEB_HOST
	logger.debug(f"i am here")
	token_url = 'https://api.intra.42.fr/oauth/token'
	redirect_uri = f'https://{host}/oauth/callback/'

	token_data = {
		'grant_type': 'authorization_code',
		'client_id': settings.SOCIALACCOUNT_PROVIDERS['42school']['APP']['client_id'],
		'client_secret': settings.SOCIALACCOUNT_PROVIDERS['42school']['APP']['secret'],
		'code': code,
		'redirect_uri': redirect_uri,
	}
	token_response = requests.post(token_url, data=token_data)
	token_json = token_response.json()
	access_token = token_json.get('access_token')

	if not access_token:
		logger.error('Access token not found in token response')
		return JsonResponse({'error': 'Invalid request'}, status=400)

	user_info_url = 'https://api.intra.42.fr/v2/me'
	headers = {'Authorization': f'Bearer {access_token}'}
	user_info_response = requests.get(user_info_url, headers=headers)
	user_info = user_info_response.json()

	username = user_info.get('login')
	email = user_info.get('email')
	user_id = user_info.get('id')
	profile_pic_url = user_info.get('image', {}).get('link')

	# Create user if not exists
	try:
		user = User.objects.get(username=username)
		if not user.is_42_user:
			# Handle username conflict by generating a new username
			for i in range(1, 10000):
				new_username = f'{username}_{i}'
				if not User.objects.filter(username=new_username).exists():
					username = new_username
					break

	except User.DoesNotExist:
		# If the user does not exist, create a new user
		user = User(username=username, email=email, id_42=user_id, is_42_user=True)
		user.set_unusable_password()
		user.profile_pic = profile_pic_url
		user.is_42_user = True
		user.save()

	# Get the authentication backends configured in Django settings
	backends = get_backends()
	user.backend = f'{backends[0].__module__}.{backends[0].__class__.__name__}'

	# login(request, user)
	refresh = RefreshToken.for_user(user)
	access_token = str(refresh.access_token)
	refresh_token = str(refresh)
	user.last_login = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	user.save()
	return JsonResponse({
			'message': 'Login successful',
			'tokens': {
				'access': str(refresh.access_token),
				'refresh': str(refresh_token),
			},
			'user': {
				'uuid': str(user.uuid),
				'username': str(user.username),
				'profile_pic': str(user.profile_pic),
			}
		})


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def twoFactor(request):
	
	user = User.from_jwt_request(request)
	if user.is_42_user:
		return JsonResponse({'error': '42 users cannot enable 2FA'}, status=403)
	
	if user.two_factor_enable:
		return JsonResponse({'error': '2FA is already enabled'}, status=403)
	
	device, created = TOTPDevice.objects.get_or_create(user=user, name='default')

	if created:
		device.save()

	# Generate otp uri
	issuer = 'transcendence'
	secret = base64.b32encode(bytes.fromhex(device.key)).decode('utf-8')
	algorithm = 'SHA1'
	digits = 6
	period = 30
	otp_uri = (
        f"otpauth://totp/{issuer}:{user.username}"
        f"?secret={secret}&issuer={issuer}&algorithm={algorithm}&digits={digits}&period={period}"
    )

	# Generate QR code
	qr = qrcode.make(otp_uri)
	buffer = BytesIO()
	qr.save(buffer, format='PNG')
	qr_image = buffer.getvalue()

	qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

	return JsonResponse({ 
		'success': True,
		'qr_image': qr_base64,
		'otp_uri': otp_uri,
	})


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def verify_2fa_enable(request):
	try:
		data = json.loads(request.body)
		opt_token = data.get('otp_token')

		if not opt_token:
			return JsonResponse({'error': 'OTP token is required'}, status=400)
		
		user = request.user

		if user.two_factor_enable:
			return JsonResponse({'error': '2FA is already enabled'}, status=403)

		device = TOTPDevice.objects.filter(user=user, name='default').first()
		if not device:
			return JsonResponse({'error': 'Device not found'}, status=404)
		
		if device.verify_token(opt_token):
			user.two_factor_enable = True
			user.save()
			return JsonResponse({'success': True, 'message': '2FA enabled successfully'})
		else:
			return JsonResponse({'error': 'Invalid OTP token'}, status=400)
		
	except json.JSONDecodeError:
		return JsonResponse({'error': 'Invalid JSON data'}, status=400)
	except Exception as e:
		logger.error(f"Error verifying OTP token: {str(e)}")
		return JsonResponse({'error': 'An error occurred while verifying the OTP token'}, status=500)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def disable_2fa(request):
	user = request.user
	if user.two_factor_enable:
		user.two_factor_enable = False
		device = TOTPDevice.objects.filter(user=user, name='default').first()
		if device:
			device.delete()
		else:
			return JsonResponse({'error': 'Device not found'}, status=404)
		user.save()
		return JsonResponse({'success': True, 'message': '2FA disabled successfully'})
	else:
		return JsonResponse({'error': '2FA is already disabled'}, status=400)


@require_http_methods(["POST"])
def verify_2fa_login(request):
	data = json.loads(request.body)
	opt_token = data.get('code')
	username = data.get('username')
	user = User.objects.filter(username=username).first()
	if not user:
		return JsonResponse({'error': 'User not found'}, status=404)

	if not opt_token:
		return JsonResponse({'error': 'OTP token is required'}, status=400)
	
	device = TOTPDevice.objects.filter(user=user, name='default').first()
	if not device:
		return JsonResponse({'error': 'Device not found'}, status=404)
	
	if device.verify_token(opt_token):
		user.backend = 'django.contrib.auth.backends.ModelBackend'
		# login(request, user)
		user.last_login = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		user.save()
		refresh : RefreshToken = RefreshToken.for_user(user)
		return JsonResponse({
			'message': 'Login successful',
			'tokens': {
				'access': str(refresh.access_token),
				'refresh': str(refresh),
			},
			'user': {
				'uuid': str(user.uuid),
				'username': str(user.username),
				'profile_pic': str(user.profile_pic),
			}
		})
	else:
		return JsonResponse({'error': 'Invalid OTP token'}, status=400)


@api_view(['POST'])
def password_reset(request):
	try:
		data = json.loads(request.body)
		email = data.get('email')

		form = CustomPasswordResetForm({'email': email})
		if form.is_valid():
			logger.debug(f"Sending password reset email to {email}")
			form.save(
				request=request,
				use_https=True,
				from_email=settings.DEFAULT_FROM_EMAIL,
				email_template_name='registration/password_reset_email.html',
				html_email_template_name='registration/password_reset_email.html',
			)
			return JsonResponse({'success': 'Password reset email sent'}, status=200)
		else:
			return JsonResponse({'error': form.errors.get('email', ['Invalid email address.'])[0]}, status=400)

	except Exception as e:
		logger.error(f"Error parsing JSON data: {str(e)}")
		return JsonResponse({'error': 'Invalid JSON data'}, status=400)


@api_view(['POST', 'GET'])
def password_reset_confirm(request, uidb64, token):
	if request.method == 'GET':
		# Validate the uidb64 and token
		try:
			uid = urlsafe_base64_decode(uidb64).decode()
			user = User.objects.get(pk=uid)
		except (TypeError, ValueError, OverflowError, User.DoesNotExist):
			return JsonResponse({'error': 'Invalid user'}, status=400)
		
		if not user.is_active:
			return JsonResponse({'error': 'User is inactive'}, status=400)
		
		if user.is_42_user:
			return JsonResponse({'error': '42 users cannot reset passwords'}, status=400)

		if not default_token_generator.check_token(user, token):
			return JsonResponse({'error': 'The password reset link has expired or is invalid.'}, status=400)

		return JsonResponse({'success': 'Token is valid'}, status=200)

	elif request.method == 'POST':
		try:
			data = json.loads(request.body)
			new_password1 = data.get('new_password1')
			new_password2 = data.get('new_password2')

			if new_password1 != new_password2:
				return JsonResponse({'error': 'Passwords do not match'}, status=400)

			try:
				uid = urlsafe_base64_decode(uidb64).decode()
				user = User.objects.get(pk=uid)
			except (TypeError, ValueError, OverflowError, User.DoesNotExist):
				return JsonResponse({'error': 'Invalid user'}, status=400)

			if not default_token_generator.check_token(user, token):
				return JsonResponse({'error': 'Invalid or expired token'}, status=400)

			try:
				validate_password(new_password1, user)
			except ValidationError as e:
				return JsonResponse({'error': e.messages[0]}, status=400)

			user.set_password(new_password1)
			user.save()
			return JsonResponse({'success': 'Password has been reset successfully'}, status=200)

		except json.JSONDecodeError:
			return JsonResponse({'error': 'Invalid JSON data'}, status=400)

	return JsonResponse({'error': 'Invalid request method'}, status=405)

def oauth_callback(request):
	logger.debug(f"OAuth callback request: {request}")
	if not request.GET.get('code'):
		return JsonResponse({'error': 'Invalid request'}, status=400)
	return HttpResponseRedirect(f'https://{settings.WEB_HOST}/#/login-fortytwo/?code={request.GET.get("code")}')