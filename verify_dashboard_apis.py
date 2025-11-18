#!/usr/bin/env python3
"""
Quick test script to verify all student dashboard APIs are working correctly.
Run this after starting the Django development server.

Usage: python verify_dashboard_apis.py
"""

import requests
import json
from urllib.parse import urljoin

BASE_URL = 'http://localhost:8000'
ENDPOINTS = [
    '/api/student/tasks/',
    '/api/student/materials/',
    '/api/student/timetable/',
    '/api/student/events/',
    '/api/student/notifications/',
    '/api/attendance/realtime/',
    '/api/latest-uploads/',
]

def test_endpoints():
    """Test all dashboard API endpoints."""
    print("=" * 70)
    print("STUDENT DASHBOARD API VERIFICATION")
    print("=" * 70)
    print()
    
    # First, try to login (you may need to adjust this based on your auth setup)
    print("Testing API Endpoints...")
    print()
    
    session = requests.Session()
    
    for endpoint in ENDPOINTS:
        url = urljoin(BASE_URL, endpoint)
        print(f"Testing: {endpoint}")
        print(f"  URL: {url}")
        
        try:
            response = session.get(url)
            
            if response.status_code == 401:
                print(f"  ❌ Status: 401 (Unauthorized)")
                print(f"     Note: This endpoint requires login")
            elif response.status_code == 403:
                print(f"  ❌ Status: 403 (Forbidden)")
                print(f"     Note: User may not have 'student' role")
            elif response.status_code == 200:
                print(f"  ✅ Status: 200 (OK)")
                try:
                    data = response.json()
                    print(f"  Response type: {type(data).__name__}")
                    if isinstance(data, dict):
                        print(f"  Keys: {list(data.keys())}")
                    elif isinstance(data, list):
                        print(f"  Items: {len(data)}")
                except:
                    print(f"  Response: {response.text[:100]}")
            else:
                print(f"  ⚠️ Status: {response.status_code}")
                print(f"  Response: {response.text[:100]}")
                
        except requests.exceptions.ConnectionError:
            print(f"  ❌ Connection Error")
            print(f"     Make sure Django server is running on {BASE_URL}")
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
        
        print()
    
    print("=" * 70)
    print("VERIFICATION COMPLETE")
    print("=" * 70)
    print()
    print("To test with authentication:")
    print("1. Login to your Django app at http://localhost:8000/login/")
    print("2. Then run this script again, or")
    print("3. Test directly in your browser:")
    print(f"   - Visit {BASE_URL}/student-dashboard/")
    print("   - Open browser DevTools (F12)")
    print("   - Go to Network tab to see API calls")
    print()

if __name__ == '__main__':
    test_endpoints()
