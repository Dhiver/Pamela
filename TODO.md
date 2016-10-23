## Arch

/home/<user>/.luksypam/
	container1
	container2
	config.json
	vault.db

## Tasks

- [ ] Handle 'useUserPassword' option
	- [ ] If bad password, ask 3 times more
- [ ] Write a pam_exec.so rapidly
- [ ] Handle db creation and usage
- [ ] Create a deb package
	- [ ] Where to put the code
	- [ ] Create hidden directory
	- [ ] Add config skel 
	- [ ] Add calling line in /etc/common-auth
	- [ ] Add calling line in /etc/common-session
