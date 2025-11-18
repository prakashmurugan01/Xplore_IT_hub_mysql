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
print('login teacher1 ->', c.login(username='teacher1', password='password'))
from portal.models import Profile, Course, StudyMaterial
teacher_profile = Profile.objects.filter(user__username='teacher1').first()
course = Course.objects.filter(teacher=teacher_profile).first()
print('teacher course ->', course)

# upload a tiny pdf
pdf = b"%PDF-1.4\n%test\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Count 0>>endobj\ntrailer<< /Root 1 0 R>>\n%%EOF"
up = SimpleUploadedFile('teacher_test.pdf', pdf, content_type='application/pdf')
resp = c.post(f'/course/{course.id}/materials/manage/', {'title':'Teacher PDF', 'description':'Uploaded by teacher test','file':up})
print('upload ->', resp.status_code)

# list materials page
r = c.get(f'/course/{course.id}/materials/manage/')
print('manage page ->', r.status_code)
print('contains Teacher PDF?', 'Teacher PDF' in r.content.decode('utf-8'))

# find the material and view it
mat = StudyMaterial.objects.filter(title='Teacher PDF', course=course).first()
print('mat id ->', mat.id if mat else None)
if mat:
    rv = c.get(f'/materials/view/{mat.id}/')
    print('view status ->', rv.status_code, rv.get('Content-Type'))
    rd = c.get(f'/materials/download/{mat.id}/')
    print('download status ->', rd.status_code, rd.get('Content-Type'))

    # delete it
    rd2 = c.post(f'/materials/delete/{mat.id}/')
    print('delete post ->', rd2.status_code)
    r2 = c.get(f'/course/{course.id}/materials/manage/')
    print('contains after delete?', 'Teacher PDF' in r2.content.decode('utf-8'))

print('done')
