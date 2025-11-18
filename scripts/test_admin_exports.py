import os
import sys
import pathlib

PROJECT_ROOT = str(pathlib.Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xplorehub.settings')
import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User

client = Client()

print('Logging in superadmin')
logged = client.login(username='superadmin', password='password')
print('logged in:', logged)

resp = client.get('/superadmin/export-users/')
print('GET /admin/export-users/ ->', resp.status_code, resp.get('Content-Type'))
if resp.status_code == 200 and resp.get('Content-Type') == 'application/pdf':
    out = os.path.join(PROJECT_ROOT, 'scripts', 'recent_users_test.pdf')
    with open(out, 'wb') as f:
        f.write(resp.content)
    print('Saved recent users PDF to', out)
else:
    print('Response length', len(resp.content))

# pick a recent user id
u = User.objects.order_by('-date_joined').first()
if u:
    uid = u.id
    print('Testing download for user id', uid)
    resp2 = client.get(f'/superadmin/download-report/{uid}/')
    print('GET /admin/download-report/%s ->' % uid, resp2.status_code, resp2.get('Content-Type'))
    if resp2.status_code == 200 and resp2.get('Content-Type') == 'application/pdf':
        out2 = os.path.join(PROJECT_ROOT, 'scripts', f'report_{u.username}.pdf')
        with open(out2, 'wb') as f:
            f.write(resp2.content)
        print('Saved user report to', out2)
    else:
        print('User report response length', len(resp2.content))
else:
    print('No users found in DB')
