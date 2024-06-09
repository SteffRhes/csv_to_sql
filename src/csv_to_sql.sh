#!/bin/bash

python3 /root/csv_to_sql.py

sqlite3 test1.db "SELECT * FROM test1;" | less

sqlite3 test1.db -cmd "SELECT name, sql FROM sqlite_schema WHERE name='test1';"

