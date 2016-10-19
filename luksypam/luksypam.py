#!/usr/bin/env python3

import sys
import os
import logging
import ParseConfig
import LUKSDevice
from mount_umount import mount, umount
from execShellCmd import execShellCmd

password = input()[:-1]

from luksypam_log import logger

USER_HOME="/home/{}/".format(os.environ["PAM_USER"])
USER_ROOT_FOLDER=USER_HOME + ".luksypam/"
USER_CONFIG_FILE=USER_ROOT_FOLDER + "config.json"
FORMAT_DRIVE_IN="ext4"

# Check if luksypam is activated

if not os.path.isdir(USER_ROOT_FOLDER[:-1]) or not os.path.isfile(USER_CONFIG_FILE):
    logger.log(logging.INFO, "not activated, cant find {} neither {}".format(USER_ROOT_FOLDER[:-1], USER_CONFIG_FILE))
    sys.exit(0)

config = ParseConfig.ParseConfig(USER_CONFIG_FILE)

if not config.parse() or config.isEmpty() or not config.isValid():
    sys.exit(0)

logger.log(logging.INFO, "Config file for user {} found and valid".format(os.environ["PAM_USER"]))
infos = config.getContent()

for container in infos:
    created = False
    logger.log(logging.DEBUG, "Container {} infos: {}".format(container, infos[container]))
    if not infos[container]["enable"]:
        logger.log(logging.INFO, "Container {} not enabled, nothing to be done"
                   .format(container))
        continue
    currentContainerPath = USER_ROOT_FOLDER + container
    d = LUKSDevice.LUKSDevice(currentContainerPath)
    if not os.path.isfile(currentContainerPath):
        logger.log(logging.INFO, "Container {} does not exist".format(container))
        # create volume
        if not d.createDevice(infos[container]["sizeInMB"], password):
            logger.log(logging.INFO, "Container {} can not create".format(container))
            sys.exit(0)
        logger.log(logging.INFO,
                   "Container {} created with size {}"
                   .format(container, infos[container]["sizeInMB"]))
        created = True
    if not d.init():
        logger.log(logging.INFO, "Container {} can not init".format(container))
        sys.exit(0)
    # Open volume
    if not d.isOpen():
        logger.log(logging.INFO, "Container {} is not open".format(container))
        if not d.open(password):
            logger.log(logging.INFO, "Container {} can not open".format(container))
            sys.exit(0)
    logger.log(logging.INFO, "Container {} is open".format(container))
    deviceInfos = d.c.info()
    logger.log(logging.DEBUG, "Container {} infos: {}".format(container, deviceInfos))
    currentDevicePath = deviceInfos["dir"] + "/" + deviceInfos["name"]
    # if new volume, format
    if created:
        logger.log(logging.INFO, "Container {} formating".format(container))
        ret = execShellCmd("mkfs.{} {}".format(FORMAT_DRIVE_IN, currentDevicePath))
        if ret[0] != 0:
            logger.log(logging.ERROR, "Error formating device: {}".format(ret[2]))
            sys.exit(0)
    # Mount volume
    currentMountPath = USER_HOME + infos[container]["mountDir"]
    if not os.path.isdir(currentMountPath):
        try:
            os.makedirs(currentMountPath)
        except Exception as e:
            logger.log(logging.ERROR,
                       "Error creating folder {}: {}"
                       .format(currentMountPath, e))
            sys.exit(0)
        logger.log(logging.INFO, "Mount destination folder created: {}".format(currentMountPath))

    if not os.path.ismount(currentMountPath):
        logger.log(logging.INFO, "Container {} not mounted".format(container))
        ret = mount(currentDevicePath, currentMountPath, FORMAT_DRIVE_IN)
        if not ret[0]:
            logger.log(logging.ERROR,
                       "Error mounting {} on {}: {}"
                       .format(currentDevicePath, currentMountPath, ret[1]))
        logger.log(logging.INFO, "Container {} mounted".format(container))

logger.log(logging.INFO, "OK")
sys.exit(0)
