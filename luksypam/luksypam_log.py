#!/usr/bin/env python3

import logging
from systemd.journal import JournalHandler

__all__ = ['logger']

logger = logging.getLogger(__name__)
logger.addHandler(JournalHandler())
logger.setLevel(logging.DEBUG)
