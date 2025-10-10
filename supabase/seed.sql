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

-- Regular employee (read-only, member role)
INSERT INTO employees (employee_id, email, display_name)
VALUES
  ('550e8400-e29b-41d4-a716-446655440000', 'employee@company.com', 'John Employee')
ON CONFLICT (employee_id) DO NOTHING;

-- Manager (can upload documents, manager role)
INSERT INTO employees (employee_id, email, display_name)
VALUES
  ('660e8400-e29b-41d4-a716-446655440001', 'manager@company.com', 'Sarah Manager')
ON CONFLICT (employee_id) DO NOTHING;

-- Additional team members (for handover testing)
INSERT INTO employees (employee_id, email, display_name)
VALUES
  ('770e8400-e29b-41d4-a716-446655440002', 'mike.johnson@company.com', 'Mike Johnson'),
  ('880e8400-e29b-41d4-a716-446655440003', 'lisa.wang@company.com', 'Lisa Wang')
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

-- John Employee: Regular employee (demo-project and atlas-api) - member role
INSERT INTO employee_projects (employee_id, project_id, role)
VALUES
  ('550e8400-e29b-41d4-a716-446655440000', 'demo-project', 'member'),
  ('550e8400-e29b-41d4-a716-446655440000', 'atlas-api', 'member')
ON CONFLICT (employee_id, project_id) DO NOTHING;

-- Sarah Manager: Manager for all projects (can upload documents) - manager role
INSERT INTO employee_projects (employee_id, project_id, role)
VALUES
  ('660e8400-e29b-41d4-a716-446655440001', 'demo-project', 'manager'),
  ('660e8400-e29b-41d4-a716-446655440001', 'atlas-api', 'manager'),
  ('660e8400-e29b-41d4-a716-446655440001', 'phoenix-ui', 'manager'),
  ('660e8400-e29b-41d4-a716-446655440001', 'internal-tools', 'manager')
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

-- =============================================================================
-- 4. SAMPLE DOCUMENTS
-- =============================================================================
-- Create some test documents for search testing

INSERT INTO documents (doc_id, title, project_id, visibility, uri, language, updated_at)
VALUES
  (1, 'Atlas API Deployment Guide', 'atlas-api', 'Private', 'https://notion.so/test-atlas-deploy', 'en', NOW()),
  (2, 'Company Handbook', NULL, 'Public', 'https://notion.so/test-handbook', 'en', NOW()),
  (3, 'Phoenix UI Design System', 'phoenix-ui', 'Private', 'https://notion.so/test-phoenix-design', 'en', NOW())
ON CONFLICT (doc_id) DO NOTHING;

-- =============================================================================
-- 5. SAMPLE CHUNKS (with embeddings for search)
-- =============================================================================
-- Create chunks with dummy embeddings for testing vector search

INSERT INTO chunks (chunk_id, doc_id, heading_path, order_in_doc, text, embedding)
VALUES
  (
    1,
    1,
    ARRAY['Deployment', 'Atlas API'],
    1,
    'To deploy the Atlas API, first ensure all environment variables are set correctly in your .env file, then run make deploy to start the deployment process.',
    ARRAY(SELECT 0.1::real FROM generate_series(1, 1024))::vector
  ),
  (
    2,
    2,
    ARRAY['Handbook', 'Getting Started'],
    1,
    'Welcome to the company! This handbook contains all the information you need to get started, including onboarding steps, company policies, and team contacts.',
    ARRAY(SELECT 0.2::real FROM generate_series(1, 1024))::vector
  ),
  (
    3,
    3,
    ARRAY['Design System', 'Components'],
    1,
    'The Phoenix UI uses a modern design system with reusable components. All components follow Material Design principles with custom branding.',
    ARRAY(SELECT 0.15::real FROM generate_series(1, 1024))::vector
  )
ON CONFLICT (chunk_id) DO NOTHING;

-- =============================================================================
-- 6. SAMPLE HANDOVERS
-- =============================================================================
-- Create test handovers for the handovers feature

INSERT INTO handovers (
  handover_id,
  from_employee_id,
  to_employee_id,
  title,
  project_id,
  context,
  current_status,
  next_steps,
  resources,
  contacts,
  additional_notes,
  status,
  created_at
)
VALUES
  (
    1,
    '550e8400-e29b-41d4-a716-446655440000', -- John Employee
    '770e8400-e29b-41d4-a716-446655440002', -- Mike Johnson
    'Atlas API Project Handover',
    'atlas-api',
    'Transferring Atlas API project knowledge before moving to Phoenix team. Mike will take over backend maintenance.',
    'API deployed to production, documentation updated, monitoring configured, all tests passing.',
    '[
      {"task": "Review deployment checklist", "done": false},
      {"task": "Schedule knowledge transfer meeting", "done": false},
      {"task": "Update team wiki with handover notes", "done": false}
    ]'::jsonb,
    '[
      {"type": "doc", "doc_id": 1, "title": "Atlas API Deployment Guide"},
      {"type": "link", "url": "https://notion.so/atlas-runbook", "title": "Atlas Runbook"},
      {"type": "link", "url": "https://github.com/company/atlas-api", "title": "GitHub Repo"}
    ]'::jsonb,
    '[
      {"name": "Sarah Manager", "email": "manager@company.com", "role": "Project Manager"},
      {"name": "DevOps Team", "email": "devops@company.com", "role": "Infrastructure"}
    ]'::jsonb,
    'Please prioritize the deployment checklist review. The production environment credentials are in 1Password.',
    'pending',
    NOW() - INTERVAL '2 hours'
  ),
  (
    2,
    '660e8400-e29b-41d4-a716-446655440001', -- Sarah Manager
    '880e8400-e29b-41d4-a716-446655440003', -- Lisa Wang
    'Phoenix UI Onboarding',
    'phoenix-ui',
    'Onboarding Lisa to Phoenix UI project. She will be leading the frontend team.',
    'Environment setup completed, access granted to all repositories, design files shared.',
    '[
      {"task": "Review architecture documentation", "done": true},
      {"task": "Set up local dev environment", "done": true},
      {"task": "Complete first feature ticket", "done": false}
    ]'::jsonb,
    '[
      {"type": "doc", "doc_id": 3, "title": "Phoenix UI Design System"},
      {"type": "link", "url": "https://figma.com/phoenix", "title": "Figma Designs"}
    ]'::jsonb,
    '[
      {"name": "Design Team", "email": "design@company.com", "role": "UX/UI Design"}
    ]'::jsonb,
    'Great progress so far! Looking forward to your first PR.',
    'acknowledged',
    NOW() - INTERVAL '1 day'
  )
ON CONFLICT (handover_id) DO NOTHING;

-- =============================================================================
-- 7. HANDOVER CHUNKS (for search testing)
-- =============================================================================
-- Create chunks for handovers so they appear in RAG search

INSERT INTO chunks (chunk_id, handover_id, heading_path, order_in_doc, text, embedding)
VALUES
  (
    4,
    1,
    ARRAY['Handover', 'Atlas API Project'],
    1,
    'Atlas API Project Handover: Transferring Atlas API project knowledge. Current status: API deployed to production, documentation updated. Next steps: Review deployment checklist, schedule knowledge transfer meeting.',
    ARRAY(SELECT 0.12::real FROM generate_series(1, 1024))::vector
  ),
  (
    5,
    2,
    ARRAY['Handover', 'Phoenix UI Onboarding'],
    1,
    'Phoenix UI Onboarding: Onboarding Lisa to Phoenix UI project. Environment setup completed, access granted. Next: Complete first feature ticket.',
    ARRAY(SELECT 0.18::real FROM generate_series(1, 1024))::vector
  )
ON CONFLICT (chunk_id) DO NOTHING;

-- =============================================================================
-- 8. RESET SEQUENCES
-- =============================================================================
-- After inserting with explicit IDs, reset sequences so new inserts work

SELECT setval('handovers_handover_id_seq', (SELECT COALESCE(MAX(handover_id), 0) FROM handovers));

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
-- Login Credentials (dev mode):
--   Employee: employee@company.com / dev  (John Employee - member role)
--   Manager:  manager@company.com / dev   (Sarah Manager - manager role)
--
-- Permissions:
--   - John Employee (member):
--       • Can search documents in demo-project and atlas-api
--       • Can view documents and handovers
--       • Cannot upload documents
--       • Cannot access Manager Interface
--
--   - Sarah Manager (manager):
--       • Can search all project documents
--       • Can upload documents to any project
--       • Can access Manager Interface
--       • Can create handovers
--
-- Next steps:
-- 1. Run migration: supabase/migrations/20251007000000_add_handovers.sql
-- 2. Upload documents via Manager Interface (login as manager@company.com)
-- 3. Test handover creation and search
--
-- =============================================================================