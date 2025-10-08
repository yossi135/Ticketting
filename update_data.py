from db import connect
from security import hash_password

cursor = connect().cursor()
cursor.execute("SELECT Name, password FROM IT_Info")
rows = cursor.fetchall()

for row in rows:
    name = row.Name
    raw_pass = str(row.password).strip()

    if not raw_pass.startswith("$2b$"):
        hashed = hash_password(raw_pass)
        cursor.execute("UPDATE IT_Info SET password = ? WHERE Name = ?", (hashed, name))

cursor.connection.commit()
cursor.connection.close()
print("✅ Passwords updated successfully.")
