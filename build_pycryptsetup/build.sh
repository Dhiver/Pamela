#!/bin/sh

readonly CRYPTSETUP_DEPO_URL=https://gitlab.com/cryptsetup/cryptsetup.git

apt install -y git python3 python3-dev build-essential libcryptsetup-dev

git clone $CRYPTSETUP_DEPO_URL cryptsetup
cp setup.py cryptsetup/python/.
cd cryptsetup/python/
python3 setup.py
mv pycryptsetup.cpython-35m-x86_64-linux-gnu.so ../../pycryptsetup.so
cd ../..
rm -rf cryptsetup/
