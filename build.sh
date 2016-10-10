#!/usr/bin/env bash

set -e

buildDir="build"
cryptoDir="crypto"

# build crypto
python3 $cryptoDir/setup.py
cp $cryptoDir/pycryptsetup.cpython-35m-x86_64-linux-gnu.so $buildDir/pycryptsetup.so
cp $cryptoDir/mount_umount.py $cryptoDir/jeankevincrypto.py $cryptoDir/utils.py $buildDir

# build pam
gcc -fPIC -c jeankevinpam.c
gcc -shared -o $buildDir/libjeankevinpam.so jeankevinpam.o -lpam

cp pam_module.py $buildDir/