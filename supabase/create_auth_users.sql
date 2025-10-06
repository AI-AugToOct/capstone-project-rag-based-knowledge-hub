-- =============================================================================
-- Create Supabase Auth Users for Testing
-- =============================================================================
-- Run this in Supabase SQL Editor to create test users
--
-- IMPORTANT: This creates users in the auth.users table (Supabase Auth)
-- These are SEPARATE from the employees table we created earlier
--
-- After running this, you can log in with:
-- - Email: test@company.com, Password: password123
-- - Email: sarah.chen@company.com, Password: password123
-- =============================================================================

-- Create Test User (regular employee)
INSERT INTO auth.users (
  id,
  instance_id,
  email,
  encrypted_password,
  email_confirmed_at,
  created_at,
  updated_at,
  raw_app_meta_data,
  raw_user_meta_data,
  is_super_admin,
  role,
  aud
)
VALUES (
  '550e8400-e29b-41d4-a716-446655440000'::uuid,
  '00000000-0000-0000-0000-000000000000'::uuid,
  'test@company.com',
  crypt('password123', gen_salt('bf')),
  now(),
  now(),
  now(),
  '{"provider":"email","providers":["email"]}'::jsonb,
  '{}'::jsonb,
  false,
  'authenticated',
  'authenticated'
)
ON CONFLICT (id) DO NOTHING;

-- Create Sarah Chen (manager)
INSERT INTO auth.users (
  id,
  instance_id,
  email,
  encrypted_password,
  email_confirmed_at,
  created_at,
  updated_at,
  raw_app_meta_data,
  raw_user_meta_data,
  is_super_admin,
  role,
  aud
)
VALUES (
  '660e8400-e29b-41d4-a716-446655440001'::uuid,
  '00000000-0000-0000-0000-000000000000'::uuid,
  'sarah.chen@company.com',
  crypt('password123', gen_salt('bf')),
  now(),
  now(),
  now(),
  '{"provider":"email","providers":["email"]}'::jsonb,
  '{}'::jsonb,
  false,
  'authenticated',
  'authenticated'
)
ON CONFLICT (id) DO NOTHING;

-- =============================================================================
-- VERIFICATION
-- =============================================================================

SELECT
  id,
  email,
  email_confirmed_at,
  created_at
FROM auth.users
WHERE email IN ('test@company.com', 'sarah.chen@company.com');