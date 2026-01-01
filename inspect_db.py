import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# List tables
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
print("Tables:", tables)

# For each table, show data
for table in tables:
    table_name = table[0]
    print(f"\nData in {table_name}:")
    c.execute(f"SELECT * FROM {table_name}")
    rows = c.fetchall()
    for row in rows:
        print(row)

conn.close()