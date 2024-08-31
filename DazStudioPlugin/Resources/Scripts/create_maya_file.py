import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds
try:
    import maya.mel as mel
    print("PyMEL loaded successfully")
except:
    print("error trying to load PyMEL")

import sys
import os
maya_modules_path = os.path.expanduser("~/maya/modules")
daz_to_maya_path = os.path.join(maya_modules_path, "DazToMaya").replace("\\", "/")

from pathlib import Path
script_dir = str(Path(__file__).parent.absolute())

try:
    import DazToMaya
    print("DazToMaya loaded successfully")
except:
    sys.path.append(maya_modules_path)
    try:
        import DazToMaya
        print("DazToMaya loaded successfully")
    except:
        print("error trying to load DazToMaya")



TEXTURE_ATLAS_SIZE_DEFAULT = 1024

g_logfile = ""

def _print_usage():
    print("\nUSAGE: mayapy.exe create_maya_file.py <fbx file>\n")

def _add_to_log(message):
    if (g_logfile == ""):
        logfile = script_dir + "/create_blend.log"
    else:
        logfile = g_logfile

    print(str(message))
    with open(logfile, "a") as file:
        file.write(str(message) + "\n")

def _main(argv):
    # try:
    #     line = str(argv[-1])
    # except:
    #     _print_usage()
    #     return

    # try:
    #     start, stop = re.search("#([0-9]*)\.", line).span(0)
    #     token_id = int(line[start+1:stop-1])
    #     print(f"DEBUG: token_id={token_id}")
    # except:
    #     print(f"ERROR: unable to parse token_id from '{line}'")
    #     token_id = 0

    DazToMaya.d2m.initialize()
    DazToMaya.d2m.auto_import_daz()

    file_path = ""
    dtu_dict = DazToMaya.d2m.global_current_dtu.get_dtu_dict()
    if "Output Maya Filepath" in dtu_dict:
        file_path = dtu_dict["Output Maya Filepath"]

    cmds.file(rename=file_path)
    if ".ma" in file_path:
        cmds.file(save=True, type="mayaAscii")
    else:
        cmds.file(save=True, type="mayaBinary")

    print("Done.")

# Execute main()
if __name__=='__main__':
    print("Starting script...")
    _add_to_log("Starting script... DEBUG: sys.argv=" + str(sys.argv))
    _main(sys.argv[4:])
    print("script completed.")
    exit(0)