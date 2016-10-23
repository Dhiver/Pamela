#!/usr/bin/env python3

import pycryptsetup
from pycryptsetup import CRYPT_DEBUG_ALL, CRYPT_DEBUG_NONE
import logging
from pathlib import Path
from hashlib import sha256
import os
from luksypam_log import logger
from constants import *

logLevels = {
    pycryptsetup.CRYPT_LOG_DEBUG: logging.DEBUG,
    pycryptsetup.CRYPT_LOG_ERROR: logging.ERROR,
    pycryptsetup.CRYPT_LOG_NORMAL: logging.INFO,
    pycryptsetup.CRYPT_LOG_VERBOSE: logging.NOTSET
}

def log_to_systemd(level, msg="<log message is not available>"):
    logger.log(logLevels.get(level, logging.NOTSET),
               "{}".format(msg))
    return

def generatePseudoRandomFileGarbage(path, size):
    try:
        with open(path, "wb") as f:
            f.write(os.urandom(size * 1024**2))
    except Exception as e:
        logger.log(logging.ERROR,
                   "Error generating garbage file {}: {}"
                   .format(path, e))
        return False
    return True

class LUKSDevice:
    """ LUKSDevice represents a LUKS device """

    def __init__(self, path):
        assert isinstance(path, str)
        self.path = path
        self.c = None
        self.name = ""

    def init(self):
        self.name = sha256(self.path.encode()).hexdigest()

        try:
            self.path = str(Path(self.path).resolve())
        except Exception as e:
            log_to_systemd(pycryptsetup.CRYPT_LOG_ERROR,
                           "Can't get absolute path for '{}': {}"
                           .format(self.path, e))
            return False

        try:
            self.c = pycryptsetup.CryptSetup(
                device = self.path,
                name = self.name,
                logFunc = log_to_systemd)
        except Exception as e:
            log_to_systemd(pycryptsetup.CRYPT_LOG_ERROR,
                           "Device {} with path {} error: {}"
                           .format(self.path, self.name, e))
            return False

        self.c.debugLevel(CRYPT_DEBUG_ALL if DEBUG_MSG_ENABLE else CRYPT_DEBUG_NONE)

        log_to_systemd(pycryptsetup.CRYPT_LOG_DEBUG,
                       "Instance correctly initialized with path: {}"
                       .format(self.path))
        return True

    def isOpen(self):
        status = self.c.status()
        return status == pycryptsetup.CRYPT_ACTIVE or status == pycryptsetup.CRYPT_BUSY

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

        if not self.isOpen():
            log_to_systemd(pycryptsetup.CRYPT_LOG_ERROR,
                           "Device {} was not activated".format(self.path))
            return False

        log_to_systemd(pycryptsetup.CRYPT_LOG_DEBUG,
                       "Device {} activated as {}".format(self.path,
                                                          self.name))
        return True

    def close(self):
        """ Close a LUKS device """
        if not self.isOpen():
            log_to_systemd(pycryptsetup.CRYPT_LOG_ERROR,
                           "Device {} is not active, can not close it".
                           format(self.path))
            return False

        try:
            self.c.deactivate()
        except Exception as e:
            log_to_systemd(pycryptsetup.CRYPT_LOG_ERROR,
                           "Device {} can't be close: {}".format(
                               self.path, e))
            return False

        log_to_systemd(pycryptsetup.CRYPT_LOG_DEBUG,
                       "Device {} correctly closed".format(self.path))
        return True

    def wipe(self):
        """ Wipe a LUKS device by overwriting volume header
        Implement section 5.4 of https://gitlab.com/cryptsetup/cryptsetup/wikis/FrequentlyAskedQuestions"""
        if self.isOpen():
            log_to_systemd(pycryptsetup.CRYPT_LOG_ERROR,
                           "Close the device {} before wiping".
                           format(self.path))
            return False

        try:
            size = os.path.getsize(self.path)
        except Exception as e:
            log_to_systemd(pycryptsetup.CRYPT_LOG_ERROR,
                           "Error getting file ({}) size: {}".format(
                               self.path, e))
            return False

        try:
            with open(self.path, 'r+b') as f:
                f.seek(0)
                if size > 10 * 1024**2:
                    size = 10 * 1024**2
                f.write(b'0' * size)
                f.flush()
        except Exception as e:
            log_to_systemd(pycryptsetup.CRYPT_LOG_ERROR,
                           "Error overwritting luks header for {}: {}".format(
                               self.path, e))
            return False

        log_to_systemd(pycryptsetup.CRYPT_LOG_DEBUG,
                       "Device {} wiped".format(self.path))

        try:
            os.remove(self.path)
        except Exception as e:
            log_to_systemd(pycryptsetup.CRYPT_LOG_ERROR,
                           "Error deleting file {}: {}".format(
                               self.path, e))
            return False

        log_to_systemd(pycryptsetup.CRYPT_LOG_DEBUG,
                       "Device {} removed".format(self.path))

        return True

    def createDevice(self, size, passphrase, weak=False):
        assert isinstance(size, int)
        assert isinstance(passphrase, str)
        assert isinstance(weak, bool)
        if not generatePseudoRandomFileGarbage(self.path, size):
            return False
        if not self.init():
            return False
        try:
            self.c.iterationTime(WEAK_ITER_TIME if weak else NORMAL_ITER_TIME)
            self.c.luksFormat(cipher="aes",
                             cipherMode="xts-plain64",
                             keysize=WEAK_KEY_SIZE if weak else NORMAL_KEY_SIZE,
                             hashMode=WEAK_HASH_MODE if weak else NORMAL_HASH_MODE,
                             useRandom=False if weak else True)
            self.c.addKeyByVolumeKey(newPassphrase = passphrase)
        except Exception as e:
            log_to_systemd(pycryptsetup.CRYPT_LOG_ERROR,
                           "Error creating device {}: {}"
                           .format(self.path, e))
            return False
        return True

    def __del__(self):
        del self.c
