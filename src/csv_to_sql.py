import csv
import sqlite3


CSV_FILE = "test1.csv"
DATA_ID = CSV_FILE.split(".csv")[0]
SHOULD_READ_HEADER = True


def sanitize_name(name):
    return "\"" + name.replace("\"", "\"\"") + "\""


with open(CSV_FILE, "r") as f:
    table_name = sanitize_name(DATA_ID)
    db_file = DATA_ID + ".db"

    csv_reader = csv.reader(f)

    conn = sqlite3.connect(db_file)
    conn.cursor().execute(f"DROP TABLE IF EXISTS {table_name}")

    for line_number, row in enumerate(csv_reader):
        row = [line_number + 1] + row

        if line_number == 0:
            max_col_len = len(row)
            headers = ["line_number INTEGER"]
            if SHOULD_READ_HEADER:
                headers += row[1:]
            else:
                headers += [f"col_{i + 1}" for i in range(max_col_len)]

            headers_sanitized = ", ".join([sanitize_name(h) for h in headers])
            conn.cursor().execute(f"CREATE TABLE {table_name} ({headers_sanitized})")

            # cursor = conn.cursor()
            # cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            # print(list(cursor.fetchall()))
            # cursor.execute(f"PRAGMA table_info({table_name})")
            # print(list(cursor.fetchall()))

            if SHOULD_READ_HEADER:
                continue


        col_number_diff = max_col_len - len(row)

        if col_number_diff > 0:
            for i in range(col_number_diff):
                row.append(None)

        elif col_number_diff < 0:
            for i in range(max_col_len, len(row)):
                conn.cursor().execute(f"ALTER TABLE {table_name} ADD COLUMN col_{i + 1}")
            max_col_len = len(row)

        place_holder = ("?, " * max_col_len)[:-2]

        conn.cursor().execute(f"INSERT INTO {table_name} VALUES ({place_holder})", row)

    # cursor = conn.cursor()
    # cursor.execute(f"SELECT * FROM {table_name}")
    # print(list(cursor.fetchall()))
    conn.commit()
    conn.close()

