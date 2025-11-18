from django.test import Client

c=Client()
logged_in = c.login(username='student1', password='password')
print('logged_in', logged_in)
r = c.get('/student-dashboard/')
print('status', r.status_code)
print(r.content[:1000])
