#!/usr/bin/env bash

set -e

buildDir="build"
cryptoDir="crypto"

rm -rf $buildDir
rm -rf $cryptoDir/$buildDir
rm -rf $cryptoDir/*.so
mkdir -p $buildDir
apt-get install build-essential python python-dev libcryptsetup-dev libpam0g-dev libpam-python

# build crypto
python2 $cryptoDir/setup.py
cp $cryptoDir/pycryptsetup.so $buildDir/
cp $cryptoDir/mount_umount.py $cryptoDir/jeankevincrypto.py $cryptoDir/utils.py $buildDir

# build pam
gcc -fPIC -c jeankevinpam.c
gcc -shared -o $buildDir/libjeankevinpam.so jeankevinpam.o -lpam -lpam_misc

cp pam_module.py $buildDir/

#scp -r -P 2222 build/ root@127.0.0.1:/tmp/