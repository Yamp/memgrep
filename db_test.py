import sqlite3

from bot import create_sqlite_table


def main():
    conn = sqlite3.connect('files.db')
    c = conn.cursor()
    c.execute("SELECT * FROM posts")
    print(c.fetchall())
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
