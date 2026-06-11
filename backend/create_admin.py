import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_core.settings.base')
import django
django.setup()
from django.contrib.auth.models import User

if not User.objects.filter(username='anna').exists():
    User.objects.create_superuser('anna', '', 'anna')
    print('Superuser created!')
else:
    User.objects.get(username='anna').set_password('anna')
    User.objects.get(username='anna').save()
    print('Password updated!')