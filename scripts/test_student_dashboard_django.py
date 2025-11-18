import os
import sys

# Ensure project root is on sys.path so Django can import the project package
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
	sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xplorehub.settings')
import django
django.setup()
from django.test import Client

c = Client()
logged_in = c.login(username='student1', password='password')
print('logged_in', logged_in)
r = c.get('/student-dashboard/')
print('status', r.status_code)
# Print short part of the response to confirm render
print(r.content.decode('utf-8')[:1000])
