#!/usr/bin/env python3

import sys
from getpass import getuser, getpass
import logging
from luksypam_log import logger
import LuksyPam
from SQLCipher import SQLCipher
from constants import *

def changeContainerPassword(luksypam, container):
    cur = luksypam.db.getCursor()
    cur.execute("SELECT * FROM Containers WHERE Name=?", (container.name,))
    row = cur.fetchone()
    try:
        newPassword = getpass("Enter new password for {} (Ctrl-d to cancel): "
                           .format(container.name))
    except EOFError as e:
        print()
        return
    except Exception as e:
        print("Error while entering {} password: {}"
              .format(container.name, e), file=sys.stderr)
        return
    if row is None:
        ins = (container.name, newPassword)
        cur.execute("INSERT INTO Containers (Name, Password) VALUES (?, ?)", ins)
    else:
        if container.data.init():
            container.data.changePassword(row["Password"], newPassword)
            cur.execute("UPDATE Containers SET Password=? WHERE Name=?",
                        (newPassword, row["Name"]))
            print("Password changed")

def removeContainer(container):
    if container.data.wipe():
        print("{} wiped!".format(container.name), file=sys.stderr)

username = getuser()
password = getpass("Enter {} password: ".format(username))

luksypam = LuksyPam.LuksyPam(username, password)
if not luksypam.init() or not luksypam.isLuksypamEnabled() or not luksypam.loadConfs():
    sys.exit(1)

if not luksypam.db:
    print("Can not initialize DB", file=sys.stderr)
    sys.exit(1)

for container in luksypam.containers:
    if container.config["enable"]:
        while True:
            choice = ''
            try:
                choice = input("{} - Delete (d) or change password (c) or do nothing (n) [c/d/n] ".format(container.name))
            except EOFError:
                sys.exit(1)
            if choice == 'c':
                changeContainerPassword(luksypam, container)
                break
            if choice == 'd':
                removeContainer(container)
                break
            if choice == 'n':
                break

luksypam.db.disconnect()

print("ok")
