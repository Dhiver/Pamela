#!/usr/bin/python3

import pycryptsetup
import logging
from systemd.journal import JournalHandler
from pathlib import Path
import hashlib

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
            del self.c
            return False

        if self.c.status != pycryptsetup.CRYPT_ACTIVE:
            log_to_systemd(pycryptsetup.CRYPT_LOG_ERROR,
                          "Device {} was not activated".format(self.path))
            del self.c
            return False

        log_to_systemd(pycryptsetup.CRYPT_LOG_NORMAL,
                       "Device {} activated as {}".format(self.path,
                                                          self.name))
        return True

logger = logging.getLogger('jeankevincrypto')
logger.addHandler(JournalHandler())
logger.setLevel(logging.DEBUG)
