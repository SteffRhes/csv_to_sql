FROM debian:latest
RUN apt update
RUN apt install -y python3 sqlite3
COPY ./src/sqliterc /root/.sqliterc
COPY ./src/csv_to_sql.py /root/csv_to_sql.py
COPY ./src/csv_to_sql.sh /root/csv_to_sql.sh
WORKDIR /mount
CMD ["/root/csv_to_sql.sh"]

