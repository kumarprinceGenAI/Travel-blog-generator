from database import get_connection

conn = get_connection()
cursor = conn.cursor()

print("\n--- ORDER BY ID DESC ---")
cursor.execute("""
SELECT id, topic, created_at
FROM blogs
ORDER BY id DESC
LIMIT 5;
""")
for row in cursor.fetchall():
    print(row)

print("\n--- ORDER BY created_at DESC ---")
cursor.execute("""
SELECT id, topic, created_at
FROM blogs
ORDER BY created_at DESC
LIMIT 5;
""")
for row in cursor.fetchall():
    print(row)

print("\n--- SCHEMA ---")
cursor.execute("""
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'blogs';
""")
for row in cursor.fetchall():
    print(row)

cursor.close()
conn.close()