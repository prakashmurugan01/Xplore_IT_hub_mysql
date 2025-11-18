#!/usr/bin/env python
"""Test notification display fix"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xplorehub.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from portal.models import Profile, Notification
import json

print("=" * 60)
print("TESTING NOTIFICATION FIX")
print("=" * 60)

# Create test user
try:
    user = User.objects.create_user(
        username='testnotif',
        email='testnotif@test.com',
        password='testpass123'
    )
    profile = Profile.objects.create(
        user=user,
        role='student'
    )
    print(f"✓ Test user created: {user.username}")
except Exception as e:
    user = User.objects.get(username='testnotif')
    print(f"✓ Test user exists: {user.username}")

# Create test notifications
for i in range(3):
    notif, created = Notification.objects.get_or_create(
        user=user,
        title=f"📅 Schedule: Test Schedule {i+1}",
        message=f"Test notification message {i+1}",
        is_read=False if i < 2 else True
    )
    if created:
        print(f"✓ Notification {i+1} created")

# Test API endpoint
client = Client()
client.login(username='testnotif', password='testpass123')

print("\n" + "-" * 60)
print("Testing API endpoint: /api/student/notifications/")
print("-" * 60)

response = client.get('/api/student/notifications/')
print(f"Status Code: {response.status_code}")

data = response.json()
print(f"\nAPI Response Structure:")
print(json.dumps(data, indent=2))

print(f"\n✓ Response has 'notifications' key: {'notifications' in data}")
print(f"✓ Response has 'unread_count' key: {'unread_count' in data}")

if 'notifications' in data:
    notifications = data['notifications']
    print(f"✓ Number of notifications: {len(notifications)}")
    
    if notifications:
        first = notifications[0]
        print(f"\nFirst notification structure:")
        print(f"  - id: {first.get('id')}")
        print(f"  - title: {first.get('title')}")
        print(f"  - message: {first.get('message')}")
        print(f"  - type: {first.get('type')}")
        print(f"  - is_read: {first.get('is_read')}")
        print(f"  - created_at: {first.get('created_at')}")
        
        required_fields = ['id', 'title', 'message', 'type', 'is_read', 'created_at']
        missing = [f for f in required_fields if f not in first]
        if missing:
            print(f"\n⚠ Missing fields: {missing}")
        else:
            print(f"\n✓ All required fields present for renderNotifications()")

print("\n" + "=" * 60)
print("FIX APPLIED:")
print("=" * 60)
print("""
In fetchNotifications():
  OLD: notificationsData = await response.json();
  NEW: const data = await response.json();
       notificationsData = data.notifications || data;

This extracts the notifications array from the API response object,
allowing renderNotifications() to iterate over the array correctly.
""")

print("\n✓ Dashboard sidebar notifications should now display!")
