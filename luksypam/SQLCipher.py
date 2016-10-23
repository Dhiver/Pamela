#!/usr/bin/env python3

import logging
from pysqlcipher3 import dbapi2 as sqlite
from luksypam_log import logger

class SQLCipher:
    def __init__(self, path):
        self.path = path
        self.conn = None
        self.cursor = None

    def connect(self, key):
        try:
            self.conn = sqlite.connect(self.path)
            self.conn.row_factory = sqlite.Row
        except Exception as e:
            logger.log(logging.ERROR, "Connecting to database error: {}"
                       .format(e))
            self.cursor = None
            return False
        with self.conn:
            self.cursor = self.conn.cursor()
            self.cursor.execute("PRAGMA key='{}'".format(key))
        return True

    def getCursor(self):
        return self.cursor

    def disconnect(self):
        try:
            self.conn.commit()
            self.cursor.close()
        except Exception as e:
            logger.log(logging.ERROR, "Disconnecting from database error: {}"
                       .format(e))
            return False
        return True
