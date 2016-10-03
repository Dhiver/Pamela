## Partie obligatoire

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

## Notes

### Create shared library with go code

go build -o libpamela.so -buildmode=c-shared pamela.go
