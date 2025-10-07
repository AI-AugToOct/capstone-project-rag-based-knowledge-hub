import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

# Check constraints on documents table
cur.execute("""
    SELECT conname, contype, pg_get_constraintdef(oid)
    FROM pg_constraint
    WHERE conrelid = 'documents'::regclass;
""")

print("=== CONSTRAINTS ON documents TABLE ===")
for row in cur.fetchall():
    print(f"{row[0]} ({row[1]}): {row[2]}")

print("\n=== INDEXES ON documents TABLE ===")
cur.execute("""
    SELECT indexname, indexdef
    FROM pg_indexes
    WHERE tablename = 'documents';
""")
for row in cur.fetchall():
    print(f"{row[0]}: {row[1]}")

print("\n=== EXISTING DOCUMENTS ===")
cur.execute("""
    SELECT doc_id, title, source_external_id, uri
    FROM documents
    LIMIT 10;
""")
for row in cur.fetchall():
    print(f"ID {row[0]}: {row[1]} (external_id={row[2]}, uri={row[3][:50] if row[3] else None})")

conn.close()
