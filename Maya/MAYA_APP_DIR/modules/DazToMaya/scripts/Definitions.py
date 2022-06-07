import os
import platform
import maya.cmds as cmds

MAYA_VERSION = int(cmds.about(v=True))

if (platform.system() == "Windows"):
    import ctypes.wintypes
    CSIDL_PERSONAL=5
    SHGFP_TYPE_CURRENT=0
    buffer = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(0, CSIDL_PERSONAL, 0, SHGFP_TYPE_CURRENT, buffer)
    HOME_DIR = buffer.value
elif (platform.system() == "Darwin"):
    HOME_DIR = os.path.expanduser("~") + "/Documents"
else:
    HOME_DIR = os.path.expanduser("~")

ROOT_DIR = os.path.join(HOME_DIR, "DAZ 3D", "Bridges", "Daz To Maya")
EXPORT_DIR = os.path.join(ROOT_DIR, "Exports")
