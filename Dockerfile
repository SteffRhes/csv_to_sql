FROM debian:latest
RUN apt update
RUN apt install -y python3 sqlite3
WORKDIR /mount

