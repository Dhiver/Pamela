#!/usr/bin/env python3

import os
import sys
import psutil
import logging
from luksypam_log import logger
import LuksyPam

password = input()[:-1]

users = list()
for user in psutil.users():
    users.append(user.name)

logger.log(logging.DEBUG, "Env : {}".format(os.environ))
logger.log(logging.DEBUG, "Logged users : {}".format(users))

username = str()
if "PAM_USER" in os.environ:
    username = os.environ["PAM_USER"]
    if not username:
        logger.log(logging.ERROR, "Username empty")
        sys.exit(0)
else:
    logger.log(logging.ERROR, "Can't get username")
    sys.exit(0)

inst = LuksyPam.LuksyPam(username, password)

if not inst.init() or not inst.isLuksypamEnabled() or not inst.loadConfs() or not inst.initContainers() or not inst.openContainers() or not inst.mountContainers():
    sys.exit(0)

logger.log(logging.INFO, "OK")
sys.exit(0)
