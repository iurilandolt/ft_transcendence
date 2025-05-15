from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template import loader
from backend.models import User
from django import forms
import logging

logger = logging.getLogger('pong')

class CustomPasswordResetForm(PasswordResetForm):
	def save(self, *args, **kwargs):
		domain = kwargs.get('domain_override') or settings.WEB_HOST or 'localhost:4443'
		protocol = 'https'

		users = list(self.get_users(self.cleaned_data['email']))

		for user in users:
			uidb64 = uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
			token = default_token_generator.make_token(user)

			context = {
				'email': self.cleaned_data['email'],
				'domain': domain,
				'site_name': domain,
				'uid': uidb64,
				'user': user,
				'token': token,
				'protocol': protocol,
			}

			self.send_mail(
				kwargs.get('subject_template_name'),
				kwargs.get('email_template_name'),
				context,
				kwargs.get('from_email'),
				self.cleaned_data['email'],
				kwargs.get('html_email_template_name'),
			)

	def send_mail(self, subject_template_name, email_template_name,
				context, from_email, to_email, html_email_template_name=None):

		logger.debug(f"subject_template_name = {subject_template_name} "
					f"email_template_name = {email_template_name} "
					f"context = {context} "
					f"from_email = {from_email} "
					f"to_email = {to_email} "
					f"html_email_template_name = {html_email_template_name} ")
		if context is None:
			context = {}

		domain = settings.WEB_HOST or 'localhost:4443'
		context.update({
			'domain': domain,
			'site_name': domain,
			'protocol': 'https',
		})

		if to_email is None:
			to_email = self.cleaned_data.get('email')

		try:
			body = loader.render_to_string(email_template_name, context)
			email_message = EmailMultiAlternatives(
				subject="Password reset for your Transcendence account",
				body=body,
				from_email=from_email,
				to=[to_email]
			)
			if html_email_template_name is not None:
				html_email = loader.render_to_string(html_email_template_name, context)
				email_message.attach_alternative(html_email, 'text/html')

			email_message.send()
		except Exception as e:
			logger.error(f"Error sending email: {str(e)}")

	def clean_email(self):
		email = self.cleaned_data.get('email')
		try:
			user = User.objects.get(email=email)
			if user.is_42_user:
				raise forms.ValidationError(
					("42 School accounts cannot reset passwords. Please use 42 OAuth login."),
					code="42_user_no_reset"
				)
		except User.DoesNotExist:
			pass
		return email