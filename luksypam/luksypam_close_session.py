#!/usr/bin/env python3

import os
import sys
import psutil
import logging
from luksypam_log import logger
import LuksyPam

MANDATORY_ENV_VARS = ['PAM_USER', 'PAM_TYPE']

for key in MANDATORY_ENV_VARS:
    if not key in os.environ:
        logger.log(logging.ERROR, "Env var {} is missing".format(key))
        sys.exit(0)
    if not os.environ[key]:
        logger.log(logging.ERROR, "Env var '{}' is empty".format(key))
        sys.exit(0)

username = os.environ["PAM_USER"]
action = os.environ["PAM_TYPE"]

if action != "close_session":
    sys.exit(0)

users = list()
for user in psutil.users():
    users.append(user.name)
logger.log(logging.DEBUG, "Logged users : {}".format(users))
if users.count(username) > 1:
    sys.exit(0)

inst = LuksyPam.LuksyPam(username)

if not inst.init() or not inst.isLuksypamEnabled() or not inst.loadConfs():
    sys.exit(0)

inst.initContainers()
inst.umountContainers()
inst.closeContainers()

logger.log(logging.INFO, "close_session OK")
sys.exit(0)
