import sqlite3

from bot import create_sqlite_table

def check_tables():
    conn = sqlite3.connect('files.db')
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    conn.commit()
    conn.close()
    return tables

def main():
    print(check_tables())

    conn = sqlite3.connect('files.db')
    c = conn.cursor()
    c.execute("SELECT * FROM files")
    print(c.fetchall())
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
