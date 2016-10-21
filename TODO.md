## Mandatory part

- [ ] Open an encrypted volume in user's home folder when user log in
	- [ ] To make a mount set userid to 0 (root) in order to mount a volume
	- [ ] Detect that the user has not mounted the directory yet
	- [ ] If a user is logged in twice, it is important that the user's home directory is not unmounted the first time the user logs out.
- [ ] When user log out, close the volume

## Test cases

- [ ] A user with an encrypted home directory (e.g. pamela with the correct password)
- [ ] The above case but with a mistyped password
- [ ] A user without an encrypted home directory (e.g. root with the correct password)
- [ ] The above case but with a mistyped password
- [ ] A non-existent user (e.g. blah)

## Arch

/home/<user>/.luksypam/
	container1
	container2
	config.json
	vault.db

## Tasks

- [x] Harden get user name
- [x] Harden open
- [x] Do weak open config params
- [x] Handle useUserPassword config parameter
- [ ] Check if mount dir is a is_symlink()
- [ ] logout close
- [ ] harden logout close
- [ ] Handle db creation and usage
- [/] device actions
	- [ ] resize
- [ ] Create a deb package
	- [ ] Where to put the code
	- [ ] Create hidden directory
	- [ ] Add config skel 
	- [ ] Add calling line in /etc/common-auth
