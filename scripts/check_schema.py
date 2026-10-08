from esper.db import connect, init_schema
from esper.config import DB_PATH, DATA_DIR, FILES_DIR, PROJECT_ROOT

conn = connect(DB_PATH)

# Check the PRAGMA settings
for pragma in ("foreign_keys", "journal_mode", "busy_timeout"):
    values = conn.execute(f'PRAGMA {pragma}').fetchone()[0]
    print(f'{pragma}: {values}')

# Calling it twice should not fail
init_schema(conn)
init_schema(conn)

tables = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall() # sqlite_master lists every object in the database
print("tables:", [row["name"] for row in tables])

# Check the columns of the documents table
for col in conn.execute("PRAGMA table_info(documents)"):
    print(col["name"], col["type"], "NOT NULL" if col["notnull"] else "", col["dflt_value"] or "")

conn.close()