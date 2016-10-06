#!/usr/bin/env bash

set -e

gcc -fPIC -c pam_module.c
gcc -shared -o libjeankevinpam.so pam_module.o -lpam
scp -P 2222 pam_python.py libjeankevinpam.so root@127.0.0.1:/tmp/

# gcc -fPIC -c pam_module.c
# gcc -shared -o pam_module.so pam_module.o -lpam
#sudo docker build -t pamela .
