#!/usr/bin/env python3

import os
import sys
import logging
from luksypam_log import logger
import LuksyPam

password = input()[:-1]

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

if action != "auth":
    sys.exit(0)

inst = LuksyPam.LuksyPam(username, password)

if not inst.init() or not inst.isLuksypamEnabled() or not inst.loadConfs():
    sys.exit(0)

if not inst.createContainers() or not inst.initContainers():
    sys.exit(0)

if not inst.openContainers() or not inst.mountContainers():
    sys.exit(0)

logger.log(logging.INFO, "auth OK")
sys.exit(0)
