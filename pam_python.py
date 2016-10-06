import ctypes
from ctypes import *

lib = ctypes.CDLL("/tmp/libjeankevinpam.so")


def pam_sm_authenticate(pamh, flags, argv):
    ret = lib.authenticate(c_void_p(pamh.pamh))
    return ret


def pam_sm_open_session(pamh, flags, argv):
    ret = lib.open_session(c_void_p(pamh.pamh))
    return ret


def pam_sm_close_session(pamh, flags, argv):
    ret = lib.close_session(c_void_p(pamh.pamh))
    return ret


def pam_sm_setcred(pamh, flags, argv):
    ret = lib.setcred(c_void_p(pamh.pamh))
    return ret


def pam_sm_acct_mgmt(pamh, flags, argv):
    ret = lib.acct_mgmt(c_void_p(pamh.pamh))
    return ret


def pam_sm_chauthtok(pamh, flags, argv):
    ret = lib.chauthtok(c_void_p(pamh.pamh))
    return ret
