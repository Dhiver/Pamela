import ctypes
import json
import pwd
from ctypes import *
from pprint import pprint

import jeankevincrypto
from mount_umount import *

# with open('/tmp/user.json') as data_file:
#     data = json.load(data_file)


pam = ctypes.CDLL("./libjeankevinpam.so")
# libpam = ctypes.CDLL("libpam.so")
# libpam_misc = ctypes.CDLL("libpam_misc.so")

secret_dir = ".pamela_vault"

def pam_sm_authenticate(pamh, flags, argv):
    ret = pam.authenticate(c_void_p(pamh.pamh))
    return ret;


def pam_sm_open_session(pamh, flags, argv):
    # c_pamh = c_void_p(pamh.pamh)
    # user = pam.get_user(c_pamh)
    # password = pam.get_password(c_pamh)
    # pw = pwd.getpwnam(user)
    # print("Hello {} your secret directory is {}, and password {}").format(user, pw.pw_dir, "/" + secret_dir, password)
    # ret = pam.open_session(c_void_p(pamh.pamh))
    return pamh.PAM_SUCCESS


def pam_sm_close_session(pamh, flags, argv):
    ret = pam.close_session(c_void_p(pamh.pamh))
    return ret


def pam_sm_setcred(pamh, flags, argv):
    ret = pam.setcred(c_void_p(pamh.pamh))
    return ret


def pam_sm_acct_mgmt(pamh, flags, argv):
    ret = pam.acct_mgmt(c_void_p(pamh.pamh))
    return ret


def pam_sm_chauthtok(pamh, flags, argv):
    ret = pam.chauthtok(c_void_p(pamh.pamh))
    return ret
