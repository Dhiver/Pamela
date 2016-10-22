#!/usr/bin/env python3

import logging
from systemd.journal import JournalHandler
from constants import *

__all__ = ['logger']

logger = logging.getLogger(__name__)
logger.addHandler(JournalHandler())
logger.setLevel(logging.DEBUG if DEBUG_MSG_ENABLE else logging.INFO)
