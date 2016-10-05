## Mandatory part

- [ ] Open an encrypted volume in user's home folder when user log in
	- [ ] To make a mount set userid to 0 (root) in order to mount a volume
	- [ ] Detect that the user has not mounted the directory yet
	- [ ] If a user is logged in twice, it is important that the user's home directory is not unmounted the first time the user logs out.
- [ ] When user log out, close the volume

## Bonus

- [ ] Handle a debug flag in our module (talk to syslog)
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
	config

## PAM part

- [ ] pam_conv()
- [ ] Be able to decrypt volume with the user password
- [ ] Determine if user close the last session

## Encryption part

- [ ] Check if valid LUKS header (by *hand*)
- [ ] Open existing container
- [ ] Create container
	- [ ] Specify used cipher
	- [ ] Specify key size
	- [ ] Specify hash
	- [ ] Specify iter time
	- [ ] Specify RNG
	- [ ] Ask passphrase
- [ ] Delete container

## Compile

```bash
gcc -fPIC -c pam_module.c
gcc -shared -o pam_module.so pam_module.o -lpam
```
