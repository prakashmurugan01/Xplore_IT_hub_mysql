from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Profile


class StudentCRUDBasicTests(TestCase):
    def setUp(self):
        # create superadmin user
        self.admin_user = User.objects.create_user(username='superadmin', password='password')
        self.admin_user.save()
        # ensure profile exists and role set
        p = self.admin_user.profile
        p.role = 'superadmin'
        p.save()

        self.client = Client()
        self.client.login(username='superadmin', password='password')

    def test_create_edit_delete_student(self):
        # Create student
        resp = self.client.post('/superadmin/students/add/', {
            'username': 'teststudent',
            'password': 'pass1234',
            'first_name': 'Test',
            'last_name': 'Student',
            'email': 'teststudent@example.com',
            'student_class': 'Class 10',
            'roll_number': '42',
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(User.objects.filter(username='teststudent').exists())
        profile = Profile.objects.get(user__username='teststudent')
        self.assertEqual(profile.student_class, 'Class 10')

        # Edit student
        edit_url = f'/superadmin/students/{profile.id}/edit/'
        resp = self.client.post(edit_url, {
            'username': 'teststudent',
            'password': '',
            'first_name': 'TestEdited',
            'last_name': 'Student',
            'email': 'edited@example.com',
            'student_class': 'Class 11',
            'roll_number': '99',
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        profile.refresh_from_db()
        self.assertEqual(profile.student_class, 'Class 11')
        self.assertEqual(profile.roll_number, '99')
        self.assertEqual(profile.user.first_name, 'TestEdited')

        # Delete (confirm via POST)
        delete_url = f'/superadmin/students/{profile.id}/delete/'
        # First GET shows confirmation
        resp = self.client.get(delete_url)
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post(delete_url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(username='teststudent').exists())
