#!/usr/bin/env python3

import logging
from systemd.journal import JournalHandler
import simplejson as json

logger = logging.getLogger(__name__)
logger.addHandler(JournalHandler())
logger.setLevel(logging.INFO)

MANDATORY_ENTRIES = [('mount', bool),
                     ('mountDir', str),
                     ('useUserPassword', bool),
                     ('savePass', bool),
                     ('weak', bool),
                     ('sizeInMB', int)]

DEFAULT_MIN_CONTAINER_SIZE = 8

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
        if self.data:
            return False if len(self.data) != 0 else True
        return True

    def isValid(self):
        if not self.data:
            return False
        for container in self.data:
            if '../' in container or '/..' in container:
                logger.log(logging.ERROR,
                           "Error: container name '{}' path must not contains '..'"
                           .format(container))
                return False
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
                if key[0] == 'mountDir':
                    if not self.data[container][key[0]]:
                        logger.log(logging.ERROR,
                                   "Error in {} config, '{}' is empty"
                                   .format(container, key[0]))
                        return False
                    if '../' in self.data[container][key[0]] or '/..' in self.data[container][key[0]]:
                        logger.log(logging.ERROR,
                                   "Error in {} config, '{}' path must not contains '..'"
                                   .format(container, key[0]))
                        return False
                if key[0] == 'sizeInMB':
                    if self.data[container][key[0]] < DEFAULT_MIN_CONTAINER_SIZE:
                        logger.log(logging.ERROR,
                                   "Error in {} config, '{}' size must but at least {}"
                                   .format(container, key[0], DEFAULT_MIN_CONTAINER_SIZE))
                        return False
        return True

    def getContent(self):
        return self.data
