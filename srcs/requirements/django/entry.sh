#!/bin/bash
cd /ft_transcendence

python manage.py makemigrations backend pong authservice

python manage.py migrate

# should only run once
DJANGO_SUPERUSER_PASSWORD="$(cat /run/secrets/web_adm_psw)" python manage.py createsuperuser \
	--noinput \
	--username "$(cat /run/secrets/web_adm)" \
	--email "$(cat /run/secrets/web_adm)"@transcendence.com


python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="Banana").exists():
    User.objects.create_user(
        username="Banana",
        email="banana_null@noway.net",
        password="12345"
    )
EOF

python manage.py runserver 0.0.0.0:8080
