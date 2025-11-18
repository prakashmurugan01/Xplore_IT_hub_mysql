import os, sys, pathlib

PROJECT_ROOT = str(pathlib.Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xplorehub.settings')
import django
django.setup()
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile

c = Client()

# Login as superadmin and upload a small PDF
print('login superadmin ->', c.login(username='superadmin', password='password'))
# create a tiny PDF binary
pdf_bytes = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 44 >>\nstream\nBT /F1 24 Tf 72 72 Td (Hello) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000115 00000 n \n0000000210 00000 n \ntrailer\n<< /Root 1 0 R >>\nstartxref\n310\n%%EOF\n"
up = SimpleUploadedFile('test_upload.pdf', pdf_bytes, content_type='application/pdf')
# Choose an existing course (TEST101 or first course)
from portal.models import Course, Enrollment, Profile
# Find a course the seeded student is enrolled in (via Enrollment for user student1)
student_profile = Profile.objects.filter(user__username='student1').first()
enr = None
if student_profile:
    enr = Enrollment.objects.filter(student=student_profile).first()

if enr:
    course = enr.course
else:
    # Fall back to any course, and ensure student1 is enrolled so they can view materials
    course = Course.objects.first()
    if student_profile and course:
        Enrollment.objects.get_or_create(student=student_profile, course=course)
print('using course:', course)
resp = c.post(f'/course/{course.id}/materials/admin-upload/', {'title': 'Admin PDF', 'description': 'Uploaded by admin via test', 'file': up})
print('upload resp ->', resp.status_code)

# Now log in as student and fetch student dashboard
c.logout()
print('login student ->', c.login(username='student1', password='password'))
resp = c.get('/student-dashboard/')
print('student dashboard ->', resp.status_code)
text = resp.content.decode('utf-8')
print('contains Admin PDF?', 'Admin PDF' in text)

# Try to GET the view URL for the material we just created
from portal.models import StudyMaterial
m = StudyMaterial.objects.filter(title='Admin PDF').order_by('-uploaded_at').first()
print('material id ->', m.id if m else None)
if m:
    r2 = c.get(f'/materials/view/{m.id}/')
    print('view material status ->', r2.status_code, r2.get('Content-Type'))
    # check bytes start with %PDF
    snippet = r2.content[:8]
    print('view snippet:', snippet)

print('done')
