#!/usr/bin/env bash

set -e

gcc -fPIC -c pam_module.c
gcc -shared -o pam_module.so pam_module.o -lpam
#sudo docker build -t pamela .
