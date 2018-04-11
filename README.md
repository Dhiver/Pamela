# Pamela

School project where we had to develop a PAM module.

This module decrypts a file in the users' home directories when the users logged in.

## Requirements

Add backports

```bash
# echo 'deb http://ftp.debian.org/debian jessie-backports main' > /etc/apt/sources.list
# apt update
```

```bash
# apt install python3 python3-dev python3-pip libcryptsetup-dev python3-simplejson python3-systemd python3-guestfs python3-psutil libsqlite3-dev libsqlcipher-dev
# pip3 install pysqlcipher3
```

```bash
$ cd /lib/x86_64-linux-gnu/security/
$ git clone git@git.epitech.eu:/dhiver_b/Pamela luksypam
```

Install `pycryptsetup` python module
```bash
$ cd pycryptsetup
# pip3 install -e .
```

Add at the end of /etc/pam.d/common-auth
```text
auth required pam_exec.so expose_authtok /lib/x86_64-linux-gnu/security/luksypam/luksypam/luksypam_auth.py
```

And at the end of /etc/pam.d/common-session
```text
session required pam_exec.so /lib/x86_64-linux-gnu/security/luksypam/luksypam/luksypam_close_session.py
```

## Bonus

* Container and configuration file creation on the fly
* SSH capable
* Logs via systemd + verbose mode
* A CLI tool is provided to change the container password
* Multi-containers
* Mountpoint and name of the volume can be set
* In Python3!
* Build module pycryptsetup
* Modification added to the pycryptsetup module (hash algorithm + True random)
* Profile management (weak or not?)
* Generated container are filled with random values
* Secure deletion
* Passwords stored in a database
* Container size can be specified
* Containers can be disabled
* pam\_exec.so recode
