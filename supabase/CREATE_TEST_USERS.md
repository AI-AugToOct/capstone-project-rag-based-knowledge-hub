# Creating Test Users for Login

## Problem
The login page now works, but you need Supabase Auth users to actually log in.

The `employees` table and `auth.users` (Supabase Auth) are **separate systems**.

## Solution: Create Users via Supabase Dashboard

### Step 1: Go to Supabase Dashboard
1. Open https://supabase.com/dashboard
2. Select your project
3. Go to **Authentication** → **Users** (left sidebar)

### Step 2: Add Test Users
Click **"Add user"** and create these users:

#### User 1: Test User (Regular Employee)
- **Email**: `test@company.com`
- **Password**: `password123`
- **Auto Confirm**: ✅ Yes
- **User UID**: Leave empty (Supabase will generate one)

**IMPORTANT**: After creating, you need to update the user's UID to match our employee_id:
1. Copy the generated UID from the user list
2. Go to **SQL Editor**
3. Run:
```sql
-- Update auth user UID to match employee_id
UPDATE auth.users
SET id = '550e8400-e29b-41d4-a716-446655440000'::uuid
WHERE email = 'test@company.com';
```

#### User 2: Sarah Chen (Manager)
- **Email**: `sarah.chen@company.com`
- **Password**: `password123`
- **Auto Confirm**: ✅ Yes

Then update UID:
```sql
UPDATE auth.users
SET id = '660e8400-e29b-41d4-a716-446655440001'::uuid
WHERE email = 'sarah.chen@company.com';
```

### Step 3: Test Login
1. Go to http://localhost:3000/login
2. Enter:
   - Email: `test@company.com`
   - Password: `password123`
3. Click "Sign In"
4. Should redirect to home page

## Alternative: Quick Test Script

Or use this simpler approach - create a test login script:

```javascript
// In browser console at http://localhost:3000
const testToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImF1ZCI6ImF1dGhlbnRpY2F0ZWQiLCJpYXQiOjE3NTk3Njc5MzYsImV4cCI6MTc5MTMwMzkzNn0.8vC4cYpNNBLrf77R6bQC4TxMP5mBl8LLzt9bhQwx4mc"

localStorage.setItem('sb-brczyipagixshsnqhfhq-auth-token', JSON.stringify({
  access_token: testToken,
  token_type: "bearer",
  expires_in: 3600,
  refresh_token: testToken
}))

location.reload()
```

## Why This is Needed

Supabase Auth is a complete authentication system with:
- Password hashing
- Email confirmation
- Password reset
- Session management
- JWT generation

Your `employees` table just stores employee metadata. The `auth.users` table handles actual authentication.