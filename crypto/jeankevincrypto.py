#!/usr/bin/python3

import pycryptsetup
import logging
from systemd.journal import JournalHandler
from pathlib import Path
import hashlib
import ctypes
import os

logLevels = {
    pycryptsetup.CRYPT_LOG_DEBUG: logging.DEBUG,
    pycryptsetup.CRYPT_LOG_ERROR: logging.ERROR,
    pycryptsetup.CRYPT_LOG_NORMAL: logging.INFO,
    pycryptsetup.CRYPT_LOG_VERBOSE: logging.NOTSET
}

def mount(source, target, fs):
    ret = ctypes.CDLL('libc.so.6', use_errno=True).mount(
        ctypes.c_char_p(source.encode()), ctypes.c_char_p(target.encode()),
        ctypes.c_char_p(fs.encode()), 0, 0)
    if ret != 0:
        errno = ctypes.get_errno()
        log_to_systemd(pycryptsetup.CRYPT_LOG_ERROR,
                       "Error mounting {} ({}) on {}: {}"
                      .format(source, fs, target, os.strerror(errno)))
        return False
    log_to_systemd(pycryptsetup.CRYPT_LOG_NORMAL,
                   "Mounting {} ({}) on {} succeed"
                  .format(source, fs, target))
    return True

def umount(path):
    ret = ctypes.CDLL('libc.so.6', use_errno=True).umount(
        ctypes.c_char_p(path.encode()))
    if ret != 0:
        errno = ctypes.get_errno()
        log_to_systemd(pycryptsetup.CRYPT_LOG_ERROR,
                       "Error umounting {} : {}"
                      .format(path, os.strerror(errno)))
        return False
    log_to_systemd(pycryptsetup.CRYPT_LOG_NORMAL,
                   "Umounting {} succeed"
                  .format(path))
    return True
    return True

def log_to_systemd(level, msg="<log message is not available>"):
    logger.log(logLevels.get(level, logging.NOTSET),
               "{}".format(msg))
    return

def get_abs_path(filename):
    return str(Path(filename).resolve())

def get_sha256_hexdigest(string):
    return hashlib.sha256(string.encode()).hexdigest()

class LUKSDevice:
    """ LUKSDevice represents a LUKS device """

    def __init__(self, path):
        assert isinstance(path, str)

        try:
            self.path = get_abs_path(path)
        except Exception as e:
            log_to_systemd(pycryptsetup.CRYPT_LOG_ERROR, e)
            raise

        self.name = get_sha256_hexdigest(self.path)

        try:
            self.c = pycryptsetup.CryptSetup(
                device = self.path,
                name = self.name,
                logFunc = log_to_systemd)
        except Exception as e:
            log_to_systemd(pycryptsetup.CRYPT_LOG_ERROR, e)
            raise

        self.c.debugLevel(pycryptsetup.CRYPT_DEBUG_ALL);

        log_to_systemd(pycryptsetup.CRYPT_LOG_NORMAL,
                       "Instance correctly initialized with path: " + path)

    def open(self, passphrase):
        """ Open a LUKS device """
        if self.c.isLuks() != 0:
            log_to_systemd(pycryptsetup.CRYPT_LOG_ERROR,
                           "{} is not a LUKS device".format(self.path))
            return False

        try:
            self.c.activate(self.name, passphrase)
        except Exception as e:
            log_to_systemd(pycryptsetup.CRYPT_LOG_ERROR, e)
            return False

        if self.c.status() != pycryptsetup.CRYPT_ACTIVE:
            log_to_systemd(pycryptsetup.CRYPT_LOG_ERROR,
                          "Device {} was not activated".format(self.path))
            return False

        log_to_systemd(pycryptsetup.CRYPT_LOG_NORMAL,
                       "Device {} activated as {}".format(self.path,
                                                          self.name))
        return True

    def close(self):
        """ Close a LUKS device """
        if self.c.status() != pycryptsetup.CRYPT_ACTIVE:
            log_to_systemd(pycryptsetup.CRYPT_LOG_ERROR,
                           "Device {} is not active, can not close it".
                          format(self.path))
            return False

        try:
            self.c.deactivate()
        except Exception as e:
            log_to_systemd(pycryptsetup.CRYPT_LOG_ERROR,
                           "Device {} cant be close: {}".format(
                               self.path, e))
            return False

        log_to_systemd(pycryptsetup.CRYPT_LOG_NORMAL,
                       "Device {} correctly closed".format(self.path))
        return True

    def __del__(self):
        log_to_systemd(pycryptsetup.CRYPT_LOG_NORMAL,
                       "Device {} object cleared".format(self.path))
        del self.c

logger = logging.getLogger('jeankevincrypto')
logger.addHandler(JournalHandler())
logger.setLevel(logging.DEBUG)
