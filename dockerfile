FROM ubuntu:latest

WORKDIR /app

RUN apt update
RUN apt install -y dh-make

RUN mkdir /app/aptC-1.0
COPY * /app/aptc-1.0/

RUN cd /app/aptC-1.0

RUN dh_make --createorig

RUN dpkg-buildpackage -us -uc

RUN cd /app

RUN cp  

CMD  ["cp","/app/aptc_1.0-1_all.deb","/mnt/res"]