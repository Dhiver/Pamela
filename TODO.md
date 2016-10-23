## Arch

/home/<user>/.luksypam/
	container1
	container2
	config.json
	vault.db

## Tasks

- [ ] Check for duplicate container name and mount point
- [ ] Write cli_db_manage.py
	- [ ] Ncurse interface
	- [ ] If 'useUserPassword' option is set
		- [ ] Handle usage
- [ ] Change container password
- [ ] Write a pam_exec.so rapidly
- [ ] Create a deb package
	- [ ] Where to put the code
	- [ ] Create hidden directory
	- [ ] Add config skel 
	- [ ] Add calling line in /etc/common-auth
	- [ ] Add calling line in /etc/common-session
