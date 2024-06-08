import csv
import sqlite3


CHECK_DELIMITERS = [",", ";", "\t"]
CHECK_SAMPLE_LIMIT = 100
CSV_FILE = "test1.csv"
DATA_ID = CSV_FILE.split(".csv")[0]
SHOULD_READ_HEADER = True


def sanitize_name(name):
    return "\"" + name.replace("\"", "\"\"") + "\""

def get_delimiter():
    with open(CSV_FILE, "r") as f:
        delimiter_count_all = {d: {} for d in CHECK_DELIMITERS}
        for i, row in enumerate(f):
            if i == CHECK_SAMPLE_LIMIT:
                break
            for delimiter, delimiter_count_rows in delimiter_count_all.items():
                count = row.count(delimiter)
                # TODO: what about files where there is only one column and no delimiter?
                if count != 0:
                    delimiter_count_rows[count] = delimiter_count_rows.get(count, 0) + 1
                    delimiter_count_all[delimiter] = delimiter_count_rows

        highest_occurrence_number = 0
        highest_occurrence_delimiter = None
        for delimiter, delimiter_count_rows in delimiter_count_all.items():
            for _, count in delimiter_count_rows.items():
                if count > highest_occurrence_number:
                    highest_occurrence_number = count
                    highest_occurrence_delimiter = delimiter

    print(f"found delimiter: {highest_occurrence_delimiter.__repr__()}")
    return highest_occurrence_delimiter


with open(CSV_FILE, "r") as f:
    table_name = sanitize_name(DATA_ID)
    db_file = DATA_ID + ".db"

    csv_reader = csv.reader(f, delimiter=get_delimiter())

    conn = sqlite3.connect(db_file)
    conn.cursor().execute(f"DROP TABLE IF EXISTS {table_name}")

    for line_number, row in enumerate(csv_reader):
        row = [line_number + 1] + row

        if line_number == 0:
            max_col_len = len(row)
            if SHOULD_READ_HEADER:
                headers = row[1:]
            else:
                headers = [f"col_{i + 1}" for i in range(max_col_len - 1)]

            headers_sanitized = ", ".join([sanitize_name(h) for h in headers])
            headers_sanitized = "line_number INTEGER, " + headers_sanitized
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
                conn.cursor().execute(f"ALTER TABLE {table_name} ADD COLUMN col_{i}")
            max_col_len = len(row)

        place_holder = ("?, " * max_col_len)[:-2]

        conn.cursor().execute(f"INSERT INTO {table_name} VALUES ({place_holder})", row)

    # cursor = conn.cursor()
    # cursor.execute(f"SELECT * FROM {table_name}")
    # print(list(cursor.fetchall()))

    conn.commit()
    conn.close()

