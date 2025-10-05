#!/usr/bin/env python3
"""
Generate a test JWT token for Supabase testing
Run: python generate_test_jwt.py
"""

import os
import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

# Get your JWT secret from .env (Must have it there)
JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")


if not JWT_SECRET:
    print("SUPABASE_JWT_SECRET not found in .env")
    exit(1)

# Create a test JWT payload
payload = {
    "sub": "550e8400-e29b-41d4-a716-446655440000",  # Test user ID (matches seed data)
    "role": "authenticated",
    "aud": "authenticated",
    "iat": int(datetime.now(timezone.utc).timestamp()),
    "exp": int((datetime.now(timezone.utc) + timedelta(days=365)).timestamp()),  # Valid for 1 year
}

# Generate the JWT
test_jwt = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

print("=" * 80)
print("✅ Generated TEST_JWT_TOKEN")
print("=" * 80)
print()
print("FULL TOKEN (copy everything below this line):")
print("-" * 80)
print(test_jwt)
print("-" * 80)
print()
print("Add to your .env file:")
print(f'TEST_JWT_TOKEN={test_jwt}')
print()
print("Token Info:")
print(f"  - User ID (sub): {payload['sub']}")
print(f"  - Role: {payload['role']}")
print(f"  - Expires: {datetime.fromtimestamp(payload['exp']).strftime('%Y-%m-%d')}")
print()
print("Verify it has 3 parts separated by dots (Header.Payload.Signature)")
parts = test_jwt.split('.')
print(f"  - Parts count: {len(parts)} {'✅' if len(parts) == 3 else '❌ ERROR!'}")
if len(parts) == 3:
    print(f"  - Header length: {len(parts[0])} chars")
    print(f"  - Payload length: {len(parts[1])} chars")
    print(f"  - Signature length: {len(parts[2])} chars")
print("=" * 80)