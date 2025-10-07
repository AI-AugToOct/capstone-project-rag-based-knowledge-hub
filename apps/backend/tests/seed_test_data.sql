-- ============================================================================
-- Test Data Seed for Backend Tests
-- Run this once to populate test data in your database ( Go to supabase, then execute in SQL editor )
-- ============================================================================

-- 1. Create test employee
INSERT INTO employees (employee_id, email, display_name)
VALUES ('550e8400-e29b-41d4-a716-446655440000', 'test@example.com', 'Test User')
ON CONFLICT (employee_id) DO NOTHING;

-- 2. Create test projects
INSERT INTO projects (project_id, name)
VALUES
    ('Atlas', 'Atlas Platform'),
    ('Phoenix', 'Phoenix System')
ON CONFLICT (project_id) DO NOTHING;

-- 3. Assign user to projects
INSERT INTO employee_projects (employee_id, project_id, role)
VALUES
    ('550e8400-e29b-41d4-a716-446655440000', 'Atlas', 'viewer'),
    ('550e8400-e29b-41d4-a716-446655440000', 'Phoenix', 'viewer')
ON CONFLICT (employee_id, project_id) DO NOTHING;

-- 4. Create test documents
INSERT INTO documents (doc_id, title, project_id, visibility, uri, language, updated_at)
VALUES
    (1, 'Atlas Deploy Guide', 'Atlas', 'Private', 'https://notion.so/test-atlas', 'en', NOW()),
    (2, 'Company Handbook', NULL, 'Public', 'https://notion.so/test-handbook', 'en', NOW())
ON CONFLICT (doc_id) DO NOTHING;

-- 5. Create test chunks with embeddings
-- Note: These are dummy 1024-dim vectors for testing
INSERT INTO chunks (chunk_id, doc_id, heading_path, order_in_doc, text, embedding)
VALUES
    (
        1,
        1,
        ARRAY['Deployment', 'Atlas API'],
        1,
        'To deploy the Atlas API, first ensure all environment variables are set, then run make deploy.',
        -- Dummy embedding (1024 dimensions, all 0.1)
        ARRAY(SELECT 0.1::real FROM generate_series(1, 1024))::vector
    ),
    (
        2,
        2,
        ARRAY['Handbook', 'Getting Started'],
        1,
        'Welcome to the company! This handbook contains all the information you need to get started.',
        -- Different dummy embedding
        ARRAY(SELECT 0.2::real FROM generate_series(1, 1024))::vector
    )
ON CONFLICT (chunk_id) DO NOTHING;

-- 6. Create second test employee (for handover recipient)
INSERT INTO employees (employee_id, email, display_name)
VALUES ('660e8400-e29b-41d4-a716-446655440001', 'recipient@example.com', 'Recipient User')
ON CONFLICT (employee_id) DO NOTHING;

-- 7. Create test handovers
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
        '550e8400-e29b-41d4-a716-446655440000',
        '660e8400-e29b-41d4-a716-446655440001',
        'Atlas Project Handover',
        'Atlas',
        'Transferring Atlas project knowledge before moving to Phoenix team',
        'API deployed, documentation updated, monitoring configured',
        '[{"task": "Review deployment checklist", "done": false}, {"task": "Schedule knowledge transfer meeting", "done": false}]'::jsonb,
        '[{"type": "doc", "doc_id": 1, "title": "Atlas Deploy Guide"}, {"type": "link", "url": "https://notion.so/atlas-runbook", "title": "Atlas Runbook"}]'::jsonb,
        '[{"name": "Sarah Khan", "email": "sarah@example.com", "role": "Team Lead"}]'::jsonb,
        'Please prioritize the deployment checklist review',
        'pending',
        NOW() - INTERVAL '2 hours'
    ),
    (
        2,
        '660e8400-e29b-41d4-a716-446655440001',
        '550e8400-e29b-41d4-a716-446655440000',
        'Phoenix Setup Handover',
        'Phoenix',
        'Onboarding to Phoenix project',
        'Environment setup completed',
        '[{"task": "Review architecture docs", "done": true}, {"task": "Set up local dev environment", "done": true}]'::jsonb,
        '[{"type": "link", "url": "https://github.com/phoenix", "title": "Phoenix Repo"}]'::jsonb,
        '[{"name": "Omar Amari", "email": "omar@example.com", "role": "Tech Lead"}]'::jsonb,
        NULL,
        'acknowledged',
        NOW() - INTERVAL '1 day'
    )
ON CONFLICT (handover_id) DO NOTHING;

-- 8. Create test chunks for handovers (for search testing)
INSERT INTO chunks (chunk_id, handover_id, heading_path, order_in_doc, text, embedding)
VALUES
    (
        3,
        1,
        ARRAY['Handover', 'Atlas Project'],
        1,
        'Atlas Project Handover: Transferring Atlas project knowledge. Current status: API deployed, documentation updated. Next steps: Review deployment checklist.',
        ARRAY(SELECT 0.15::real FROM generate_series(1, 1024))::vector
    )
ON CONFLICT (chunk_id) DO NOTHING;

-- Reset sequences to prevent ID conflicts
SELECT setval('documents_doc_id_seq', (SELECT MAX(doc_id) FROM documents), true);
SELECT setval('chunks_chunk_id_seq', (SELECT MAX(chunk_id) FROM chunks), true);
SELECT setval('handovers_handover_id_seq', (SELECT MAX(handover_id) FROM handovers), true);

-- Verify data was inserted
SELECT 'Employees:', COUNT(*) FROM employees;
SELECT 'Projects:', COUNT(*) FROM projects;
SELECT 'Employee-Projects:', COUNT(*) FROM employee_projects;
SELECT 'Documents:', COUNT(*) FROM documents;
SELECT 'Chunks:', COUNT(*) FROM chunks;
SELECT 'Handovers:', COUNT(*) FROM handovers;