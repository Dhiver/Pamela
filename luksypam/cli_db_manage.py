#!/usr/bin/env python3

import sys
from getpass import getuser, getpass
import logging
from luksypam_log import logger
import LuksyPam
from SQLCipher import SQLCipher
from constants import *

username = getuser()
password = getpass("Enter {} password: ".format(username))

luksypam = LuksyPam.LuksyPam(username, password)
if not luksypam.init() or not luksypam.isLuksypamEnabled() or not luksypam.loadConfs():
    sys.exit(1)

if not luksypam.db:
    print("Can not initialize DB", file=sys.stderr)
    sys.exit(1)

cur = luksypam.db.getCursor()

for container in luksypam.containers:
    if container.config["enable"] and not container.config["useUserPassword"]:
        cur.execute("SELECT * FROM Containers WHERE Name=?", (container.name,))
        row = cur.fetchone()
        try:
            password = getpass("Enter new password for {} (Ctrl-d to cancel): "
                               .format(container.name))
        except EOFError as e:
            print()
            continue
        except Exception as e:
            print("Error while entering {} password: {}"
                  .format(container.name, e), file=sys.stderr)
            continue
        if row is None:
            ins = (container.name, password)
            cur.execute("INSERT INTO Containers (Name, Password) VALUES (?, ?)", ins)
        else:
            if row["Name"] == container.name:
                cur.execute("UPDATE Containers SET Password=? WHERE Name=?", (password, row["Name"]))

luksypam.db.disconnect()

print("ok")
