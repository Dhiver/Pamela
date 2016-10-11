#!/usr/bin/env python3

import sys
sys.path.append("/tmp/build")

import ctypes
import json
import pwd
from ctypes import *
from pprint import pprint

import jeankevincrypto
from mount_umount import *

import os


pam = ctypes.CDLL("/tmp/build/libjeankevinpam.so")
pam.get_user.restype = ctypes.c_char_p
pam.get_password.restype = ctypes.c_char_p

secret_folder = ".pamela_vault"
config_file = "config.json"

def init_pam(secret_dir):
    print("init")
    os.mkdir(secret_dir)
    save_config({"container1": {"mountDir": "container1", "userPassword": True}}, os.path.join(secret_dir, config_file))


def load_config(filepath):
    with open(filepath) as data_file:
        return json.load(data_file)


def save_config(config, filepath):
    with open(filepath, "w") as outfile:
        json.dump(config, outfile, indent=4)


def pam_sm_authenticate(pamh, flags, argv):
    ret = pam.authenticate(c_void_p(pamh.pamh))
    return ret;


def pam_sm_open_session(pamh, flags, argv):
    c_pamh = c_void_p(pamh.pamh)
    user = pam.get_user(c_pamh)
    password = pam.get_password(c_pamh)
    pw = pwd.getpwnam(user)
    secret_dir = os.path.join(pw.pw_dir, secret_folder)
    if os.path.isdir(secret_dir) is False:
        init_pam(secret_dir)

    config = load_config(os.path.join(secret_dir, config_file))
    for key in config:
        contain = jeankevincrypto.LUKSDevice(os.path.join(secret_dir, key))
        if contain.open(password) is False:
            print('Bad Password')
        print(json.dumps(config[contain], indent=4, sort_keys=True))
    print(json.dumps(config, indent=4, sort_keys=True))
    print("Hello {} your secret directory is {}, and password {}").format(user, secret_dir, password)
    return pamh.PAM_SUCCESS


def pam_sm_close_session(pamh, flags, argv):
    # ret = pam.close_session(c_void_p(pamh.pamh))
    return pamh.PAM_SUCCESS


def pam_sm_setcred(pamh, flags, argv):
    # ret = pam.setcred(c_void_p(pamh.pamh))
    return pamh.PAM_SUCCESS


def pam_sm_acct_mgmt(pamh, flags, argv):
    # ret = pam.acct_mgmt(c_void_p(pamh.pamh))
    return pamh.PAM_SUCCESS


def pam_sm_chauthtok(pamh, flags, argv):
    # ret = pam.chauthtok(c_void_p(pamh.pamh))
    return pamh.PAM_SUCCESS
