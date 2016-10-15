#import sys
#sys.path.append("/tmp/build/")

import pycryptsetup
import logging
from systemd.journal import JournalHandler
from utils import get_abs_path, get_sha256_hexdigest
import os

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
        self.path = None
        self.c = None
        assert isinstance(path, basestring)

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

        self.c.debugLevel(pycryptsetup.CRYPT_DEBUG_NONE);

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

    def __del__(self):
        log_to_systemd(pycryptsetup.CRYPT_LOG_NORMAL,
                       "Device {} object cleared".format(self.path))
        del self.c

logger = logging.getLogger('jeankevincrypto')
logger.addHandler(JournalHandler())
logger.setLevel(logging.DEBUG)
