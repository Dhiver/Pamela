#!/usr/bin/env python3

import logging
from systemd.journal import JournalHandler
import simplejson as json

logger = logging.getLogger('ParseConfig')
logger.addHandler(JournalHandler())
logger.setLevel(logging.INFO)

MANDATORY_ENTRIES = [('mount', bool),
                     ('mountDir', str),
                     ('useUserPassword', bool),
                     ('savePass', bool),
                     ('createProfile', str),
                     ('sizeInMB', int)]

class ParseConfig:
    def __init__(self, path):
        assert isinstance(path, str)
        self.path = path
        self.data = None

    def parse(self):
        try:
            with open(self.path) as confFile:
                self.data = json.load(confFile)
        except Exception as e:
            logger.log(logging.ERROR, "Error parsing JSON file {}: {}".format(
                self.path, e))
            return False
        return True

    def isEmpty(self):
        return False if len(self.data) != 0 else True

    def isValid(self):
        for container in self.data:
            for key in MANDATORY_ENTRIES:
                if not key[0] in self.data[container]:
                    logger.log(logging.ERROR,
                               "Error: can't find key '{}' in {} config"
                               .format(key[0], container))
                    return False
                if not isinstance(self.data[container][key[0]], key[1]):
                    logger.log(logging.ERROR,
                               "Error in {} config, '{}' must be of type {}"
                               .format(container, key[0], key[1].__name__))
                    return False
        return True

    def getContent(self):
        return self.data
