import sqlite3

from fuzzysearch import find_near_matches
from fire import Fire

def find_postst(needle: str) -> list[str]:
    conn = sqlite3.connect('files.db')
    c = conn.cursor()
    table = c.execute("SELECT * FROM files")
    data = table.fetchall()
    res = []
    for d in data:
        ocr_text = d[5]
        if m := find_near_matches(
            needle,
            ocr_text,
            max_l_dist=2,
            max_insertions=0,
            max_deletions=0,
            max_substitutions=2,
        ):
            res += [d[6]]
    # print(data)

def search_text(needle: str):
    conn = sqlite3.connect('files.db')
    c = conn.cursor()
    table = c.execute("SELECT * FROM files")
    data = table.fetchall()
    for d in data:
        ocr_text = d[5]
        if m := find_near_matches(
            needle,
            ocr_text,
            max_l_dist=2,
            max_insertions=0,
            max_deletions=0,
            max_substitutions=2,
        ):
            print(d)
    # print(data)

if __name__ == "__main__":
    Fire(search_text)