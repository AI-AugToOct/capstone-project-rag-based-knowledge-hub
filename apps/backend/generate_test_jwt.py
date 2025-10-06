#!/usr/bin/env python3
"""
Generate test JWT tokens for Supabase testing
Run: python generate_test_jwt.py [employee|manager]

Examples:
  python generate_test_jwt.py employee  # Regular employee (Test User)
  python generate_test_jwt.py manager   # Manager (Sarah Chen)
"""

import os
import sys
import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

# Get your JWT secret from .env
JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

if not JWT_SECRET:
    print("[ERROR] SUPABASE_JWT_SECRET not found in .env")
    exit(1)

# Test users from seed.sql
USERS = {
    "employee": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "test@company.com",
        "name": "Test User",
        "role_type": "Regular Employee (member)",
        "projects": ["demo-project", "atlas-api"],
        "can_upload": False
    },
    "manager": {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "email": "sarah.chen@company.com",
        "name": "Sarah Chen",
        "role_type": "Manager",
        "projects": ["atlas-api", "phoenix-ui"],
        "can_upload": True
    }
}

# Parse command line argument
user_type = sys.argv[1] if len(sys.argv) > 1 else "employee"

if user_type not in USERS:
    print(f"[ERROR] Invalid user type: {user_type}")
    print(f"   Valid options: {', '.join(USERS.keys())}")
    exit(1)

user = USERS[user_type]

# Create JWT payload
payload = {
    "sub": user["id"],  # User ID (matches seed data)
    "role": "authenticated",
    "aud": "authenticated",
    "iat": int(datetime.now(timezone.utc).timestamp()),
    "exp": int((datetime.now(timezone.utc) + timedelta(days=365)).timestamp()),  # Valid for 1 year
}

# Generate the JWT
test_jwt = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

print("=" * 80)
print(f"[OK] Generated JWT for {user['name']} ({user_type})")
print("=" * 80)
print()
print("User Info:")
print(f"  - Name: {user['name']}")
print(f"  - Email: {user['email']}")
print(f"  - Role: {user['role_type']}")
print(f"  - Projects: {', '.join(user['projects'])}")
print(f"  - Can Upload Documents: {'Yes' if user['can_upload'] else 'No (read-only)'}")
print()
print("JWT Token (copy this):")
print("-" * 80)
print(test_jwt)
print("-" * 80)
print()
print("How to Use:")
print("  1. Open browser DevTools (F12)")
print("  2. Go to Application > Local Storage > http://localhost:3000")
print("  3. Add new key-value pair:")
print(f"     Key: supabase.auth.token")
print(f'     Value: {{"access_token":"{test_jwt[:30]}..."}}')
print("  4. Refresh the page")
print()
print(f"Token expires: {datetime.fromtimestamp(payload['exp']).strftime('%Y-%m-%d')}")
print("=" * 80)