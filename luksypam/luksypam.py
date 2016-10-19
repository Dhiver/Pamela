#!/usr/bin/env python3

import os
import sys
import psutil
import logging
from luksypam_log import logger
import LuksyPam

password = input()[:-1]

#users = list()
#for user in psutil.users():
#    users.append(user.name)
#logger.log(logging.DEBUG, "Logged users : {}".format(users))

logger.log(logging.DEBUG, "Env : {}".format(os.environ))

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

inst = LuksyPam.LuksyPam(username, password)

if not inst.init() or not inst.isLuksypamEnabled() or not inst.loadConfs() or not inst.initContainers() or not inst.openContainers() or not inst.mountContainers():
    sys.exit(0)

logger.log(logging.INFO, "OK")
sys.exit(0)
