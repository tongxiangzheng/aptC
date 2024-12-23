FROM ubuntu:latest AS packager

WORKDIR /app/aptc-1.0

RUN apt update && apt install -y dh-make

COPY bin /app/aptc-1.0/bin
COPY etc /app/aptc-1.0/etc
COPY src /app/aptc-1.0/src
COPY debian /app/aptc-1.0/debian
COPY makefile /app/aptc-1.0/makefile

RUN dpkg-buildpackage -us -uc

FROM scratch AS deb_package
COPY --from=packager /app/aptc_1.0_all.deb /