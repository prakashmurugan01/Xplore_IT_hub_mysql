import os
import sys
import pathlib

# Ensure project root on sys.path
PROJECT_ROOT = str(pathlib.Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xplorehub.settings')
import django
django.setup()

from django.test import Client
from django.conf import settings

client = Client()

def test_student_prediction():
    print('=== Testing student prediction ===')
    logged_in = client.login(username='student1', password='password')
    print('login student1:', logged_in)
    resp = client.get('/student/prediction/')
    print('GET /student/prediction/ ->', resp.status_code)
    if resp.status_code == 200:
        # Print a small snippet of the rendered page
        text = resp.content.decode('utf-8', errors='ignore')
        print('content snippet:', text[:400])
    else:
        print('response content:', resp.content[:400])
    client.logout()


def test_student_report_download():
    print('\n=== Testing student report download ===')
    logged_in = client.login(username='student1', password='password')
    print('login student1:', logged_in)
    resp = client.get('/student/download-report/')
    print('GET /student/download-report/ ->', resp.status_code, resp.get('Content-Type'))
    if resp.status_code == 200 and resp.get('Content-Type') == 'application/pdf':
        out_path = os.path.join(PROJECT_ROOT, 'scripts', 'student_report_test.pdf')
        with open(out_path, 'wb') as f:
            f.write(resp.content)
        print('Saved PDF to', out_path)
    else:
        # Print error message or HTML
        try:
            print('response text snippet:', resp.content.decode('utf-8')[:400])
        except Exception:
            print('binary response, length', len(resp.content))
    client.logout()


def test_admin_ai_insights():
    print('\n=== Testing admin AI insights ===')
    logged_in = client.login(username='superadmin', password='password')
    print('login superadmin:', logged_in)
    resp = client.get('/superadmin/ai-insights/')
    print('GET /superadmin/ai-insights/ ->', resp.status_code)
    if resp.status_code == 200:
        print('content snippet:', resp.content.decode('utf-8')[:400])
    else:
        print('resp content:', resp.content[:400])
    client.logout()

if __name__ == '__main__':
    test_student_prediction()
    test_student_report_download()
    test_admin_ai_insights()
