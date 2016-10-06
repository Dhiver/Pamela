#include <security/pam_modules.h>
#include <security/pam_misc.h>
#include <security/pam_ext.h>
#include <security/pam_appl.h>
#include <sys/types.h>
#include <pwd.h>
#include <stdio.h>



#define UNUSED  __attribute__((unused))
#define SECRET_DIR ".pamela_vault"
#define PASSWORD_ENV "volume_password"

PAM_EXTERN int
pam_sm_authenticate(UNUSED pam_handle_t *pamh, UNUSED int flags, UNUSED int argc, UNUSED const char **argv) {
    char *password = NULL;

    printf("pam_sm_authenticate\n");
    if (pam_get_item(pamh, PAM_AUTHTOK, (void *)&password) != PAM_SUCCESS) {
        return PAM_IGNORE;
    }
    if (pam_misc_setenv(pamh, PASSWORD_ENV, password, 1) != PAM_SUCCESS) {
        return PAM_IGNORE;
    }
    return PAM_SUCCESS;
}

PAM_EXTERN int
pam_sm_open_session(UNUSED pam_handle_t *pamh, UNUSED int flags, UNUSED int argc, UNUSED const char **argv) {
    const char      *user;
    const char      *password;
    struct passwd   *pwd;

//  get user
    pam_get_user(pamh, &user, NULL);

//  get pwd
    pwd = getpwnam(user);

//  get password
    password = pam_getenv(pamh, PASSWORD_ENV);

//   check password
    //TODO check if password == volume_password
//    if (password == NULL) {
        pam_get_authtok(pamh, PAM_AUTHTOK, (void*)&password, "Password for unlock volume: ");
        //TODO check if password == volume_password
//    }


    printf("Hello %s your secret directory is %s%s, and password %s\n", user, pwd->pw_dir, "/"SECRET_DIR, password);
    return (PAM_SUCCESS);
}

PAM_EXTERN int
pam_sm_close_session(UNUSED pam_handle_t *pamh, UNUSED int flags, UNUSED int argc, UNUSED const char **argv) {
    //TODO check if last user
    return (PAM_SUCCESS);
}

PAM_EXTERN int
pam_sm_setcred(UNUSED pam_handle_t *pamh, UNUSED int flags, UNUSED int argc, UNUSED const char **argv) {
    printf("pam_sm_setcred\n");
    return (PAM_SUCCESS);
}

PAM_EXTERN int
pam_sm_acct_mgmt(UNUSED pam_handle_t *pamh, UNUSED int flags, UNUSED int argc, UNUSED const char **argv) {
    printf("pam_sm_acct_mgmt\n");
    return (PAM_SUCCESS);
}

PAM_EXTERN int
pam_sm_chauthtok(UNUSED pam_handle_t *pamh, UNUSED int flags, UNUSED int argc, UNUSED const char **argv) {
    printf("pam_sm_chauthtok\n");
    return (PAM_SUCCESS);
}