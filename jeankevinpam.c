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

const char  *get_password(pam_handle_t *pamh) {
    return pam_getenv(pamh, PASSWORD_ENV);
}

const char  *get_user(pam_handle_t *pamh) {
    const char      *user;

    pam_get_user(pamh, &user, NULL);
    return user;
}

int authenticate(pam_handle_t *pamh) {
    char *password = NULL;

    // printf("authenticate\n");
    if (pam_get_item(pamh, PAM_AUTHTOK, (void *)&password) != PAM_SUCCESS) {
        return PAM_IGNORE;
    }
    if (pam_misc_setenv(pamh, PASSWORD_ENV, password, 1) != PAM_SUCCESS) {
        return PAM_IGNORE;
    }
    return PAM_SUCCESS;
}

//int open_session(pam_handle_t *pamh) {
//    const char      *user;
//    const char      *password;
//    struct passwd   *pwd;
//
////  get user
//    pam_get_user(pamh, &user, NULL);
//
////  get pwd
//    pwd = getpwnam(user);
//
////  get password
//    password = pam_getenv(pamh, PASSWORD_ENV);
//
////   check password
//    //TODO check if password == volume_password
////    if (password == NULL) {
//        // pam_get_authtok(pamh, PAM_AUTHTOK, (void*)&password, "Password for unlock volume: ");
//        //TODO check if password == volume_password
////    }
//
//
//    printf("Hello %s your secret directory is %s%s, and password %s\n", user, pwd->pw_dir, "/"SECRET_DIR, password);
//    return (PAM_SUCCESS);
//}
//
//int close_session(UNUSED pam_handle_t *pamh) {
//    //TODO check if last user
//    return (PAM_SUCCESS);
//}
//
//int setcred(UNUSED pam_handle_t *pamh) {
//    printf("setcred\n");
//    return (PAM_SUCCESS);
//}
//
//int acct_mgmt(UNUSED pam_handle_t *pamh) {
//    printf("acct_mgmt\n");
//    return (PAM_SUCCESS);
//}
//
//int chauthtok(UNUSED pam_handle_t *pamh) {
//    printf("chauthtok\n");
//    return (PAM_SUCCESS);
//}
