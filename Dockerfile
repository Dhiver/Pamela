FROM debian:latest
MAINTAINER Adrien WERY "adrien.wery@epitech.eu"

ENV DEBIAN_FRONTEND noninteractive

RUN (apt update && apt upgrade -y && apt install openssl gnupg -y)

RUN useradd -m -d /home/toto  -s /bin/bash -p $(echo toto | openssl passwd -1 -stdin) toto
RUN useradd -m -d /home/titi  -s /bin/bash -p $(echo titi | openssl passwd -1 -stdin) titi
