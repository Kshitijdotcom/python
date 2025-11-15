"""Check database schema"""
import sqlite3

conn = sqlite3.connect('instance/users.db')
cursor = conn.cursor()

# Get table info
cursor.execute("PRAGMA table_info(user)")
columns = cursor.fetchall()

print("User table columns:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

conn.close()
