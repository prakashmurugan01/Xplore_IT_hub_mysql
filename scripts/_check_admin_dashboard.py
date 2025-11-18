import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','xplorehub.settings')
import django
django.setup()
from django.contrib.auth.models import User
from django.test import Client
u=User.objects.filter(username='superadmin').first()
if not u:
    u=User.objects.create_user('superadmin','admin@example.com','password')
    u.profile.role='superadmin'
    u.profile.save()

c=Client()
logged = c.login(username='superadmin',password='password')
print('logged', logged)
r=c.get('/admin-dashboard/')
print('STATUS',r.status_code)
open('last_admin_dashboard.html','wb').write(r.content)
print('wrote last_admin_dashboard.html')
