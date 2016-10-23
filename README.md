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
cd /lib/x86_64-linux-gnu/security/
git clone git@git.epitech.eu:/dhiver_b/Pamela luksypam
```

Install `pycryptsetup` python module
```bash
cd pycryptsetup
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
