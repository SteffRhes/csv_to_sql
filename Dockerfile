FROM debian:bullseye-20230227
RUN apt update
RUN apt install -y less
RUN apt install -y sqlite3
RUN apt install -y python3
RUN apt install -y python3-pip
RUN pip3 install ipython
RUN pip3 install ipdb
COPY ./src/sqliterc /root/.sqliterc
COPY ./src/csv_to_sql.py /root/csv_to_sql.py
COPY ./src/csv_to_sql.sh /root/csv_to_sql.sh
WORKDIR /mount
ENTRYPOINT ["/root/csv_to_sql.sh"]

