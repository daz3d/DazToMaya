import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds
try:
    import maya.mel as mel
    print("MEL loaded successfully")
except:
    print("error trying to load MEL")

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

    # Delete unused nodes
    mel.eval('MLdeleteUnused()')

    # Save Textures
    root_path = os.path.dirname(file_path)
    images_foldername = os.path.basename(file_path) + "_images"
    images_folderpath = root_path + "/" + images_foldername
    if not os.path.exists(images_folderpath):
        try:
            os.makedirs(images_folderpath)
        except Exception as e:
            _add_to_log("Unable to create image folder: " + images_folderpath)
            _add_to_log(str(e))
            raise e
    texture_file_nodes = cmds.ls(type='file')
    for file_node in texture_file_nodes:
        _add_to_log("DEBUG: processing file_node: " + file_node)
        image_path = cmds.getAttr(file_node + '.fileTextureName')
        # save file properties
        colorSpace = cmds.getAttr(file_node + '.colorSpace')
        colorGain = cmds.setAttr(file_node + '.colorGain')
        alphaGain = cmds.getAttr(file_node + '.alphaGain')
        alphaIsLuminance = cmds.getAttr(file_node + '.alphaIsLuminance')
        invert = cmds.getAttr(file_node + '.invert')
        just_file_name = os.path.basename(image_path)
        out_file_name = images_folderpath + "/" + str(just_file_name)
        if image_path != out_file_name:
            from shutil import copyfile
            copyfile(image_path, out_file_name)
            cmds.setAttr(file_node + '.fileTextureName', 
                         images_foldername + "/" + str(just_file_name),
                         type='string')
            # restore file properties
            if colorSpace: cmds.setAttr(file_node + '.colorSpace', colorSpace, type='string')
            if colorGain: cmds.setAttr(file_node + '.colorGain', float(colorGain))
            if alphaGain: cmds.setAttr(file_node + '.alphaGain', float(alphaGain))
            if alphaIsLuminance: cmds.setAttr(file_node + '.alphaIsLuminance', bool(alphaIsLuminance))
            if invert: cmds.setAttr(file_node + '.invert', bool(invert))

    # Save Maya File
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
