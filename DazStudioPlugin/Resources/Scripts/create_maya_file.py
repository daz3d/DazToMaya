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
import tempfile
import shutil
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
    with open(logfile, "a", encoding="utf-8") as file:
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
    generate_final_fbx = False
    shader_target = None
    dtu_dict = DazToMaya.d2m.global_current_dtu.get_dtu_dict()
    if "Output Maya Filepath" in dtu_dict:
        file_path = dtu_dict["Output Maya Filepath"]
    try:
        generate_final_fbx = dtu_dict["Generate Final Fbx"]
        shader_target = dtu_dict["Shader Target"]
    except Exception as e:
        _add_to_log("ERROR while querying values from dtu_dict")
        _add_to_log(str(e))

    if shader_target:
        import dazmaterials as dzm
        if shader_target == "arnold":
            _add_to_log("DEBUG: converting to arnold")
            dzm.DazMaterials(False).convert_to_arnold()
        elif shader_target == "standard":
            _add_to_log("DEBUG: converting to standard")
            dzm.DazMaterials(False).convert_to_standard_surface()
        elif shader_target == "stingray":
            _add_to_log("DEBUG: converting to stingray")
            dzm.DazMaterials(False).convert_to_stingray_pbs()         

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
        if image_path and image_path != out_file_name:
            from shutil import copyfile
            _add_to_log("DEBUG: copying file: " + image_path + " to " + out_file_name)
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
    try:
        cmds.file(rename=file_path)
        if ".ma" in file_path:
            cmds.file(save=True, type="mayaAscii")
        else:
            cmds.file(save=True, type="mayaBinary")
        _add_to_log("Saved file: " + file_path)
    except RuntimeError as e:
        _add_to_log("ERROR while saving file: " + file_path + " " + str(e))
        temp_folder = tempfile.gettempdir().replace("\\", "/")
        temp_file_name = os.path.basename(file_path)
        temp_file_path = temp_folder + "/" + temp_file_name
        _add_to_log("Attempting to save to temp folder: " + temp_file_path)
        cmds.file(rename=temp_file_path)
        if ".ma" in file_path:
            cmds.file(save=True, type="mayaAscii")
        else:
            cmds.file(save=True, type="mayaBinary")
        _add_to_log("Moving temp file to: " + file_path)
        shutil.move(temp_file_path, file_path)

    if generate_final_fbx:
        # Generate FBX
        fbx_file_path = file_path.replace(".ma", ".fbx").replace(".mb", ".fbx")
        _add_to_log("DEBUG: generate_final_fbx: exporting to " + fbx_file_path)
        mel.eval("FBXExportAxisConversionMethod none;")
        mel.eval("FBXExportSmoothMesh -v false;")
        mel.eval("FBXExportInAscii -v false;")
        mel.eval("FBXExportScaleFactor 1.0;")
        mel.eval("FBXExportUpAxis y;")
        mel.eval("FBXExportInstances -v true;")
        mel.eval("FBXExportEmbeddedTextures -v true;")
        # file -force -options "" -type "FBX export" -pr -ea "C:/Users/dbui2/Documents/__Ultra_Tests/maya-phong.fbx";
        cmds.file(fbx_file_path, force=True, options="", type="FBX export", pr=True, exportAll=True)

    print("Done.")

# Execute main()
if __name__=='__main__':
    print("Starting script...")
    _add_to_log("Starting script... DEBUG: sys.argv=" + str(sys.argv))
    _main(sys.argv[4:])
    print("script completed.")
    exit(0)
