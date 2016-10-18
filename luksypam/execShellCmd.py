#!/usr/bin/env python3

import subprocess

def execShellCmd(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    return p.returncode, out, err
