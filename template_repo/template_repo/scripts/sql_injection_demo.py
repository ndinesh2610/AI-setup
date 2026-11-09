# ruff: noqa: S608, T201 -- intentional SQL injection demonstration
# ruff: noqa: S608, T201 -- intentional SQL injection demonstration
# ruff: noqa: S608, T201 -- intentional SQL injection demonstration
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE users (id INTEGER, username TEXT)")
conn.execute("INSERT INTO users VALUES (1, 'alice')")
conn.execute("INSERT INTO users VALUES (2, 'bob')")

# Unsafe: SQL string concatenation
username = "' OR '1'='1"
unsafe_query = f"SELECT * FROM users WHERE username = '{username}'"
print("Unsafe query:", unsafe_query)
print("Unsafe result:", conn.execute(unsafe_query).fetchall())

# Safe: parameterized query
safe_query = "SELECT * FROM users WHERE username = ?"
print("Safe result:", conn.execute(safe_query, (username,)).fetchall())

conn.close()
