#!/usr/bin/env python3

import pycryptsetup
import logging
from systemd.journal import JournalHandler
from pathlib import Path
from hashlib import sha256
import os

logger = logging.getLogger(__name__)
logger.addHandler(JournalHandler())
logger.setLevel(logging.INFO)

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
            log_to_systemd(pycryptsetup.CRYPT_LOG_ERROR, e)
            return False

        self.c.debugLevel(pycryptsetup.CRYPT_DEBUG_NONE);

        log_to_systemd(pycryptsetup.CRYPT_LOG_NORMAL,
                       "Instance correctly initialized with path: {}"
                       .format(self.path))
        return True

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

    def wipe(self):
        """ Wipe a LUKS device by overwriting volume header
        Implement section 5.4 of https://gitlab.com/cryptsetup/cryptsetup/wikis/FrequentlyAskedQuestions"""
        if self.c.status() != pycryptsetup.CRYPT_INACTIVE:
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

        log_to_systemd(pycryptsetup.CRYPT_LOG_NORMAL,
                       "Device {} wiped".format(self.path))

        try:
            os.remove(self.path)
        except Exception as e:
            log_to_systemd(pycryptsetup.CRYPT_LOG_ERROR,
                           "Error deleting file {}: {}".format(
                               self.path, e))
            return False

        log_to_systemd(pycryptsetup.CRYPT_LOG_NORMAL,
                       "Device {} removed".format(self.path))

        return True

    def createDevice(self, passphrase, profile="normal"):
        assert isinstance(passphrase, str)
        assert isinstance(profile, str)
        pass

    def resize(self, newSize):
        assert isinstance(newSize, int)
        pass

    def __del__(self):
        log_to_systemd(pycryptsetup.CRYPT_LOG_NORMAL,
                       "Device {} object cleared".format(self.path))
        del self.c
