import sys

import maya.cmds as cmds

import d2m

if int(cmds.about(v=True)) > 2020:
    import importlib
    importlib.reload(d2m)
else:
    reload(d2m)

def run():
    print("Daz to Maya, run() method")
    d2m.initialize()