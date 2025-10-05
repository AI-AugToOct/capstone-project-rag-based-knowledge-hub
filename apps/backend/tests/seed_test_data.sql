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

-- Reset sequences to prevent ID conflicts
SELECT setval('documents_doc_id_seq', (SELECT MAX(doc_id) FROM documents), true);
SELECT setval('chunks_chunk_id_seq', (SELECT MAX(chunk_id) FROM chunks), true);

-- Verify data was inserted
SELECT 'Employees:', COUNT(*) FROM employees;
SELECT 'Projects:', COUNT(*) FROM projects;
SELECT 'Employee-Projects:', COUNT(*) FROM employee_projects;
SELECT 'Documents:', COUNT(*) FROM documents;
SELECT 'Chunks:', COUNT(*) FROM chunks;