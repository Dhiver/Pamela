#!/bin/sh

if [[ $EUID -ne 0 ]]; then
	echo "This script must be run as root" 1>&2
	exit 1
fi

echo 'deb http://ftp.debian.org/debian jessie-backports main' >> /etc/apt/sources.list
apt update

apt install python3 python3-dev python3-pip libcryptsetup-dev python3-simplejson python3-systemd python3-psutil libsqlite3-dev libsqlcipher-dev
pip3 install pysqlcipher3

cd /lib/x86_64-linux-gnu/security/
git clone git@git.epitech.eu:/dhiver_b/Pamela luksypam
cd luksypam

cd pycryptsetup
pip3 install -e .

echo 'auth required pam_exec.so expose_authtok /lib/x86_64-linux-gnu/security/luksypam/luksypam/luksypam_auth.py' >> /etc/pam.d/common-auth

echo 'session required pam_exec.so /lib/x86_64-linux-gnu/security/luksypam/luksypam/luksypam_close_session.py' >> /etc/pam.d/common-session

mkdir /etc/skel/.luksypam
cp luksypam/config.json.skel /etc/skel/.luksypam/config.json

echo 'Done!'
