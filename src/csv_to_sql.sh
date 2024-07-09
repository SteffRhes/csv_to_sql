#!/bin/bash

python3 /root/csv_to_sql.py

sqlite3 test.db "SELECT * FROM test;" | less

sqlite3 test.db -cmd "SELECT name, sql FROM sqlite_schema WHERE name='test';"

