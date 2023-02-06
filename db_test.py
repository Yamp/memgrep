import sqlite3


def check_tables():
    conn = sqlite3.connect("files.db")
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    conn.commit()
    conn.close()
    return tables

def main():

    conn = sqlite3.connect("files.db")
    c = conn.cursor()
    c.execute("SELECT * FROM files")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
