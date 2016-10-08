## Mandatory part

- [ ] Open an encrypted volume in user's home folder when user log in
	- [ ] To make a mount set userid to 0 (root) in order to mount a volume
	- [ ] Detect that the user has not mounted the directory yet
	- [ ] If a user is logged in twice, it is important that the user's home directory is not unmounted the first time the user logs out.
- [ ] When user log out, close the volume

## Bonus

- [ ] Handle a debug flag in our module (talk to systemd)
```c
/* Don't forget the -lsystemd */
#include <systemd/sd-journal.h>

sd_journal_print(LOG_NOTICE, "Hello World");
}
```

```python
# See https://www.freedesktop.org/software/systemd/python-systemd/journal.html
import logging
from systemd.journal import JournalHandler

log = logging.getLogger('demo')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)
log.info("sent to journal")
```

- [ ] Create a config file
	- [ ] Specify where the volume is regarding the user
	- [ ] Say if the encrypted volume password is different from the user session password

## Test cases

- [ ] A user with an encrypted home directory (e.g. pamela with the correct password)
- [ ] The above case but with a mistyped password
- [ ] A user without an encrypted home directory (e.g. root with the correct password)
- [ ] The above case but with a mistyped password
- [ ] A non-existent user (e.g. blah)

## Arch

/home/<user>/.pamela_vault/
	container1
	container2
	config

## PAM part

- [ ] Be able to decrypt volume with the user password
- [ ] Determine if user close the last session

## Encryption part

- [x] Open existing container
- [x] Mount the container
- [x] Umount container
- [x] Close container
- [ ] Create container
	- [ ] With 2 profiles (newbie / paranoia)
	- [ ] Format to ext4 filesystem
- [ ] Delete container

## Compiling

### PAM related

```bash
aptitude install libpam-python
gcc -fPIC -c pam_module.c
gcc -shared -o pam_module.so pam_module.o -lpam

auth required /tmp/pam_module.so
session required /tmp/pam_module.so
```

### Crypto related
```bash
python3 setup.py
```
