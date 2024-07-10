#!/bin/bash

csv_file=""
db_file=""
db_name=""
should_persist=0
should_skip_headers=0


handle_help() {
  echo "additional args: --persist --skip-headers"
  exit 1
}


if [[ $# -eq 0 || ( $# -eq 1 && $1 == "--help" ) ]]; then 

  handle_help

else

  # file handling
  csv_file="$1"
  db_name="${csv_file%.*}"
  db_file="$db_name".sqlite
  shift 1

  # other args handling
  while [[ $# -gt 0 ]]; do
    if [[ $1 == "--persist" ]]; then
      should_persist=1
      shift 1
    elif [[ $1 == "--skip-headers" ]]; then
      should_skip_headers=1
      shift 1
    else
      handle_help
    fi
  done

fi

python3 /root/csv_to_sql.py "$csv_file" "$db_file" "$db_name" "$should_skip_headers"

sqlite3 "$db_file" "SELECT * FROM ${db_name};" | less

sqlite3 "$db_file" -cmd "SELECT name, sql FROM sqlite_schema WHERE name=\"${db_name}\";"

if [[ "$should_persist" -eq 0 ]]; then
  rm "$db_file"
fi

