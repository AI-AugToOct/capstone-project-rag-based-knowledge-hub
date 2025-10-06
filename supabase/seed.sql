-- =============================================================================
-- Seed Script for RAG Knowledge Hub
-- =============================================================================
-- Run via Supabase SQL Editor or: psql "your_database_url" < supabase/seed.sql
--
-- This creates:
-- - 5 test employees (including the one from generate_test_jwt.py)
-- - 4 projects (Demo, Atlas, Phoenix, Internal Tools)
-- - Employee-project assignments
-- - Ready for testing uploads and search
-- =============================================================================

BEGIN;

-- =============================================================================
-- 1. EMPLOYEES
-- =============================================================================
-- Insert test employees (using UUIDs that match typical Supabase auth format)

-- Main test user (matches JWT from generate_test_jwt.py)
INSERT INTO employees (employee_id, email, display_name)
VALUES
  ('550e8400-e29b-41d4-a716-446655440000', 'test@company.com', 'Test User')
ON CONFLICT (employee_id) DO NOTHING;

-- Additional team members
INSERT INTO employees (employee_id, email, display_name)
VALUES
  ('660e8400-e29b-41d4-a716-446655440001', 'sarah.chen@company.com', 'Sarah Chen'),
  ('770e8400-e29b-41d4-a716-446655440002', 'mike.johnson@company.com', 'Mike Johnson'),
  ('880e8400-e29b-41d4-a716-446655440003', 'lisa.wang@company.com', 'Lisa Wang'),
  ('990e8400-e29b-41d4-a716-446655440004', 'alex.kim@company.com', 'Alex Kim')
ON CONFLICT (employee_id) DO NOTHING;

-- =============================================================================
-- 2. PROJECTS
-- =============================================================================
-- Create projects that employees can be assigned to

INSERT INTO projects (project_id, name)
VALUES
  ('demo-project', 'Demo Project'),
  ('atlas-api', 'Atlas API'),
  ('phoenix-ui', 'Phoenix UI'),
  ('internal-tools', 'Internal Tools')
ON CONFLICT (project_id) DO NOTHING;

-- =============================================================================
-- 3. EMPLOYEE-PROJECT ASSIGNMENTS
-- =============================================================================
-- Assign employees to projects with roles (creates permission boundaries)
-- Roles: 'member' (regular employee) or 'manager' (can upload/manage docs)

-- Test User: Regular employee (demo-project and atlas-api)
INSERT INTO employee_projects (employee_id, project_id, role)
VALUES
  ('550e8400-e29b-41d4-a716-446655440000', 'demo-project', 'member'),
  ('550e8400-e29b-41d4-a716-446655440000', 'atlas-api', 'member')
ON CONFLICT (employee_id, project_id) DO NOTHING;

-- Sarah Chen: Manager for Atlas and Phoenix (can upload documents)
INSERT INTO employee_projects (employee_id, project_id, role)
VALUES
  ('660e8400-e29b-41d4-a716-446655440001', 'atlas-api', 'manager'),
  ('660e8400-e29b-41d4-a716-446655440001', 'phoenix-ui', 'manager')
ON CONFLICT (employee_id, project_id) DO NOTHING;

-- Mike Johnson: Backend specialist, regular member
INSERT INTO employee_projects (employee_id, project_id, role)
VALUES
  ('770e8400-e29b-41d4-a716-446655440002', 'atlas-api', 'member'),
  ('770e8400-e29b-41d4-a716-446655440002', 'internal-tools', 'member')
ON CONFLICT (employee_id, project_id) DO NOTHING;

-- Lisa Wang: Frontend specialist, regular member (Phoenix only)
INSERT INTO employee_projects (employee_id, project_id, role)
VALUES
  ('880e8400-e29b-41d4-a716-446655440003', 'phoenix-ui', 'member')
ON CONFLICT (employee_id, project_id) DO NOTHING;

-- Alex Kim: Manager for all projects (can upload to all projects)
INSERT INTO employee_projects (employee_id, project_id, role)
VALUES
  ('990e8400-e29b-41d4-a716-446655440004', 'demo-project', 'manager'),
  ('990e8400-e29b-41d4-a716-446655440004', 'atlas-api', 'manager'),
  ('990e8400-e29b-41d4-a716-446655440004', 'phoenix-ui', 'manager'),
  ('990e8400-e29b-41d4-a716-446655440004', 'internal-tools', 'manager')
ON CONFLICT (employee_id, project_id) DO NOTHING;

COMMIT;

-- =============================================================================
-- VERIFICATION
-- =============================================================================
-- Check that data was inserted correctly

SELECT '=== SEED COMPLETE ===' as status;
SELECT '' as blank;

SELECT 'EMPLOYEES:' as section;
SELECT employee_id, email, display_name FROM employees ORDER BY display_name;
SELECT '' as blank;

SELECT 'PROJECTS:' as section;
SELECT project_id, name FROM projects ORDER BY name;
SELECT '' as blank;

SELECT 'EMPLOYEE-PROJECT ASSIGNMENTS:' as section;
SELECT
  e.display_name as employee_name,
  e.email,
  p.name as project_name,
  ep.role
FROM employee_projects ep
JOIN employees e ON e.employee_id = ep.employee_id
JOIN projects p ON p.project_id = ep.project_id
ORDER BY e.display_name, p.name;
SELECT '' as blank;

SELECT 'SUMMARY:' as section;
SELECT
  (SELECT count(*) FROM employees) as total_employees,
  (SELECT count(*) FROM projects) as total_projects,
  (SELECT count(*) FROM employee_projects) as total_assignments;

-- =============================================================================
-- NOTES
-- =============================================================================
--
-- Next steps:
-- 1. Upload documents via Manager Interface (http://localhost:3000)
-- 2. Documents can be assigned to projects (e.g., "atlas-api")
-- 3. Test permissions:
--    - Test User can see: demo-project + atlas-api documents + Public docs
--    - Lisa Wang can see: phoenix-ui documents + Public docs only
--    - Alex Kim can see: ALL project documents + Public docs
--
-- Testing JWT:
-- - The employee_id '550e8400-e29b-41d4-a716-446655440000' matches
--   the JWT generated by apps/backend/generate_test_jwt.py
-- - Use that JWT to test as "Test User"
-- - To test as other users, modify generate_test_jwt.py with their UUIDs
--
-- =============================================================================