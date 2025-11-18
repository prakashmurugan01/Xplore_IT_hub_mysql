import os, sys, pathlib
PROJECT_ROOT = str(pathlib.Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xplorehub.settings')
import django
django.setup()
from django.test import Client

c = Client()
print('login student1 ->', c.login(username='student1', password='password'))
r = c.get('/notifications/')
print('/notifications/ ->', r.status_code)
print('snippet:', r.content.decode('utf-8')[:400])
