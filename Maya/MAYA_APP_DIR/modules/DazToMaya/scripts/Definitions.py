import os
import platform
import maya.cmds as cmds

MAYA_VERSION = int(cmds.about(v=True))

if (platform.system() == "Windows"):
    try:
        import ctypes.wintypes
        csidl=5 # My Documents Folder (CSIDL_PERSONAL)
        access_token=None # Current User
        flags=0 # Current Value (SHGFP_TYPE_CURRENT)
        buffer = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        result = ctypes.windll.shell32.SHGetFolderPathW(0, csidl, access_token, flags, buffer)
        if result != 0:
            if result < 0:
                result += 2**32
            print("ERROR: SHGetFolderPathW() returned error code=[" + str(hex(result)) + "]")
            del buffer
            raise Exception()
        HOME_DIR = buffer.value
    except:
        HOME_DIR = os.path.expanduser("~").replace("\\","/") + "/Documents"
        print("Unable to query the correct Documents path for Windows, failing back to user folder=\"" + str(HOME_DIR) + "\".")
elif (platform.system() == "Darwin"):
    HOME_DIR = os.path.expanduser("~") + "/Documents"
else:
    HOME_DIR = os.path.expanduser("~")

ROOT_DIR = os.path.join(HOME_DIR, "DAZ 3D", "Bridges", "Daz To Maya")
EXPORT_DIR = os.path.join(ROOT_DIR, "Exports").replace("\\","/")
