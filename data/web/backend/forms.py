from django import forms
from .models import User
from django.core.exceptions import ValidationError
import re

from django.contrib.auth.password_validation import validate_password

class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password',
        ]
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')

        # Check if empty
        if not username or username.strip() == '':
            raise ValidationError("Username cannot be empty.")

        # Check minimum length
        if len(username.strip()) < 3:
            raise ValidationError("Username must be at least 3 characters long.")

        # Check maximum length
        if len(username.strip()) > 20:
            raise ValidationError("Username cannot exceed 20 characters.")

        # Check for valid characters (letters, numbers, underscores, hyphens only)
        if not re.match(r'^[a-zA-Z0-9-]+$', username):
            raise ValidationError("Username can only contain letters, numbers, underscores and hyphens.")

        # Check if username starts with a letter
        if not username[0].isalpha():
            raise ValidationError("Username must start with a letter.")

        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        validate_password(password, self.instance)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class UserProfileUpdateForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['username', 'email']

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super().__init__(*args, **kwargs)

	def clean_username(self):
		username = self.cleaned_data.get('username')

		# Skip validation if username hasn't changed
		if self.user and username == self.user.username:
			return username

		# Check if empty
		if not username or username.strip() == '':
			raise ValidationError("Username cannot be empty.")

		# Check minimum length
		if len(username.strip()) < 3:
			raise ValidationError("Username must be at least 3 characters long.")

		# Check maximum length
		if len(username.strip()) > 20:
			raise ValidationError("Username cannot exceed 20 characters.")

		# Check for valid characters (letters, numbers, underscores, hyphens only)
		if not re.match(r'^[a-zA-Z0-9_-]+$', username):
			raise ValidationError("Username can only contain letters, numbers, underscores and hyphens.")

		# Check if username starts with a letter
		if not username[0].isalpha():
			raise ValidationError("Username must start with a letter.")

		# Check if username is already taken
		if User.objects.filter(username=username).exists():
			raise ValidationError("Username already taken.")

		return username



	def clean_email(self):
		email = self.cleaned_data.get('email')

		# Skip validation if email hasn't changed
		if self.user and email == self.user.email:
			return email

		# Check if email is already registered
		if User.objects.filter(email=email).exists():
			raise ValidationError("Email already registered.")

		return email
