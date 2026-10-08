import sqlite3
import sqlite_vec

# engine version used by python
print("SQLite: ", sqlite3.sqlite_version)

# database in memory, disappear at the end of execution
conn = sqlite3.connect(":memory:")

# enables extentions loading, loads sqlite_vec, then disable the extension loading
conn.enable_load_extension(True)
sqlite_vec.load(conn)
conn.enable_load_extension(False)

# asks to sqlite-vec it's version
print(":sqlite-vec:", conn.execute("SELECT vec_version()").fetchone()[0])