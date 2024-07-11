import argparse
import csv
import sys
import sqlite3


csv.field_size_limit(sys.maxsize)


CSV_FILE = None
DB_FILE = None
DB_NAME = None
SHOULD_SKIP_HEADERS = None
CHECK_DELIMITERS = [",", ";", "\t"]
CHECK_SAMPLE_LIMIT = 100


def handle_args():

    # define args
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file")
    parser.add_argument("db_file")
    parser.add_argument("db_name")
    parser.add_argument("should_skip_headers", type=int)
    args = parser.parse_args()

    # read args into variables
    global CSV_FILE
    global DB_FILE
    global DB_NAME
    global SHOULD_SKIP_HEADERS
    CSV_FILE = args.csv_file
    DB_FILE = args.db_file
    DB_NAME = args.db_name
    if args.should_skip_headers == 0:
        SHOULD_SKIP_HEADERS = False
    elif args.should_skip_headers == 1:
        SHOULD_SKIP_HEADERS = True
    print(f"CSV_FILE: {CSV_FILE}")
    print(f"DB_FILE: {DB_FILE}")
    print(f"SHOULD_SKIP_HEADERS: {SHOULD_SKIP_HEADERS}")


def sanitize_name(name):
    return "\"" + name.replace("\"", "\"\"") + "\""


def get_delimiter():
    with open(CSV_FILE, "r") as f:

        # count occurences of delimiters
        delimiter_count_all = {d: {} for d in CHECK_DELIMITERS}
        for i, row in enumerate(f):
            if i == CHECK_SAMPLE_LIMIT:
                break
            for delimiter, delimiter_count_rows in delimiter_count_all.items():
                count = row.count(delimiter)
                if count != 0:
                    delimiter_count_rows[count] = delimiter_count_rows.get(count, 0) + 1
                    delimiter_count_all[delimiter] = delimiter_count_rows

        # get highest occurring pattern
        highest_occurrence_number = 0
        highest_occurrence_delimiter = None
        for delimiter, delimiter_count_rows in delimiter_count_all.items():
            for _, count in delimiter_count_rows.items():
                if count > highest_occurrence_number:
                    highest_occurrence_number = count
                    highest_occurrence_delimiter = delimiter

    print(f"found delimiter: {highest_occurrence_delimiter.__repr__()}")
    return highest_occurrence_delimiter


def cast_to_types(row):
    row_casted = []
    for col in row:
        col_casted = col
        try:
            col_casted = float(col)
        except:
            pass
        try:
            col_casted = int(col)
        except:
            pass
        row_casted.append(col_casted)
    return row_casted


def main():
    print("loading csv/tsv into db")
    handle_args()
    with open(CSV_FILE, "r") as f:

        # prepare
        csv_reader = csv.reader(f, delimiter=get_delimiter())
        table_name = sanitize_name(DB_NAME)
        conn = sqlite3.connect(DB_FILE)
        conn.cursor().execute(f"DROP TABLE IF EXISTS {table_name}")

        # iterate over rows
        for line_number, row in enumerate(csv_reader):
            row = [line_number + 1] + row

            # handle first line
            if line_number == 0:
                max_col_len = len(row)
                if not SHOULD_SKIP_HEADERS:
                    headers = row[1:]
                else:
                    headers = [f"col_{i + 1}" for i in range(max_col_len - 1)]
                headers_sanitized = ", ".join([sanitize_name(h) for h in headers])
                headers_sanitized = "line_number INTEGER PRIMARY KEY, " + headers_sanitized
                conn.cursor().execute(f"CREATE TABLE {table_name} ({headers_sanitized})")
                if not SHOULD_SKIP_HEADERS:
                    continue

            # handle different number of columns 
            col_number_diff = max_col_len - len(row)
            if col_number_diff > 0:
                for i in range(col_number_diff):
                    row.append(None)
            elif col_number_diff < 0:
                for i in range(max_col_len, len(row)):
                    conn.cursor().execute(f"ALTER TABLE {table_name} ADD COLUMN col_{i}")
                max_col_len = len(row)

            # handle types and write to db
            row = cast_to_types(row)
            place_holder = "?, " * max_col_len
            place_holder = place_holder[:-2]
            conn.cursor().execute(f"INSERT INTO {table_name} VALUES ({place_holder})", row)

        # finalize
        conn.commit()
        conn.close()

    print("done with loading csv/tsv into db")


if __name__ == "__main__":
    main()

