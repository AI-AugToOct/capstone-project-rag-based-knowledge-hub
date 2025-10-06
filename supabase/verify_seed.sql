-- Quick verification queries for seed data
-- Run these in IntelliJ database connector

-- 1. Check employees
SELECT employee_id, email, display_name FROM employees ORDER BY display_name;

-- 2. Check projects
SELECT project_id, name FROM projects ORDER BY name;

-- 3. Check employee-project assignments WITH ROLES
SELECT
  e.display_name as employee_name,
  e.email,
  p.name as project_name,
  ep.role as role
FROM employee_projects ep
JOIN employees e ON e.employee_id = ep.employee_id
JOIN projects p ON p.project_id = ep.project_id
ORDER BY e.display_name, p.name;

-- 4. Summary counts
SELECT
  (SELECT count(*) FROM employees) as total_employees,
  (SELECT count(*) FROM projects) as total_projects,
  (SELECT count(*) FROM employee_projects) as total_assignments;

-- 5. Verify specific test users exist
SELECT
  employee_id,
  display_name,
  email,
  CASE
    WHEN employee_id = '550e8400-e29b-41d4-a716-446655440000' THEN 'Test User (Employee)'
    WHEN employee_id = '660e8400-e29b-41d4-a716-446655440001' THEN 'Sarah Chen (Manager)'
    ELSE 'Other'
  END as user_type
FROM employees
WHERE employee_id IN (
  '550e8400-e29b-41d4-a716-446655440000',
  '660e8400-e29b-41d4-a716-446655440001'
);