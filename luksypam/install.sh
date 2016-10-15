#!/bin/sh

readonly HIDDEN_DIR=".luksypam"
readonly CONFIG_FILE_NAME="config.json"

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# Add Skel for new users
mkdir /etc/skel/$HIDDEN_DIR
mv $CONFIG_FILE_NAME.skel /etc/skel/$HIDDEN_DIR/$CONFIG_FILE_NAME
