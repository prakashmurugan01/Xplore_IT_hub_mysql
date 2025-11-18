from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from portal.models import Profile, Course, StudyMaterial
from django.core.files.base import ContentFile


class Command(BaseCommand):
    help = 'Create a sample StudyMaterial for TEST101 course'

    def handle(self, *args, **options):
        teacher = User.objects.filter(username='teacher1').first()
        if not teacher:
            self.stdout.write(self.style.ERROR('teacher1 not found; run seed_demo_data first'))
            return

        course = Course.objects.filter(code='TEST101').first()
        if not course:
            self.stdout.write(self.style.ERROR('Course TEST101 not found; run seed_demo_data first'))
            return

        # Avoid duplicating the same material
        if StudyMaterial.objects.filter(course=course, title='Example Material').exists():
            self.stdout.write(self.style.WARNING('Example Material already exists'))
            return

        content = ContentFile(b'Example study material content', name='example_material.txt')
        sm = StudyMaterial.objects.create(course=course, uploaded_by=teacher.profile, title='Example Material', description='A small sample file', file=content)
        self.stdout.write(self.style.SUCCESS(f'Created StudyMaterial id={sm.id} file={sm.file.url}'))
