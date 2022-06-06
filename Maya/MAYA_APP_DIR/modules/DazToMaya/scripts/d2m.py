import sys
import os
import math
import traceback
import webbrowser
import importlib

import maya.mel as mel
import maya.cmds as cmds
import pymel.core as pm
import xml.etree.cElementTree as ET

from xml.etree import ElementTree
from pymel import versions
from shutil import copyfile

import Definitions
import DtuLoader
import morphs
import dazmaterials as dzm
import TextureLib

if int(cmds.about(v=True)) > 2020:
    import importlib
    importlib.reload(Definitions)
    importlib.reload(DtuLoader)
    importlib.reload(morphs)
    importlib.reload(dzm)
    importlib.reload(TextureLib)
else:
    reload(Definitions)
    reload(DtuLoader)
    reload(morphs)
    reload(dzm)
    reload(TextureLib)


# no delete morph, editer for user...

# DB, 2022-June-05: Hotfix for Mac Maya
import platform
if (platform.system() == "Darwin"):
    module_script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(module_script_dir)

d2m_logo = os.path.abspath("../icons/d2m_import_logo.png")
d2m_banner = os.path.abspath("../icons/d2m_banner.png")
d2m_help_icon = os.path.abspath("../icons/d2m_help_icon.png")
txtConf = os.path.abspath("../scripts/d2m.cfg")

scale_menu_value = "Automatic"

targetShaders = ['phong']
mappingPhongNEW = [
    ['diffuse', 'baseColor'],
    ['color', 'baseColor'],
    ['reflectedColor', 'KrColor'],
    ['specularColor', 'KsColor'],
    ['reflectivity', 'Kr'],
    ['normalCamera', 'normalCamera'],
    ['incandescence', 'emissionColor'],
    ['translucence', 'Kb']
]
mappingPhong = [
    ['diffuse', 'Kd'],
    ['color', 'color'],
    ['reflectedColor', 'KrColor'],
    ['specularColor', 'KsColor'],
    ['reflectivity', 'Kr'],
    ['normalCamera', 'normalCamera'],
    ['incandescence', 'emissionColor'],
    ['translucence', 'Kb']
]

figure = ""

check_box_save = 0
check_box_merge = 0
cfg_settings = ""
window_daz_main = ""
window_name = "DazToMayaMain12225"
ask_to_save_window_name = "AskToSaveWindow5"


def config_ask_to_save(value):
    with open(txtConf, 'wt') as output:
        output.write('askToSaveSceneWithTextures=' + str(value))


# ------------ VRAY FIXES-----------------------------
def vray_eye_fix():
    try:
        mel.eval('setAttr "EyeMoisture.transparency" -type double3 1 1 1')
    except:
        pass
    try:
        mel.eval(
            'setAttr "EyeMoisture.specularColor" -type double3 0.279221 0.279221 0.279221')
    except:
        pass
    try:
        mel.eval('setAttr "EyeMoisture.cosinePower" 91.727273')
    except:
        pass
    try:
        mel.eval('setAttr "EyeMoisture.color" -type double3 1 1 1')
    except:
        pass
    try:
        mel.eval('setAttr "Cornea.cosinePower" 64.36364')
    except:
        pass
    try:
        mel.eval(
            'setAttr "Cornea.specularColor" -type double3 0.75974 0.75974 0.75974')
    except:
        pass
    try:
        mel.eval('setAttr "Cornea.transparency" -type double3 1 1 1')
    except:
        pass


def vray_eyelashes_fix():
    caca = cmds.ls()
    for m in caca:
        if "lashes" in m:
            try:
                cmds.setAttr(m + ".alphaGain", 1.7)
                cmds.setAttr(m + ".invert", 0)
                cmds.setAttr(m + ".alphaIsLuminance", 0)
            except:
                pass
        if "Lash" in m:
            try:
                cmds.setAttr(m + ".alphaGain", 1.7)
                cmds.setAttr(m + ".invert", 0)
                cmds.setAttr(m + ".alphaIsLuminance", 0)
            except:
                pass


def break_transparency():
    try:
        connections = cmds.listConnections("EyeMoisture", d=0, s=1, c=1, p=1)
    except:
        pass
    try:
        for c in connections:
            if ".transparency" in c:
                cAttribute = c
            if ".outTransparency" in c:
                cNode = c
        cmds.disconnectAttr(cNode, cAttribute)
    except:
        pass


def vray_fixes():
    break_transparency()
    vray_eye_fix()
    vray_eyelashes_fix()
# --------------------------------------------------------------------------


def mat_refresh_fix():
    mats = mel.eval('ls -type "phong"')
    if mats != None:
        for m in mats:
            old = m
            new = mel.eval('createNode phong')
            mel.eval('replaceNode %s %s' % (old, new))
            cmds.delete(old)
            cmds.rename(new, m)


def parent_ar(source, target):
    # Parentar------------------------------------------
    mel.eval('select -r %s' % target)
    mel.eval('select -tgl %s' % source)
    mel.eval(
        'doCreateParentConstraintArgList 1 { "1","0","0","0","0","0","0","0","1","","1" }')
    mel.eval('parentConstraint -mo -weight 1')
    mel.eval('select -cl')
    # --------------------------------------------------


def unir_bones(source, target):
    joints_list = mel.eval('ls -type joint')
    if source in joints_list:
        target_pConst = target + "_pointConstraint1"
        # Poner en misma ubicacion-------------------------
        #mel.eval('select -r %s' %source)
        #mel.eval('select -add %s' %target)
        cmds.matchTransform(target, source)
        #mel.eval('pointConstraint -offset 0 0 0 -weight 1')
        #cmds.delete('%s' %target_pConst)

        #mel.eval('select -r %s' %target_pConst)
        # mel.eval('doDelete')
        #mel.eval('select -cl')
        # Parentar------------------------------------------
        parent_ar(source, target)
        # --------------------------------------------------


def add_extra_joint(j_name, j_parent, obj_name, vert_a, vert_b):
    vertex_a = obj_name + ".vtx[" + vert_a + "]"
    vertex_b = obj_name + ".vtx[" + vert_b + "]"
    vert_pos_a = cmds.pointPosition(vertex_a)
    vert_pos_b = cmds.pointPosition(vertex_b)
    vert_pos_x = (vert_pos_a[0] + vert_pos_b[0]) / 2
    vert_pos_y = (vert_pos_a[1] + vert_pos_b[1]) / 2
    vert_pos_z = (vert_pos_a[2] + vert_pos_b[2]) / 2
    mel.eval('select -r %s' % j_parent)
    cmds.joint(name=j_name, p=(vert_pos_x, vert_pos_y, vert_pos_z))


def extra_eye_fixes():
    try:
        mel.eval(
            'disconnectAttr LoganEyesRef.outTransparency EyeReflection.transparency')
        mel.eval('setAttr "EyeReflection.transparency" -type double3 1 1 1')
    except:
        pass


def eyelashes_fix1():
    try:
        mel.eval('select -r Eyelashes_vr')
        mel.eval('delete')
        mel.eval('select -r Eyelashes ')
        try:
            mel.eval('disconnectAttr m5philliplashes.outColor Eyelashes.color ')
            mel.eval('setAttr "m5philliplasheso.invert" 0 ')
        except:
            pass
        try:
            mel.eval('setAttr "v5breelashes1.invert" 0 ')
        except:
            pass
        try:
            mel.eval('setAttr "g8fbaseeyelashes_1006.invert" 0 ')
        except:
            pass
        mel.eval('setAttr "Eyelashes.color" -type double3 0 0 0 ')
        mel.eval('setAttr "Eyelashes.specularColor" -type double3 0 0 0 ')
        mel.eval('setAttr "Eyelashes.cosinePower" 2')
    except:
        print("Lashes fix")


def eyelashes_fix2():
    try:
        mel.eval('select -r Eyelash_vr')
        mel.eval('delete')
        mel.eval('select -r Eyelash')
        mel.eval('setAttr "m4jeremyrrtr.invert" 0')
        mel.eval('setAttr "Eyelash.cosinePower" 2')
        mel.eval('setAttr "Eyelash.reflectedColor" -type double3 0 0 0')
    except:
        print("Lashes fix")
    try:
        mel.eval(
            'setAttr "ncl1_vr.opacityMap" -type double3 0.027972 0.027972 0.027972')
        mel.eval(
            'setAttr "ncl1_vr.reflectionColor" -type double3 0.776224 0.776224 0.776224')
    except:
        print("Lashes fix")


def do_mapping(in_shd):
    """
    Figures out which attribute mapping to use, and does the thing.

    @param inShd: Shader name
    @type inShd: String
    """
    ret = None

    shader_type = cmds.objectType(in_shd)
    print("-*-**-"*10)
    print(shader_type, in_shd)
    if 'phong' in shader_type:
        #ret = shaderToAiStandard(inShd, 'aiStandardSurface', mappingPhong)
        ret = shader_to_ai_standard(in_shd, 'aiStandard', mappingPhong)
        print(in_shd, "Converted")
        convert_phong(in_shd, ret)

    # else:
    #    print shaderType, " not supported yet"

        # do some cleanup on the roughness params
    #    for chan in ['specularRoughness', 'refractionRoughness']:
    #        conns = cmds.listConnections( ret + '.' + chan, d=False, s=True, plugs=True )
    #        if not conns:
    #            val = cmds.getAttr(ret + '.' + chan)
    #            setValue(ret + '.' + chan, (1 - val))

    if ret:
        # assign objects to the new shader
        assign_to_new_shader(in_shd, ret)


def assign_to_new_shader(old_shd, new_shd):
    """
    Creates a shading group for the new shader, and assigns members of the old shader to it

    @param oldShd: Old shader to upgrade
    @type oldShd: String
    @param newShd: New shader
    @type newShd: String
    """

    ret_val = False

    shd_group = cmds.listConnections(old_shd, type="shadingEngine")

    # print 'shdGroup:', shdGroup

    if shd_group:
        if "Eye" in new_shd or "Cornea" in new_shd or "Tear" in new_shd:
            print("=========" + new_shd)
            # CHELO LINE...
            cmds.connectAttr(new_shd + '.outColor',
                             shd_group[0] + '.aiSurfaceShader', force=True)
        else:
            cmds.connectAttr(new_shd + '.outColor',
                             shd_group[0] + '.surfaceShader', force=True)
            cmds.delete(old_shd)

        ret_val = True

    return ret_val


def setup_connections(in_shd, from_attr, out_shd, to_attr):
    conns = cmds.listConnections(
        in_shd + '.' + from_attr, d=False, s=True, plugs=True)
    if conns:
        cmds.connectAttr(conns[0], out_shd + '.' + to_attr, force=True)
        return True

    return False


def shader_to_ai_standard(in_shd, node_type, mapping):
    """
    'Converts' a shader to arnold, using a mapping table.

    @param inShd: Shader to convert
    @type inShd: String
    @param nodeType: Arnold shader type to create
    @type nodeType: String
    @param mapping: List of attributes to map from old to new
    @type mapping: List
    """

    # print 'Converting material:', inShd

    if ':' in in_shd:
        ai_name = in_shd.rsplit(':')[-1] + '_ai'
    else:
        ai_name = in_shd + '_ai'

    # print 'creating '+ aiName
    ai_node = cmds.shadingNode(node_type, name=ai_name, asShader=True)
    for chan in mapping:
        from_attr = chan[0]
        to_attr = chan[1]

        try:
            if cmds.objExists(in_shd + '.' + from_attr):
                # print '\t', fromAttr, ' -> ', toAttr

                if not setup_connections(in_shd, from_attr, ai_node, to_attr):
                    # copy the values
                    val = cmds.getAttr(in_shd + '.' + from_attr)
                    set_value(ai_node + '.' + to_attr, val)
        except:
            print("nothing to connect...")

    # print 'Done. New shader is ', aiNode

    return ai_node


def set_value(attr, value):
    """Simplified set attribute function.

    @param attr: Attribute to set. Type will be queried dynamically
    @param value: Value to set to. Should be compatible with the attr type.
    """

    a_type = None

    if cmds.objExists(attr):
        # temporarily unlock the attribute
        is_locked = cmds.getAttr(attr, lock=True)
        if is_locked:
            cmds.setAttr(attr, lock=False)

        # one last check to see if we can write to it
        if cmds.getAttr(attr, settable=True):
            attr_type = cmds.getAttr(attr, type=True)

            # print value, type(value)

            if attr_type in ['string']:
                a_type = 'string'
                cmds.setAttr(attr, value, type=a_type)

            elif attr_type in ['long', 'short', 'float', 'byte', 'double', 'doubleAngle', 'doubleLinear', 'bool']:
                a_type = None
                cmds.setAttr(attr, value)

            elif attr_type in ['long2', 'short2', 'float2',  'double2', 'long3', 'short3', 'float3',  'double3']:
                if isinstance(value, float):
                    if attr_type in ['long2', 'short2', 'float2',  'double2']:
                        value = [(value, value)]
                    elif attr_type in ['long3', 'short3', 'float3',  'double3']:
                        value = [(value, value, value)]

                cmds.setAttr(attr, *value[0], type=attr_type)

            # else:
            #    print 'cannot yet handle that data type!!'

        if is_locked:
            # restore the lock on the attr
            cmds.setAttr(attr, lock=True)


def transparency_to_opacity(in_shd, out_shd):
    transp_map = cmds.listConnections(
        in_shd + '.transparency', d=False, s=True, plugs=True)
    if transp_map:
        # map is connected, argh...
        # need to add a reverse node in the shading tree

        # create reverse
        invert_node = cmds.shadingNode(
            'reverse', name=out_shd + '_rev', asUtility=True)

        # connect transparency Map to reverse 'input'
        cmds.connectAttr(transp_map[0], invert_node + '.input', force=True)

        # connect reverse to opacity  ----DAZ needs inverted... avoid this fix! /Chelo
        #cmds.connectAttr(invertNode + '.output', outShd + '.opacity', force=True)

        # connect reverse to opacity
        cmds.connectAttr(transp_map[0], out_shd + '.opacity', force=True)
    else:
        # print inShd

        transparency = cmds.getAttr(in_shd + '.transparency')
        opacity = [(1.0 - transparency[0][0], 1.0 -
                    transparency[0][1], 1.0 - transparency[0][2])]

        # print opacity
        set_value(out_shd + '.opacity', opacity)


def convert_phong(in_shd, out_shd):
    cosine_power = cmds.getAttr(in_shd + '.cosinePower')
    roughness = math.sqrt(1.0 / (0.454 * cosine_power + 3.357))
    set_value(out_shd + '.specularRoughness', roughness)
    set_value(out_shd + '.emission', 1.0)
    set_value(out_shd + '.Ks', 1.0)
    transparency_to_opacity(in_shd, out_shd)


def convert_options():
    cmds.setAttr("defaultArnoldRenderOptions.GIRefractionDepth", 10)


def is_opaque(shape_name):

    my_sgs = cmds.listConnections(shape_name, type='shadingEngine')
    if not my_sgs:
        return 1

    surface_shader = cmds.listConnections(my_sgs[0] + ".aiSurfaceShader")

    if surface_shader == None:
        surface_shader = cmds.listConnections(my_sgs[0] + ".surfaceShader")

    if surface_shader == None:
        return 1

    for shader in surface_shader:
        if cmds.attributeQuery("opacity", node=shader, exists=True) == 0:
            continue

        opacity = cmds.getAttr(shader + ".opacity")

        if opacity[0][0] < 1.0 or opacity[0][1] < 1.0 or opacity[0][2] < 1.0:
            return 0

    return 1


def setup_opacities():
    shapes = cmds.ls(type='geometryShape')
    for shape in shapes:

        if is_opaque(shape) == 0:
            # print shape + ' is transparent'
            try:
                cmds.setAttr(shape+".aiOpaque", 0)
            except:
                print("no opaque")


def convert_all_shaders():
    """
    Converts each (in-use) material in the scene
    """
    # better to loop over the types instead of calling
    # ls -type targetShader
    # if a shader in the list is not registered (i.e. VrayMtl)
    # everything would fail

    for shader_type in targetShaders:
        shader_coll = cmds.ls(exactType=shader_type)
        if shader_coll:
            for x in shader_coll:
                # query the objects assigned to the shader
                # only convert things with members
                shd_group = cmds.listConnections(x, type="shadingEngine")
                set_mem = cmds.sets(shd_group, query=True)
                if set_mem:
                    ret = do_mapping(x)


def convert_all_phong_to_arnold():
    convert_all_shaders()
    setup_opacities()


def break_lash_connection(mat):
    file_list = cmds.ls(type='file')
    for file_text in file_list:
        if "Lashes" in file_text or "lash" in file_text:
            try:
                texture_file = cmds.getAttr(file_text + '.fileTextureName')
                try:
                    mel.eval('disconnectAttr %s.outColor %s.color' % (file_text, mat))
                except:
                    print("breakCon skiped")
            except:
                print("File Text.Error")


def convert_all_to_arnold_daz_fixes():
    convert_all_phong_to_arnold()
    # Make all geometry opaque
    objs = mel.eval('ls -geometry')
    if objs is None:
        print("Nothing on scene")
    else:
        for o in objs:
            try:
                mel.eval('setAttr "%s.aiOpaque" 0' % o)
            except:
                print("no obj")

        i = 0
        mats = mel.eval('ls -type "aiStandard"')

        if (mats == None):
            return

        for mat in mats:
            try:
                mel.eval('setAttr "%s.Ks" 0.045' % mat)
                mel.eval(
                    'setAttr "%s.KsColor" -type double3 0.077 0.077 0.077' % mat)
            except:
                print("no phong")

            if "lashes" in mats[i] or "Lashes" in mats[i]:
                break_lash_connection(mats[i])

            if "Cornea" in mats[i]:
                try:
                    mel.eval(
                        'setAttr "%s.KtColor" -type double3 1 1 1' % mats[i])
                    mel.eval(
                        'setAttr "%s.opacity" -type double3 0.0324675 0.0324675 0.0324675' % mats[i])
                    mel.eval(
                        'setAttr "%s.specularRoughness" 0.00649351' % mats[i])
                    mel.eval('setAttr "%s." 0.25974' % mats[i])
                except:
                    print("matchange skiped")
            if "Reflection" in mats[i]:
                try:
                    mel.eval(
                        'setAttr "%s.color" -type double3 0 0 0' % mats[i])
                    mel.eval(
                        'setAttr "%s.opacity" -type double3 0.0779221 0.0779221 0.0779221' % mats[i])
                    mel.eval(
                        'setAttr "%s.specularRoughness" 0.0324675' % mats[i])
                    mel.eval('setAttr "%s.Ks" 0.746753' % mats[i])
                except:
                    print("matchange skiped")
            if "Moisture" in mats[i]:
                try:
                    mel.eval(
                        'setAttr "%s.opacity" -type double3 0 0 0' % mats[i])
                except:
                    print("matchange skiped")
            if "EyeLights" in mats[i]:
                try:
                    mel.eval(
                        'setAttr "%s.opacity" -type double3 0 0 0' % mats[i])
                except:
                    print("matchange skiped")
            if "Tear" in mats[i]:
                try:
                    mel.eval(
                        'setAttr "%s.opacity" -type double3 0 0 0' % mats[i])
                except:
                    print("matchange skiped")

            i = i + 1


# ==========================================================================


def maya2018_fix():
    try:
        j_parent = cmds.listRelatives("hip", parent=True)[0]
        if "_Group" not in j_parent:
            group_name = j_parent + "_Group"
            cmds.spaceLocator(name=group_name, p=[0, 0, 0])
            j_children = cmds.listRelatives(j_parent, children=True)
    except:
        pass

    if "_Group" not in j_parent:
        try:
            for j in j_children:
                cmds.parent(j, group_name)
        except:
            pass
        cmds.delete(j_parent)
    mel.eval('select -cl')


def gen8_lagrimal_fix():
    try:
        mel.eval(
            'setAttr "ncl1.transparency" -type double3 0.993007 0.993007 0.993007')
        mel.eval('setAttr "ncl1.cosinePower" 44.48951')
        mel.eval(
            'setAttr "ncl1.specularColor" -type double3 0.013986 0.013986 0.013986')
    except:
        pass


def lash_fix_2():
    try:
        mel.eval('setAttr "SummerLash_1006.alphaGain" 1.5')
        mel.eval('setAttr "SummerLash_1006.invert" 0')
        mel.eval('setAttr "SummerLash_1006.alphaIsLuminance" 0')
    except:
        pass


def scalp_fix():
    try:
        mel.eval('setAttr "Scalp.cosinePower" 2')
        mel.eval('setAttr "Scalp.specularColor" -type double3 0 0 0')
        mel.eval('setAttr "Scalp.reflectivity" 0')
    except:
        pass


def hide_bone(target):
    target = target + ".drawStyle"
    cmds.setAttr('%s' % target, 2)


def daz_to_ik():
    # Load Skeleton
    try:
        hide_bone("Genesis2Female")
    except:
        None
    try:
        hide_bone("Genesis2Male")
    except:
        None

    # unirBones(DazBone,HumanIkBone) -------------------------------------
    joints_list = mel.eval('ls -type joint')

    if "hip" in joints_list:
        mel.eval('setCharacterObject("hip","Character1",1,0)')
    # if "pelvis" in jointsList:
        # unirBones("pelvis","Character1_Hips")

    # if "spine" in jointsList:
    #	unirBones("spine","Character1_Spine")

    if "abdomen" in joints_list:
        mel.eval('setCharacterObject("abdomen","Character1",8,0)')

    if "abdomenLower" in joints_list:
        mel.eval('setCharacterObject("abdomenLower","Character1",8,0)')

    if "abdomenUpper" in joints_list:
        mel.eval('setCharacterObject("abdomenUpper","Character1",23,0)')

    if "abdomen2" in joints_list:
        mel.eval('setCharacterObject("abdomen2","Character1",23,0)')
    if "chestLower" in joints_list:
        mel.eval('setCharacterObject("chestLower","Character1",24,0)')

    if "chestUpper" in joints_list:
        mel.eval('setCharacterObject("chestUpper","Character1",25,0)')
    if "chest" in joints_list:
        # mel.eval('setCharacterObject("chest","Character1",24,0)')
        mel.eval('setCharacterObject("chest","Character1",23,0)')

    if "neckLower" in joints_list:
        mel.eval('setCharacterObject("neckLower","Character1",20,0)')
    if "neck" in joints_list:
        mel.eval('setCharacterObject("neck","Character1",20,0)')

    mel.eval('setCharacterObject("head","Character1",15,0)')

    if "abdomen" in joints_list and "chest" in joints_list:  # Sentinel, etc fix
        if "abdomenLower" not in joints_list:
            if "abdomenUpper" not in joints_list:
                if "abdomen2" not in joints_list:
                    if "chestLower" not in joints_list:
                        mel.eval(
                            'setCharacterObject("abdomen","Character1",8,0)')
                        mel.eval(
                            'setCharacterObject("chest","Character1",23,0)')

    # Left
    if "lThighBend" in joints_list:
        mel.eval('setCharacterObject("lThighBend","Character1",2,0)')
    if "lThigh" in joints_list:
        mel.eval('setCharacterObject("lThigh","Character1",2,0)')

    mel.eval('setCharacterObject("lShin","Character1",3,0)')
    mel.eval('setCharacterObject("lFoot","Character1",4,0)')

    if cmds.objExists('lToe'):
        mel.eval('setCharacterObject("lToe","Character1",16,0)')

    if "lCollar" in joints_list:
        mel.eval('setCharacterObject("lCollar","Character1",18,0)')
    # if "lShldr" in jointsList:
        # unirBones("lShldr","Character1_LeftShoulder")

    if "lShldrBend" in joints_list:
        mel.eval('setCharacterObject("lShldrBend","Character1",9,0)')
    if "lShldr" in joints_list:
        mel.eval('setCharacterObject("lShldr","Character1",9,0)')

    if "lForearmBend" in joints_list:
        mel.eval('setCharacterObject("lForearmBend","Character1",10,0)')
    if "lForeArm" in joints_list:
        mel.eval('setCharacterObject("lForeArm","Character1",10,0)')

    mel.eval('setCharacterObject("lHand","Character1",11,0)')
    if cmds.objExists('lThumb1'):
        mel.eval('setCharacterObject("lThumb1","Character1",50,0)')
        mel.eval('setCharacterObject("lThumb2","Character1",51,0)')
        mel.eval('setCharacterObject("lThumb3","Character1",52,0)')
    sentinel = 0
    for joint in joints_list:
        if "SENTINEL" in joint:
            sentinel = sentinel + 1
    if sentinel >= 1:
        print("Sentinel Detected")
    else:
        if cmds.objExists('lThumb4'):
            mel.eval('setCharacterObject("lThumb4","Character1",53,0)')
    if cmds.objExists('lIndex1'):
        mel.eval('setCharacterObject("lIndex1","Character1",54,0)')
        mel.eval('setCharacterObject("lIndex2","Character1",55,0)')
        mel.eval('setCharacterObject("lIndex3","Character1",56,0)')
        mel.eval('setCharacterObject("lIndex4","Character1",57,0)')
    if cmds.objExists('lMid1'):
        mel.eval('setCharacterObject("lMid1","Character1",58,0)')
        mel.eval('setCharacterObject("lMid2","Character1",59,0)')
        mel.eval('setCharacterObject("lMid3","Character1",60,0)')
        mel.eval('setCharacterObject("lMid4","Character1",61,0)')
    if cmds.objExists('lRing1'):
        mel.eval('setCharacterObject("lRing1","Character1",62,0)')
        mel.eval('setCharacterObject("lRing2","Character1",63,0)')
        mel.eval('setCharacterObject("lRing3","Character1",64,0)')
        mel.eval('setCharacterObject("lRing4","Character1",65,0)')
    if cmds.objExists('lPinky1'):
        mel.eval('setCharacterObject("lPinky1","Character1",66,0)')
        mel.eval('setCharacterObject("lPinky2","Character1",67,0)')
        mel.eval('setCharacterObject("lPinky3","Character1",68,0)')
        mel.eval('setCharacterObject("lPinky4","Character1",69,0)')

    # Right
    if "rThighBend" in joints_list:
        mel.eval('setCharacterObject("rThighBend","Character1",5,0)')
    if "rThigh" in joints_list:
        mel.eval('setCharacterObject("rThigh","Character1",5,0)')

    mel.eval('setCharacterObject("rShin","Character1",6,0)')
    mel.eval('setCharacterObject("rFoot","Character1",7,0)')

    if cmds.objExists('rToe'):
        mel.eval('setCharacterObject("rToe","Character1",17,0)')

    if "rCollar" in joints_list:
        mel.eval('setCharacterObject("rCollar","Character1",19,0)')
    # if "rShldr" in jointsList:
        # unirBones("rShldr","Character1_RightShoulder")

    if "rShldrBend" in joints_list:
        mel.eval('setCharacterObject("rShldrBend","Character1",12,0)')
    if "rShldr" in joints_list:
        mel.eval('setCharacterObject("rShldr","Character1",12,0)')

    if "rForearmBend" in joints_list:
        mel.eval('setCharacterObject("rForearmBend","Character1",13,0)')
    if "rForeArm" in joints_list:
        mel.eval('setCharacterObject("rForeArm","Character1",13,0)')

    mel.eval('setCharacterObject("rHand","Character1",14,0)')
    if cmds.objExists('rThumb1'):
        mel.eval('setCharacterObject("rThumb1","Character1",74,0)')
        mel.eval('setCharacterObject("rThumb2","Character1",75,0)')
        mel.eval('setCharacterObject("rThumb3","Character1",76,0)')
    sentinel = 0
    for joint in joints_list:
        if "SENTINEL" in joint:
            sentinel = sentinel + 1
    if sentinel >= 1:
        print("Sentinel Detected")
    else:
        mel.eval('setCharacterObject("rThumb4","Character1",77,0)')

    mel.eval('setCharacterObject("rIndex1","Character1",78,0)')
    mel.eval('setCharacterObject("rIndex2","Character1",79,0)')
    mel.eval('setCharacterObject("rIndex3","Character1",80,0)')
    mel.eval('setCharacterObject("rIndex4","Character1",81,0)')

    mel.eval('setCharacterObject("rMid1","Character1",82,0)')
    mel.eval('setCharacterObject("rMid2","Character1",83,0)')
    mel.eval('setCharacterObject("rMid3","Character1",84,0)')
    mel.eval('setCharacterObject("rMid4","Character1",85,0)')

    mel.eval('setCharacterObject("rRing1","Character1",86,0)')
    mel.eval('setCharacterObject("rRing2","Character1",87,0)')
    mel.eval('setCharacterObject("rRing3","Character1",88,0)')
    mel.eval('setCharacterObject("rRing4","Character1",89,0)')

    mel.eval('setCharacterObject("rPinky1","Character1",90,0)')
    mel.eval('setCharacterObject("rPinky2","Character1",91,0)')
    mel.eval('setCharacterObject("rPinky3","Character1",92,0)')
    mel.eval('setCharacterObject("rPinky4","Character1",93,0)')

    # GENESIS 3 - FIXES ---------------------------------------------------------
    # ---------------------------------------------------------
    # ---------------------------------------------------------

    try:
        mel.eval('setAttr "head.visibility" 0')
    except:
        pass
    if "lForearmTwist" in joints_list:
        mel.eval('setCharacterObject("lForearmTwist","Character1",177,0)')
        mel.eval('setCharacterObject("lShldrTwist","Character1",176,0)')
        mel.eval('setCharacterObject("lThighTwist","Character1",172,0)')
        # parentar("lMetatarsals","Character1_LeftFoot")
        mel.eval('setCharacterObject("rForearmTwist","Character1",179,0)')
        mel.eval('setCharacterObject("rShldrTwist","Character1",178,0)')
        mel.eval('setCharacterObject("rThighTwist","Character1",174,0)')
        # parentar("rMetatarsals","Character1_RightFoot")

    toe_bones_left = ("lBigToe", "lSmallToe1", "lSmallToe2",
                    "lSmallToe3", "lSmallToe4")
    for toe_bone_left in toe_bones_left:
        if toe_bone_left in joints_list:
            parent_ar(toe_bone_left, "lToe")

    toe_bones_right = ("rBigToe", "rSmallToe1", "rSmallToe2",
                     "rSmallToe3", "rSmallToe4")
    for toe_bone_right in toe_bones_right:
        if toe_bone_right in joints_list:
            parent_ar(toe_bone_right, "rToe")


def min_y_in_scene():
    """
    Find the min y of bounding box from all the shapes
    """
    try:
        shapes = cmds.ls(type='geometryShape')
        bound_box_min_y = 0
        bound_box_min_y_all = 0
        for shape in shapes:
            bound_box_min_y = cmds.polyEvaluate(shape, b=True)[1][0]
            if bound_box_min_y < bound_box_min_y_all:
                bound_box_min_y_all = bound_box_min_y
        return bound_box_min_y_all
    except:
        pass


def compensate_hip():
    """
    Adjust hip position based on the min possible y of all shapes in the scene
    """
    try:
        min_y = min_y_in_scene()
        hip_y = cmds.getAttr("hip.translateY")
        cmds.setAttr('hip.translateY', hip_y + (min_y*-1))
    except:
        pass


def extend_finger(base_scale_bone, end_bone, new_bone, scale=2, rotation=0):
    mel.eval('select -r %s' % base_scale_bone)

    mel.eval('rotate -r -os -fo 0 0 %s' % rotation)
    mel.eval('scale -a %s %s %s' % (scale, scale, scale))
    mel.eval('select -r %s' % end_bone)
    caca = mel.eval('xform -q -t -ws')
    mel.eval('select -r %s' % base_scale_bone)
    mel.eval('scale -a 1 1 1')
    rotation = rotation * -1
    mel.eval('rotate -r -os -fo 0 0 %s' % rotation)
    mel.eval('select -r %s' % end_bone)
    cmds.joint(name=new_bone, p=(caca))


def extend_hand_fingers():
    joints_list = mel.eval('ls -type joint')
    done = 0
    if "lIndex3" in joints_list:
        extend_finger("lIndex2", "lIndex3", "lIndex4", 2, 0)
        extend_finger("lMid2", "lMid3", "lMid4", 2, 0)
        extend_finger("lRing2", "lRing3", "lRing4", 2, 0)
        extend_finger("lPinky2", "lPinky3", "lPinky4", 2, 0)
        extend_finger("lThumb2", "lThumb3", "lThumb4", 2, 0)

        extend_finger("rIndex2", "rIndex3", "rIndex4", 2, 0)
        extend_finger("rMid2", "rMid3", "rMid4", 2, 0)
        extend_finger("rRing2", "rRing3", "rRing4", 2, 0)
        extend_finger("rPinky2", "rPinky3", "rPinky4", 2, 0)
        extend_finger("rThumb2", "rThumb3", "rThumb4", 2, 0)
        done = 1
    if "lIndex2" in joints_list:
        if "lIndex3" not in joints_list:
            extend_finger("lIndex2", "lIndex2", "lIndex3")
            extend_finger("lMid2", "lMid2", "lMid3")
            extend_finger("lRing2", "lRing2", "lRing3")
            extend_finger("lPinky2", "lPinky2", "lPinky3")
            extend_finger("lThumb2", "lThumb2", "lThumb3", 2)

            extend_finger("rIndex2", "rIndex2", "rIndex3")
            extend_finger("rMid2", "rMid2", "rMid3")
            extend_finger("rRing2", "rRing2", "rRing3")
            extend_finger("rPinky2", "rPinky2", "rPinky3")
            extend_finger("rThumb2", "rThumb2", "rThumb3", 2)


def sentinel_remove_finger():
    try:
        mel.eval('select -r -sym lThumb4')
        mel.eval('doDelete')
        mel.eval('select -r -sym rThumb4')
        mel.eval('doDelete')
    except:
        print("Sentinel Finger Fix")


def remove_hidden_objs():
    camera_list = cmds.ls(cameras=1)
    obj_list = cmds.ls()
    i = 0
    for obj in obj_list:
        try:
            visibility = cmds.getAttr(obj_list[i] + ".visibility")
            if visibility == False:
                if obj not in camera_list:
                    mel.eval('delete %s' % obj_list[i])
        except:
            None
        i = i + 1


def scene_modified_check():
    """
    Check and exit if scene modified
    """
    objs = mel.eval('ls')
    for obj in objs:
        if cmds.objectType(obj) == "locator":
            if obj.find("Character1_Reference") == 0:
                print("\n"*10)
                print("Scene already modified")
                sys.exit()  # ABOUR SCRIPT IF SCENE NOT READY!!


def transparency_fix():
    shader_type = "phong"
    mat_list = cmds.ls(exactType=shader_type)
    skip_mats = ["Pupils", "Cornea", "Irises", "nails", "Eye"]

    for mat in mat_list:
        for skip_mat in skip_mats:
            if skip_mat not in mat:
                try:
                    mel.eval('setAttr "%s.specularColor" -type double3 0 0 0' % mat)
                    mel.eval('setAttr "%s.reflectivity" 0' % mat)
                except:
                    pass


def clamp_textures():
    try:
        mel.eval('setAttr "hardwareRenderingGlobals.enableTextureMaxRes" 1')
        mel.eval('setAttr "hardwareRenderingGlobals.textureMaxResolution" 512')
    except:
        print("No Text Clamp")


# TODO: Remove hardocing
def sentinel_rotations_fix():
    try:
        mel.eval('setAttr "lShldr.rotateX" 0.54')
        mel.eval('setAttr "lShldr.rotateY" 3.88')
        mel.eval('setAttr "lShldr.rotateZ" 7.05')

        mel.eval('setAttr "rShldr.rotateX" 0.54')
        mel.eval('setAttr "rShldr.rotateY" -3.88')
        mel.eval('setAttr "rShldr.rotateZ" -7.05')

        mel.eval('setAttr "lForeArm.rotateX" -0.26')
        mel.eval('setAttr "lForeArm.rotateY" 9.49')
        mel.eval('setAttr "lForeArm.rotateZ" -0.13')

        mel.eval('setAttr "rForeArm.rotateX" -0.26')
        mel.eval('setAttr "rForeArm.rotateY" -9.49')
        mel.eval('setAttr "rForeArm.rotateZ" 0.13')

        mel.eval('setAttr "lHand.rotateX" 16.88')
        mel.eval('setAttr "lHand.rotateY" -1.91')
        mel.eval('setAttr "lHand.rotateZ" -0.71')

        mel.eval('setAttr "rHand.rotateX" 16.88')
        mel.eval('setAttr "rHand.rotateY" 1.91')
        mel.eval('setAttr "rHand.rotateZ" 0.71')

        mel.eval('setAttr "lThumb1.rotateX" -9.98')
        mel.eval('setAttr "lThumb1.rotateY" -9.51')
        mel.eval('setAttr "lThumb1.rotateZ" 5.4')

        mel.eval('setAttr "rThumb1.rotateX" -9.98')
        mel.eval('setAttr "rThumb1.rotateY" 9.51')
        mel.eval('setAttr "rThumb1.rotateZ" -5.4')

        mel.eval('setAttr "lThumb2.rotateX" -0.6')
        mel.eval('setAttr "lThumb2.rotateY" -12.73')
        mel.eval('setAttr "lThumb2.rotateZ" 0.27')

        mel.eval('setAttr "rThumb2.rotateX" -0.6')
        mel.eval('setAttr "rThumb2.rotateY" 12.73')
        mel.eval('setAttr "rThumb2.rotateZ" -0.27')

        mel.eval('setAttr "lThumb3.rotateX" -0.6')
        mel.eval('setAttr "lThumb3.rotateY" -12.73')
        mel.eval('setAttr "lThumb3.rotateZ" 0.27')

        mel.eval('setAttr "rThumb3.rotateX" -0.6')
        mel.eval('setAttr "rThumb3.rotateY" 12.73')
        mel.eval('setAttr "rThumb3.rotateZ" -0.27')

        mel.eval('setAttr "lIndex1.rotateX" -6.65')
        mel.eval('setAttr "lIndex1.rotateY" -7.61')
        mel.eval('setAttr "lIndex1.rotateZ" 5.69')

        mel.eval('setAttr "rIndex1.rotateX" -6.65')
        mel.eval('setAttr "rIndex1.rotateY" 7.61')
        mel.eval('setAttr "rIndex1.rotateZ" -5.69')

        mel.eval('setAttr "lIndex2.rotateX" 3.39')
        mel.eval('setAttr "lIndex2.rotateY" -1.2')
        mel.eval('setAttr "lIndex2.rotateZ" 21.0')

        mel.eval('setAttr "rIndex2.rotateX" 3.39')
        mel.eval('setAttr "rIndex2.rotateY" 1.2')
        mel.eval('setAttr "rIndex2.rotateZ" -21.0')

        mel.eval('setAttr "lIndex3.rotateX" -0.0')
        mel.eval('setAttr "lIndex3.rotateY" -0.0')
        mel.eval('setAttr "lIndex3.rotateZ" 0.0')

        mel.eval('setAttr "rIndex3.rotateX" -0.0')
        mel.eval('setAttr "rIndex3.rotateY" 0.0')
        mel.eval('setAttr "rIndex3.rotateZ" -0.0')

        mel.eval('setAttr "lMid1.rotateX" 1.02')
        mel.eval('setAttr "lMid1.rotateY" -13.59')
        mel.eval('setAttr "lMid1.rotateZ" 14.46')

        mel.eval('setAttr "rMid1.rotateX" 1.02')
        mel.eval('setAttr "rMid1.rotateY" 13.59')
        mel.eval('setAttr "rMid1.rotateZ" -14.46')

        mel.eval('setAttr "lMid2.rotateX" 0.12')
        mel.eval('setAttr "lMid2.rotateY" -4.91')
        mel.eval('setAttr "lMid2.rotateZ" 20.86')

        mel.eval('setAttr "rMid2.rotateX" 0.12')
        mel.eval('setAttr "rMid2.rotateY" 4.91')
        mel.eval('setAttr "rMid2.rotateZ" -20.86')

        mel.eval('setAttr "lMid3.rotateX" 0.31')
        mel.eval('setAttr "lMid3.rotateY" -1.98')
        mel.eval('setAttr "lMid3.rotateZ" -2.4')

        mel.eval('setAttr "rMid3.rotateX" 0.31')
        mel.eval('setAttr "rMid3.rotateY" 1.98')
        mel.eval('setAttr "rMid3.rotateZ" 2.4')

        mel.eval('setAttr "lRing1.rotateX" -2.7')
        mel.eval('setAttr "lRing1.rotateY" -16.45')
        mel.eval('setAttr "lRing1.rotateZ" 26.89')

        mel.eval('setAttr "rRing1.rotateX" -2.7')
        mel.eval('setAttr "rRing1.rotateY" 16.45')
        mel.eval('setAttr "rRing1.rotateZ" -26.89')

        mel.eval('setAttr "lRing2.rotateX" -1.93')
        mel.eval('setAttr "lRing2.rotateY" -5.11')
        mel.eval('setAttr "lRing2.rotateZ" 12.0')

        mel.eval('setAttr "rRing2.rotateX" -1.93')
        mel.eval('setAttr "rRing2.rotateY" 5.11')
        mel.eval('setAttr "rRing2.rotateZ" -12.0')

        mel.eval('setAttr "lRing3.rotateX" 0.0')
        mel.eval('setAttr "lRing3.rotateY" -0.0')
        mel.eval('setAttr "lRing3.rotateZ" 0.0')

        mel.eval('setAttr "rRing3.rotateX" 0.0')
        mel.eval('setAttr "rRing3.rotateY" 0.0')
        mel.eval('setAttr "rRing3.rotateZ" -0.0')

        mel.eval('setAttr "lPinky1.rotateX" -2.24')
        mel.eval('setAttr "lPinky1.rotateY" -18.15')
        mel.eval('setAttr "lPinky1.rotateZ" 18.9')

        mel.eval('setAttr "rPinky1.rotateX" -2.24')
        mel.eval('setAttr "rPinky1.rotateY" 18.15')
        mel.eval('setAttr "rPinky1.rotateZ" -18.9')

        mel.eval('setAttr "lPinky2.rotateX" 3.15')
        mel.eval('setAttr "lPinky2.rotateY" -6.07')
        mel.eval('setAttr "lPinky2.rotateZ" 23.72')

        mel.eval('setAttr "rPinky2.rotateX" 3.15')
        mel.eval('setAttr "rPinky2.rotateY" 6.07')
        mel.eval('setAttr "rPinky2.rotateZ" -23.72')

        mel.eval('setAttr "lPinky3.rotateX" 5.42')
        mel.eval('setAttr "lPinky3.rotateY" 7.35')
        mel.eval('setAttr "lPinky3.rotateZ" 2.93')

        mel.eval('setAttr "rPinky3.rotateX" 5.42')
        mel.eval('setAttr "rPinky3.rotateY" -7.35')
        mel.eval('setAttr "rPinky3.rotateZ" -2.93')

        mel.eval('setAttr "lThigh.rotateX" -0.37')
        mel.eval('setAttr "lThigh.rotateY" -0.45')
        mel.eval('setAttr "lThigh.rotateZ" -4.37')

        mel.eval('setAttr "rThigh.rotateX" -0.37')
        mel.eval('setAttr "rThigh.rotateY" 0.45')
        mel.eval('setAttr "rThigh.rotateZ" 4.37')

        mel.eval('setAttr "lFoot.rotateX" -0.57')
        mel.eval('setAttr "lFoot.rotateY" -6.61')
        mel.eval('setAttr "lFoot.rotateZ" -3.66')

        mel.eval('setAttr "rFoot.rotateX" -0.57')
        mel.eval('setAttr "rFoot.rotateY" 6.61')
        mel.eval('setAttr "rFoot.rotateZ" 3.66')
    except:
        print("Sentinel fix")


# TODO: Remove hardocing
def gen1_rotations_fix():
    try:
        mel.eval('setAttr "lShldr.rotateX" -0.0')
        mel.eval('setAttr "lShldr.rotateY" 5.7')
        mel.eval('setAttr "lShldr.rotateZ" 2.73')

        mel.eval('setAttr "rShldr.rotateX" -0.0')
        mel.eval('setAttr "rShldr.rotateY" -5.7')
        mel.eval('setAttr "rShldr.rotateZ" -2.73')

        mel.eval('setAttr "lForeArm.rotateX" 0.0')
        mel.eval('setAttr "lForeArm.rotateY" 20.0')
        mel.eval('setAttr "lForeArm.rotateZ" -1.78')

        mel.eval('setAttr "rForeArm.rotateX" 0.0')
        mel.eval('setAttr "rForeArm.rotateY" -20.0')
        mel.eval('setAttr "rForeArm.rotateZ" 1.78')

        mel.eval('setAttr "lHand.rotateX" -0.0')
        mel.eval('setAttr "lHand.rotateY" -0.0')
        mel.eval('setAttr "lHand.rotateZ" 0.0')

        mel.eval('setAttr "rHand.rotateX" -0.0')
        mel.eval('setAttr "rHand.rotateY" 0.0')
        mel.eval('setAttr "rHand.rotateZ" -0.0')

        mel.eval('setAttr "lThumb1.rotateX" 0.0')
        mel.eval('setAttr "lThumb1.rotateY" 0.0')
        mel.eval('setAttr "lThumb1.rotateZ" 2.94')

        mel.eval('setAttr "rThumb1.rotateX" 0.0')
        mel.eval('setAttr "rThumb1.rotateY" -0.0')
        mel.eval('setAttr "rThumb1.rotateZ" -2.94')

        mel.eval('setAttr "lThumb2.rotateX" 0.0')
        mel.eval('setAttr "lThumb2.rotateY" -0.0')
        mel.eval('setAttr "lThumb2.rotateZ" 0.0')

        mel.eval('setAttr "rThumb2.rotateX" 0.0')
        mel.eval('setAttr "rThumb2.rotateY" 0.0')
        mel.eval('setAttr "rThumb2.rotateZ" -0.0')

        mel.eval('setAttr "lThumb3.rotateX" 0.0')
        mel.eval('setAttr "lThumb3.rotateY" -0.0')
        mel.eval('setAttr "lThumb3.rotateZ" 0.0')

        mel.eval('setAttr "rThumb3.rotateX" 0.0')
        mel.eval('setAttr "rThumb3.rotateY" 0.0')
        mel.eval('setAttr "rThumb3.rotateZ" -0.0')

        mel.eval('setAttr "lCarpal1.rotateX" -0.0')
        mel.eval('setAttr "lCarpal1.rotateY" -0.0')
        mel.eval('setAttr "lCarpal1.rotateZ" 0.0')

        mel.eval('setAttr "rCarpal1.rotateX" -0.0')
        mel.eval('setAttr "rCarpal1.rotateY" 0.0')
        mel.eval('setAttr "rCarpal1.rotateZ" -0.0')

        mel.eval('setAttr "lIndex1.rotateX" -5.14')
        mel.eval('setAttr "lIndex1.rotateY" 12.62')
        mel.eval('setAttr "lIndex1.rotateZ" 16.12')

        mel.eval('setAttr "rIndex1.rotateX" -5.14')
        mel.eval('setAttr "rIndex1.rotateY" -12.62')
        mel.eval('setAttr "rIndex1.rotateZ" -16.12')

        mel.eval('setAttr "lIndex2.rotateX" 7.45')
        mel.eval('setAttr "lIndex2.rotateY" -3.01')
        mel.eval('setAttr "lIndex2.rotateZ" 27.34')

        mel.eval('setAttr "rIndex2.rotateX" 7.45')
        mel.eval('setAttr "rIndex2.rotateY" 3.01')
        mel.eval('setAttr "rIndex2.rotateZ" -27.34')

        mel.eval('setAttr "lIndex3.rotateX" 4.44')
        mel.eval('setAttr "lIndex3.rotateY" -0.0')
        mel.eval('setAttr "lIndex3.rotateZ" 12.1')

        mel.eval('setAttr "rIndex3.rotateX" 4.44')
        mel.eval('setAttr "rIndex3.rotateY" 0.0')
        mel.eval('setAttr "rIndex3.rotateZ" -12.1')

        mel.eval('setAttr "lMid1.rotateX" 5.49')
        mel.eval('setAttr "lMid1.rotateY" 3.03')
        mel.eval('setAttr "lMid1.rotateZ" 17.56')

        mel.eval('setAttr "rMid1.rotateX" 5.49')
        mel.eval('setAttr "rMid1.rotateY" -3.03')
        mel.eval('setAttr "rMid1.rotateZ" -17.56')

        mel.eval('setAttr "lMid2.rotateX" -0.62')
        mel.eval('setAttr "lMid2.rotateY" 0.01')
        mel.eval('setAttr "lMid2.rotateZ" 32.07')

        mel.eval('setAttr "rMid2.rotateX" -0.62')
        mel.eval('setAttr "rMid2.rotateY" -0.01')
        mel.eval('setAttr "rMid2.rotateZ" -32.07')

        mel.eval('setAttr "lMid3.rotateX" 5.7')
        mel.eval('setAttr "lMid3.rotateY" 0.01')
        mel.eval('setAttr "lMid3.rotateZ" 16.17')

        mel.eval('setAttr "rMid3.rotateX" 5.7')
        mel.eval('setAttr "rMid3.rotateY" -0.01')
        mel.eval('setAttr "rMid3.rotateZ" -16.17')

        mel.eval('setAttr "lCarpal2.rotateX" -0.0')
        mel.eval('setAttr "lCarpal2.rotateY" -0.0')
        mel.eval('setAttr "lCarpal2.rotateZ" 0.0')

        mel.eval('setAttr "rCarpal2.rotateX" -0.0')
        mel.eval('setAttr "rCarpal2.rotateY" 0.0')
        mel.eval('setAttr "rCarpal2.rotateZ" -0.0')

        mel.eval('setAttr "lRing1.rotateX" 4.68')
        mel.eval('setAttr "lRing1.rotateY" -3.36')
        mel.eval('setAttr "lRing1.rotateZ" 19.99')

        mel.eval('setAttr "rRing1.rotateX" 4.68')
        mel.eval('setAttr "rRing1.rotateY" 3.36')
        mel.eval('setAttr "rRing1.rotateZ" -19.99')

        mel.eval('setAttr "lRing2.rotateX" 3.19')
        mel.eval('setAttr "lRing2.rotateY" 1.4')
        mel.eval('setAttr "lRing2.rotateZ" 32.05')

        mel.eval('setAttr "rRing2.rotateX" 3.19')
        mel.eval('setAttr "rRing2.rotateY" -1.4')
        mel.eval('setAttr "rRing2.rotateZ" -32.05')

        mel.eval('setAttr "lRing3.rotateX" 4.9')
        mel.eval('setAttr "lRing3.rotateY" 0.17')
        mel.eval('setAttr "lRing3.rotateZ" 5.06')

        mel.eval('setAttr "rRing3.rotateX" 4.9')
        mel.eval('setAttr "rRing3.rotateY" -0.17')
        mel.eval('setAttr "rRing3.rotateZ" -5.06')

        mel.eval('setAttr "lPinky1.rotateX" 6.72')
        mel.eval('setAttr "lPinky1.rotateY" -12.44')
        mel.eval('setAttr "lPinky1.rotateZ" 23.36')

        mel.eval('setAttr "rPinky1.rotateX" 6.72')
        mel.eval('setAttr "rPinky1.rotateY" 12.44')
        mel.eval('setAttr "rPinky1.rotateZ" -23.36')

        mel.eval('setAttr "lPinky2.rotateX" 7.11')
        mel.eval('setAttr "lPinky2.rotateY" 6.24')
        mel.eval('setAttr "lPinky2.rotateZ" 38.7')

        mel.eval('setAttr "rPinky2.rotateX" 7.11')
        mel.eval('setAttr "rPinky2.rotateY" -6.24')
        mel.eval('setAttr "rPinky2.rotateZ" -38.7')

        mel.eval('setAttr "lPinky3.rotateX" 0.0')
        mel.eval('setAttr "lPinky3.rotateY" 0.0')
        mel.eval('setAttr "lPinky3.rotateZ" -0.0')

        mel.eval('setAttr "rPinky3.rotateX" 0.0')
        mel.eval('setAttr "rPinky3.rotateY" -0.0')
        mel.eval('setAttr "rPinky3.rotateZ" 0.0')

        mel.eval('setAttr "lFoot.rotateX" -0.1')
        mel.eval('setAttr "lFoot.rotateY" -11.32')
        mel.eval('setAttr "lFoot.rotateZ" 3.78')

        mel.eval('setAttr "rFoot.rotateX" -0.1')
        mel.eval('setAttr "rFoot.rotateY" 11.32')
        mel.eval('setAttr "rFoot.rotateZ" -3.78')

    except:
        print("Gen1RotsFix...")


# TODO: Remove hardocing
def gen2_rotations_fix():
    try:
        mel.eval('setAttr "lShldr.rotateX" -0.0')
        mel.eval('setAttr "lShldr.rotateY" 5.44')
        mel.eval('setAttr "lShldr.rotateZ" 1.87')

        mel.eval('setAttr "rShldr.rotateX" -0.0')
        mel.eval('setAttr "rShldr.rotateY" -5.44')
        mel.eval('setAttr "rShldr.rotateZ" -1.87')

        mel.eval('setAttr "lForeArm.rotateX" 0.62')
        mel.eval('setAttr "lForeArm.rotateY" 20.19')
        mel.eval('setAttr "lForeArm.rotateZ" -1.69')

        mel.eval('setAttr "rForeArm.rotateX" 0.62')
        mel.eval('setAttr "rForeArm.rotateY" -20.19')
        mel.eval('setAttr "rForeArm.rotateZ" 1.69')

        mel.eval('setAttr "lHand.rotateX" 15.11')
        mel.eval('setAttr "lHand.rotateY" -0.28')
        mel.eval('setAttr "lHand.rotateZ" -0.59')

        mel.eval('setAttr "rHand.rotateX" 15.11')
        mel.eval('setAttr "rHand.rotateY" 0.28')
        mel.eval('setAttr "rHand.rotateZ" 0.59')

        mel.eval('setAttr "lThumb1.rotateX" -0.0')
        mel.eval('setAttr "lThumb1.rotateY" -0.0')
        mel.eval('setAttr "lThumb1.rotateZ" 0.0')

        mel.eval('setAttr "rThumb1.rotateX" -0.0')
        mel.eval('setAttr "rThumb1.rotateY" 0.0')
        mel.eval('setAttr "rThumb1.rotateZ" -0.0')

        mel.eval('setAttr "lThumb2.rotateX" -0.0')
        mel.eval('setAttr "lThumb2.rotateY" -0.0')
        mel.eval('setAttr "lThumb2.rotateZ" -0.0')

        mel.eval('setAttr "rThumb2.rotateX" -0.0')
        mel.eval('setAttr "rThumb2.rotateY" 0.0')
        mel.eval('setAttr "rThumb2.rotateZ" 0.0')

        mel.eval('setAttr "lThumb3.rotateX" 0.0')
        mel.eval('setAttr "lThumb3.rotateY" -0.0')
        mel.eval('setAttr "lThumb3.rotateZ" -0.0')

        mel.eval('setAttr "rThumb3.rotateX" 0.0')
        mel.eval('setAttr "rThumb3.rotateY" 0.0')
        mel.eval('setAttr "rThumb3.rotateZ" 0.0')

        mel.eval('setAttr "lCarpal1.rotateX" -0.29')
        mel.eval('setAttr "lCarpal1.rotateY" -0.4')
        mel.eval('setAttr "lCarpal1.rotateZ" -2.3')

        mel.eval('setAttr "rCarpal1.rotateX" -0.29')
        mel.eval('setAttr "rCarpal1.rotateY" 0.4')
        mel.eval('setAttr "rCarpal1.rotateZ" 2.3')

        mel.eval('setAttr "lIndex1.rotateX" 0.15')
        mel.eval('setAttr "lIndex1.rotateY" 10.31')
        mel.eval('setAttr "lIndex1.rotateZ" 0.16')

        mel.eval('setAttr "rIndex1.rotateX" 0.15')
        mel.eval('setAttr "rIndex1.rotateY" -10.31')
        mel.eval('setAttr "rIndex1.rotateZ" -0.16')

        mel.eval('setAttr "lIndex2.rotateX" -1.01')
        mel.eval('setAttr "lIndex2.rotateY" -0.08')
        mel.eval('setAttr "lIndex2.rotateZ" 13.96')

        mel.eval('setAttr "rIndex2.rotateX" -1.01')
        mel.eval('setAttr "rIndex2.rotateY" 0.08')
        mel.eval('setAttr "rIndex2.rotateZ" -13.96')

        mel.eval('setAttr "lIndex3.rotateX" -0.0')
        mel.eval('setAttr "lIndex3.rotateY" 0.0')
        mel.eval('setAttr "lIndex3.rotateZ" 0.0')

        mel.eval('setAttr "rIndex3.rotateX" -0.0')
        mel.eval('setAttr "rIndex3.rotateY" -0.0')
        mel.eval('setAttr "rIndex3.rotateZ" -0.0')

        mel.eval('setAttr "lMid1.rotateX" 5.85')
        mel.eval('setAttr "lMid1.rotateY" 2.88')
        mel.eval('setAttr "lMid1.rotateZ" -0.0')

        mel.eval('setAttr "rMid1.rotateX" 5.85')
        mel.eval('setAttr "rMid1.rotateY" -2.88')
        mel.eval('setAttr "rMid1.rotateZ" 0.0')

        mel.eval('setAttr "lMid2.rotateX" 0.0')
        mel.eval('setAttr "lMid2.rotateY" 0.0')
        mel.eval('setAttr "lMid2.rotateZ" 9.13')

        mel.eval('setAttr "rMid2.rotateX" 0.0')
        mel.eval('setAttr "rMid2.rotateY" -0.0')
        mel.eval('setAttr "rMid2.rotateZ" -9.13')

        mel.eval('setAttr "lMid3.rotateX" -0.0')
        mel.eval('setAttr "lMid3.rotateY" 0.0')
        mel.eval('setAttr "lMid3.rotateZ" 0.0')

        mel.eval('setAttr "rMid3.rotateX" -0.0')
        mel.eval('setAttr "rMid3.rotateY" -0.0')
        mel.eval('setAttr "rMid3.rotateZ" -0.0')

        mel.eval('setAttr "lCarpal2.rotateX" 0.11')
        mel.eval('setAttr "lCarpal2.rotateY" 0.02')
        mel.eval('setAttr "lCarpal2.rotateZ" -0.72')

        mel.eval('setAttr "rCarpal2.rotateX" 0.11')
        mel.eval('setAttr "rCarpal2.rotateY" -0.02')
        mel.eval('setAttr "rCarpal2.rotateZ" 0.72')

        mel.eval('setAttr "lRing1.rotateX" 2.91')
        mel.eval('setAttr "lRing1.rotateY" -4.8')
        mel.eval('setAttr "lRing1.rotateZ" -0.0')

        mel.eval('setAttr "rRing1.rotateX" 2.91')
        mel.eval('setAttr "rRing1.rotateY" 4.8')
        mel.eval('setAttr "rRing1.rotateZ" 0.0')

        mel.eval('setAttr "lRing2.rotateX" 12.88')
        mel.eval('setAttr "lRing2.rotateY" 1.94')
        mel.eval('setAttr "lRing2.rotateZ" 7.8')

        mel.eval('setAttr "rRing2.rotateX" 12.88')
        mel.eval('setAttr "rRing2.rotateY" -1.94')
        mel.eval('setAttr "rRing2.rotateZ" -7.8')

        mel.eval('setAttr "lRing3.rotateX" 0.0')
        mel.eval('setAttr "lRing3.rotateY" -0.0')
        mel.eval('setAttr "lRing3.rotateZ" 0.0')

        mel.eval('setAttr "rRing3.rotateX" 0.0')
        mel.eval('setAttr "rRing3.rotateY" 0.0')
        mel.eval('setAttr "rRing3.rotateZ" -0.0')

        mel.eval('setAttr "lPinky1.rotateX" 0.0')
        mel.eval('setAttr "lPinky1.rotateY" -6.84')
        mel.eval('setAttr "lPinky1.rotateZ" 0.0')

        mel.eval('setAttr "rPinky1.rotateX" 0.0')
        mel.eval('setAttr "rPinky1.rotateY" 6.84')
        mel.eval('setAttr "rPinky1.rotateZ" -0.0')

        mel.eval('setAttr "lPinky2.rotateX" 0.0')
        mel.eval('setAttr "lPinky2.rotateY" 0.0')
        mel.eval('setAttr "lPinky2.rotateZ" 10.86')

        mel.eval('setAttr "rPinky2.rotateX" 0.0')
        mel.eval('setAttr "rPinky2.rotateY" -0.0')
        mel.eval('setAttr "rPinky2.rotateZ" -10.86')

        mel.eval('setAttr "lPinky3.rotateX" -0.0')
        mel.eval('setAttr "lPinky3.rotateY" -0.0')
        mel.eval('setAttr "lPinky3.rotateZ" 0.0')

        mel.eval('setAttr "rPinky3.rotateX" -0.0')
        mel.eval('setAttr "rPinky3.rotateY" 0.0')
        mel.eval('setAttr "rPinky3.rotateZ" -0.0')
    except:
        print("Gen2RotsFix...")


# TODO: Remove hardocing
def gen3_rotations_fix():
    # ---------------------------------------------------------
    try:
        mel.eval('setAttr "lShldrBend.rotateX" 0.11')
        mel.eval('setAttr "lShldrBend.rotateY" 2.52')
        mel.eval('setAttr "lShldrBend.rotateZ" 3.86')

        mel.eval('setAttr "rShldrBend.rotateX" 0.11')
        mel.eval('setAttr "rShldrBend.rotateY" -2.52')
        mel.eval('setAttr "rShldrBend.rotateZ" -3.86')

        mel.eval('setAttr "lForearmBend.rotateX" -0.29')
        mel.eval('setAttr "lForearmBend.rotateY" 12.71')
        mel.eval('setAttr "lForearmBend.rotateZ" -3.95')

        mel.eval('setAttr "rForearmBend.rotateX" -0.29')
        mel.eval('setAttr "rForearmBend.rotateY" -12.71')
        mel.eval('setAttr "rForearmBend.rotateZ" 3.95')

        mel.eval('setAttr "lHand.rotateX" 0.03')
        mel.eval('setAttr "lHand.rotateY" -14.23')
        mel.eval('setAttr "lHand.rotateZ" 1.77')

        mel.eval('setAttr "rHand.rotateX" 0.03')
        mel.eval('setAttr "rHand.rotateY" 14.23')
        mel.eval('setAttr "rHand.rotateZ" -1.77')

        mel.eval('setAttr "lThumb1.rotateX" 0.0')
        mel.eval('setAttr "lThumb1.rotateY" 0.0')
        mel.eval('setAttr "lThumb1.rotateZ" -0.0')

        mel.eval('setAttr "rThumb1.rotateX" 0.0')
        mel.eval('setAttr "rThumb1.rotateY" -0.0')
        mel.eval('setAttr "rThumb1.rotateZ" 0.0')

        mel.eval('setAttr "lThumb2.rotateX" 0.0')
        mel.eval('setAttr "lThumb2.rotateY" -0.0')
        mel.eval('setAttr "lThumb2.rotateZ" 0.0')

        mel.eval('setAttr "rThumb2.rotateX" 0.0')
        mel.eval('setAttr "rThumb2.rotateY" 0.0')
        mel.eval('setAttr "rThumb2.rotateZ" -0.0')

        mel.eval('setAttr "lThumb3.rotateX" -0.0')
        mel.eval('setAttr "lThumb3.rotateY" -0.0')
        mel.eval('setAttr "lThumb3.rotateZ" -0.0')

        mel.eval('setAttr "rThumb3.rotateX" -0.0')
        mel.eval('setAttr "rThumb3.rotateY" 0.0')
        mel.eval('setAttr "rThumb3.rotateZ" 0.0')

        mel.eval('setAttr "lCarpal1.rotateX" 0.0')
        mel.eval('setAttr "lCarpal1.rotateY" -0.0')
        mel.eval('setAttr "lCarpal1.rotateZ" -0.0')

        mel.eval('setAttr "rCarpal1.rotateX" 0.0')
        mel.eval('setAttr "rCarpal1.rotateY" 0.0')
        mel.eval('setAttr "rCarpal1.rotateZ" 0.0')

        mel.eval('setAttr "lIndex1.rotateX" -2.07')
        mel.eval('setAttr "lIndex1.rotateY" 12.03')
        mel.eval('setAttr "lIndex1.rotateZ" 2.8')

        mel.eval('setAttr "rIndex1.rotateX" -2.07')
        mel.eval('setAttr "rIndex1.rotateY" -12.03')
        mel.eval('setAttr "rIndex1.rotateZ" -2.8')

        mel.eval('setAttr "lIndex2.rotateX" 0.31')
        mel.eval('setAttr "lIndex2.rotateY" -4.02')
        mel.eval('setAttr "lIndex2.rotateZ" 1.4')

        mel.eval('setAttr "rIndex2.rotateX" 0.31')
        mel.eval('setAttr "rIndex2.rotateY" 4.02')
        mel.eval('setAttr "rIndex2.rotateZ" -1.4')

        mel.eval('setAttr "lIndex3.rotateX" 2.13')
        mel.eval('setAttr "lIndex3.rotateY" -2.89')
        mel.eval('setAttr "lIndex3.rotateZ" 0.5')

        mel.eval('setAttr "rIndex3.rotateX" 2.13')
        mel.eval('setAttr "rIndex3.rotateY" 2.89')
        mel.eval('setAttr "rIndex3.rotateZ" -0.5')

        mel.eval('setAttr "lCarpal2.rotateX" 0.0')
        mel.eval('setAttr "lCarpal2.rotateY" -0.0')
        mel.eval('setAttr "lCarpal2.rotateZ" -0.0')

        mel.eval('setAttr "rCarpal2.rotateX" 0.0')
        mel.eval('setAttr "rCarpal2.rotateY" 0.0')
        mel.eval('setAttr "rCarpal2.rotateZ" 0.0')

        mel.eval('setAttr "lMid1.rotateX" -0.08')
        mel.eval('setAttr "lMid1.rotateY" 4.74')
        mel.eval('setAttr "lMid1.rotateZ" -1.14')

        mel.eval('setAttr "rMid1.rotateX" -0.08')
        mel.eval('setAttr "rMid1.rotateY" -4.74')
        mel.eval('setAttr "rMid1.rotateZ" 1.14')

        mel.eval('setAttr "lMid2.rotateX" 0.23')
        mel.eval('setAttr "lMid2.rotateY" 3.23')
        mel.eval('setAttr "lMid2.rotateZ" 7.72')

        mel.eval('setAttr "rMid2.rotateX" 0.23')
        mel.eval('setAttr "rMid2.rotateY" -3.23')
        mel.eval('setAttr "rMid2.rotateZ" -7.72')

        mel.eval('setAttr "lMid3.rotateX" 0.0')
        mel.eval('setAttr "lMid3.rotateY" -6.76')
        mel.eval('setAttr "lMid3.rotateZ" -6.91')

        mel.eval('setAttr "rMid3.rotateX" 0.0')
        mel.eval('setAttr "rMid3.rotateY" 6.76')
        mel.eval('setAttr "rMid3.rotateZ" 6.91')

        mel.eval('setAttr "lCarpal3.rotateX" 0.0')
        mel.eval('setAttr "lCarpal3.rotateY" -0.0')
        mel.eval('setAttr "lCarpal3.rotateZ" 0.0')

        mel.eval('setAttr "rCarpal3.rotateX" 0.0')
        mel.eval('setAttr "rCarpal3.rotateY" 0.0')
        mel.eval('setAttr "rCarpal3.rotateZ" -0.0')

        mel.eval('setAttr "lRing1.rotateX" -0.12')
        mel.eval('setAttr "lRing1.rotateY" 0.03')
        mel.eval('setAttr "lRing1.rotateZ" 2.52')

        mel.eval('setAttr "rRing1.rotateX" -0.12')
        mel.eval('setAttr "rRing1.rotateY" -0.03')
        mel.eval('setAttr "rRing1.rotateZ" -2.52')

        mel.eval('setAttr "lRing2.rotateX" -3.68')
        mel.eval('setAttr "lRing2.rotateY" 0.14')
        mel.eval('setAttr "lRing2.rotateZ" 3.24')

        mel.eval('setAttr "rRing2.rotateX" -3.68')
        mel.eval('setAttr "rRing2.rotateY" -0.14')
        mel.eval('setAttr "rRing2.rotateZ" -3.24')

        mel.eval('setAttr "lRing3.rotateX" 0.07')
        mel.eval('setAttr "lRing3.rotateY" -1.88')
        mel.eval('setAttr "lRing3.rotateZ" -2.16')

        mel.eval('setAttr "rRing3.rotateX" 0.07')
        mel.eval('setAttr "rRing3.rotateY" 1.88')
        mel.eval('setAttr "rRing3.rotateZ" 2.16')

        mel.eval('setAttr "lCarpal4.rotateX" 0.0')
        mel.eval('setAttr "lCarpal4.rotateY" 0.0')
        mel.eval('setAttr "lCarpal4.rotateZ" 6.12')

        mel.eval('setAttr "rCarpal4.rotateX" 0.0')
        mel.eval('setAttr "rCarpal4.rotateY" -0.0')
        mel.eval('setAttr "rCarpal4.rotateZ" -6.12')

        mel.eval('setAttr "lPinky1.rotateX" -0.47')
        mel.eval('setAttr "lPinky1.rotateY" -3.69')
        mel.eval('setAttr "lPinky1.rotateZ" -3.95')

        mel.eval('setAttr "rPinky1.rotateX" -0.47')
        mel.eval('setAttr "rPinky1.rotateY" 3.69')
        mel.eval('setAttr "rPinky1.rotateZ" 3.95')

        mel.eval('setAttr "lPinky2.rotateX" 4.06')
        mel.eval('setAttr "lPinky2.rotateY" 0.44')
        mel.eval('setAttr "lPinky2.rotateZ" 0.13')

        mel.eval('setAttr "rPinky2.rotateX" 4.06')
        mel.eval('setAttr "rPinky2.rotateY" -0.44')
        mel.eval('setAttr "rPinky2.rotateZ" -0.13')

        mel.eval('setAttr "lPinky3.rotateX" 0.0')
        mel.eval('setAttr "lPinky3.rotateY" -1.88')
        mel.eval('setAttr "lPinky3.rotateZ" 0.0')

        mel.eval('setAttr "rPinky3.rotateX" 0.0')
        mel.eval('setAttr "rPinky3.rotateY" 1.88')
        mel.eval('setAttr "rPinky3.rotateZ" -0.0')
        '''
        mel.eval('setAttr "lFoot.rotateX" 0.64')
        mel.eval('setAttr "lFoot.rotateY" -12.87')
        mel.eval('setAttr "lFoot.rotateZ" 5.7')

        mel.eval('setAttr "rFoot.rotateX" 0.64')
        mel.eval('setAttr "rFoot.rotateY" 12.87')
        mel.eval('setAttr "rFoot.rotateZ" -5.7')
        '''
    except:
        print("Gen3RotsFix...")


# TODO: Remove hardocing
def gen8_rotations_fix():
    # ---------------------------------------------------------
    try:
        mel.eval('setAttr "lShldrBend.rotateX" 0.0')
        mel.eval('setAttr "lShldrBend.rotateY" 0.0')
        mel.eval('setAttr "lShldrBend.rotateZ" 48.24')
        # 45.75

        mel.eval('setAttr "rShldrBend.rotateX" 0.0')
        mel.eval('setAttr "rShldrBend.rotateY" -0.0')
        mel.eval('setAttr "rShldrBend.rotateZ" -48.24')

        mel.eval('setAttr "lForearmBend.rotateX" 1.16')
        mel.eval('setAttr "lForearmBend.rotateY" 15.49')
        mel.eval('setAttr "lForearmBend.rotateZ" -4.2')

        mel.eval('setAttr "rForearmBend.rotateX" 1.16')
        mel.eval('setAttr "rForearmBend.rotateY" -15.49')
        mel.eval('setAttr "rForearmBend.rotateZ" 4.2')

        mel.eval('setAttr "lHand.rotateX" 0.0')
        mel.eval('setAttr "lHand.rotateY" -13.76')
        mel.eval('setAttr "lHand.rotateZ" 0.0')

        mel.eval('setAttr "rHand.rotateX" 0.0')
        mel.eval('setAttr "rHand.rotateY" 13.76')
        mel.eval('setAttr "rHand.rotateZ" -0.0')

        mel.eval('setAttr "lThumb1.rotateX" -0.0')
        mel.eval('setAttr "lThumb1.rotateY" -0.0')
        mel.eval('setAttr "lThumb1.rotateZ" -0.0')

        mel.eval('setAttr "rThumb1.rotateX" -0.0')
        mel.eval('setAttr "rThumb1.rotateY" 0.0')
        mel.eval('setAttr "rThumb1.rotateZ" 0.0')

        mel.eval('setAttr "lThumb2.rotateX" -0.0')
        mel.eval('setAttr "lThumb2.rotateY" -0.0')
        mel.eval('setAttr "lThumb2.rotateZ" -0.0')

        mel.eval('setAttr "rThumb2.rotateX" -0.0')
        mel.eval('setAttr "rThumb2.rotateY" 0.0')
        mel.eval('setAttr "rThumb2.rotateZ" 0.0')

        mel.eval('setAttr "lThumb3.rotateX" -0.0')
        mel.eval('setAttr "lThumb3.rotateY" -0.0')
        mel.eval('setAttr "lThumb3.rotateZ" -0.0')

        mel.eval('setAttr "rThumb3.rotateX" -0.0')
        mel.eval('setAttr "rThumb3.rotateY" 0.0')
        mel.eval('setAttr "rThumb3.rotateZ" 0.0')

        mel.eval('setAttr "lCarpal1.rotateX" -0.0')
        mel.eval('setAttr "lCarpal1.rotateY" -0.0')
        mel.eval('setAttr "lCarpal1.rotateZ" -0.0')

        mel.eval('setAttr "rCarpal1.rotateX" -0.0')
        mel.eval('setAttr "rCarpal1.rotateY" 0.0')
        mel.eval('setAttr "rCarpal1.rotateZ" 0.0')

        mel.eval('setAttr "lIndex1.rotateX" -0.0')
        mel.eval('setAttr "lIndex1.rotateY" 0.0')
        mel.eval('setAttr "lIndex1.rotateZ" -0.0')

        mel.eval('setAttr "rIndex1.rotateX" -0.0')
        mel.eval('setAttr "rIndex1.rotateY" -0.0')
        mel.eval('setAttr "rIndex1.rotateZ" 0.0')

        mel.eval('setAttr "lIndex2.rotateX" -0.0')
        mel.eval('setAttr "lIndex2.rotateY" -0.0')
        mel.eval('setAttr "lIndex2.rotateZ" -0.0')

        mel.eval('setAttr "rIndex2.rotateX" -0.0')
        mel.eval('setAttr "rIndex2.rotateY" 0.0')
        mel.eval('setAttr "rIndex2.rotateZ" 0.0')

        mel.eval('setAttr "lIndex3.rotateX" -0.0')
        mel.eval('setAttr "lIndex3.rotateY" -0.0')
        mel.eval('setAttr "lIndex3.rotateZ" -0.0')

        mel.eval('setAttr "rIndex3.rotateX" -0.0')
        mel.eval('setAttr "rIndex3.rotateY" 0.0')
        mel.eval('setAttr "rIndex3.rotateZ" 0.0')

        mel.eval('setAttr "lCarpal2.rotateX" -0.0')
        mel.eval('setAttr "lCarpal2.rotateY" 0.0')
        mel.eval('setAttr "lCarpal2.rotateZ" -0.0')

        mel.eval('setAttr "rCarpal2.rotateX" -0.0')
        mel.eval('setAttr "rCarpal2.rotateY" -0.0')
        mel.eval('setAttr "rCarpal2.rotateZ" 0.0')

        mel.eval('setAttr "lMid1.rotateX" -0.0')
        mel.eval('setAttr "lMid1.rotateY" -0.0')
        mel.eval('setAttr "lMid1.rotateZ" -0.0')

        mel.eval('setAttr "rMid1.rotateX" -0.0')
        mel.eval('setAttr "rMid1.rotateY" 0.0')
        mel.eval('setAttr "rMid1.rotateZ" 0.0')

        mel.eval('setAttr "lMid2.rotateX" -0.0')
        mel.eval('setAttr "lMid2.rotateY" -0.0')
        mel.eval('setAttr "lMid2.rotateZ" 0.0')

        mel.eval('setAttr "rMid2.rotateX" -0.0')
        mel.eval('setAttr "rMid2.rotateY" 0.0')
        mel.eval('setAttr "rMid2.rotateZ" -0.0')

        mel.eval('setAttr "lMid3.rotateX" -0.0')
        mel.eval('setAttr "lMid3.rotateY" -0.0')
        mel.eval('setAttr "lMid3.rotateZ" -0.0')

        mel.eval('setAttr "rMid3.rotateX" -0.0')
        mel.eval('setAttr "rMid3.rotateY" 0.0')
        mel.eval('setAttr "rMid3.rotateZ" 0.0')

        mel.eval('setAttr "lCarpal3.rotateX" -0.0')
        mel.eval('setAttr "lCarpal3.rotateY" 0.0')
        mel.eval('setAttr "lCarpal3.rotateZ" -0.0')

        mel.eval('setAttr "rCarpal3.rotateX" -0.0')
        mel.eval('setAttr "rCarpal3.rotateY" -0.0')
        mel.eval('setAttr "rCarpal3.rotateZ" 0.0')

        mel.eval('setAttr "lRing1.rotateX" -0.0')
        mel.eval('setAttr "lRing1.rotateY" 0.0')
        mel.eval('setAttr "lRing1.rotateZ" -0.0')

        mel.eval('setAttr "rRing1.rotateX" -0.0')
        mel.eval('setAttr "rRing1.rotateY" -0.0')
        mel.eval('setAttr "rRing1.rotateZ" 0.0')

        mel.eval('setAttr "lRing2.rotateX" -0.0')
        mel.eval('setAttr "lRing2.rotateY" 0.0')
        mel.eval('setAttr "lRing2.rotateZ" -0.0')

        mel.eval('setAttr "rRing2.rotateX" -0.0')
        mel.eval('setAttr "rRing2.rotateY" -0.0')
        mel.eval('setAttr "rRing2.rotateZ" 0.0')

        mel.eval('setAttr "lRing3.rotateX" -0.0')
        mel.eval('setAttr "lRing3.rotateY" 0.0')
        mel.eval('setAttr "lRing3.rotateZ" -0.0')

        mel.eval('setAttr "rRing3.rotateX" -0.0')
        mel.eval('setAttr "rRing3.rotateY" -0.0')
        mel.eval('setAttr "rRing3.rotateZ" 0.0')

        mel.eval('setAttr "lCarpal4.rotateX" -0.0')
        mel.eval('setAttr "lCarpal4.rotateY" 0.0')
        mel.eval('setAttr "lCarpal4.rotateZ" -0.0')

        mel.eval('setAttr "rCarpal4.rotateX" -0.0')
        mel.eval('setAttr "rCarpal4.rotateY" -0.0')
        mel.eval('setAttr "rCarpal4.rotateZ" 0.0')

        mel.eval('setAttr "lPinky1.rotateX" -0.0')
        mel.eval('setAttr "lPinky1.rotateY" -0.0')
        mel.eval('setAttr "lPinky1.rotateZ" -0.0')

        mel.eval('setAttr "rPinky1.rotateX" -0.0')
        mel.eval('setAttr "rPinky1.rotateY" 0.0')
        mel.eval('setAttr "rPinky1.rotateZ" 0.0')

        mel.eval('setAttr "lPinky2.rotateX" -0.0')
        mel.eval('setAttr "lPinky2.rotateY" -0.0')
        mel.eval('setAttr "lPinky2.rotateZ" 0.0')

        mel.eval('setAttr "rPinky2.rotateX" -0.0')
        mel.eval('setAttr "rPinky2.rotateY" 0.0')
        mel.eval('setAttr "rPinky2.rotateZ" -0.0')

        mel.eval('setAttr "lPinky3.rotateX" -0.0')
        mel.eval('setAttr "lPinky3.rotateY" -0.0')
        mel.eval('setAttr "lPinky3.rotateZ" 0.0')

        mel.eval('setAttr "rPinky3.rotateX" -0.0')
        mel.eval('setAttr "rPinky3.rotateY" 0.0')
        mel.eval('setAttr "rPinky3.rotateZ" -0.0')

        mel.eval('setAttr "lShin.rotateX" 0.0')
        mel.eval('setAttr "lShin.rotateY" -9.66')
        mel.eval('setAttr "lShin.rotateZ" 0.0')

        mel.eval('setAttr "rShin.rotateX" 0.0')
        mel.eval('setAttr "rShin.rotateY" 9.66')
        mel.eval('setAttr "rShin.rotateZ" -0.0')

        mel.eval('setAttr "lThighBend.rotateX" 0.54')
        mel.eval('setAttr "lThighBend.rotateY" -0.16')
        mel.eval('setAttr "lThighBend.rotateZ" -6.23')

        mel.eval('setAttr "rThighBend.rotateX" 0.54')
        mel.eval('setAttr "rThighBend.rotateY" 0.16')
        mel.eval('setAttr "rThighBend.rotateZ" 6.23')
        '''
        mel.eval('setAttr "lFoot.rotateX" -1.96')
        mel.eval('setAttr "lFoot.rotateY" -4.88')
        mel.eval('setAttr "lFoot.rotateZ" 3.53')

        mel.eval('setAttr "rFoot.rotateX" -1.96')
        mel.eval('setAttr "rFoot.rotateY" 4.88')
        mel.eval('setAttr "rFoot.rotateZ" -3.53')
        '''
    except:
        print("Gen8RotsFix...")


def gen8_mat_fix():
    try:
        mel.eval('setAttr "EyeMoisture.transparency" -type double3 1 1 1')
    except:
        pass
    try:
        mel.eval(
            'setAttr "EyeMoisture.specularColor" -type double3 0.279221 0.279221 0.279221')
    except:
        pass
    try:
        mel.eval('setAttr "EyeMoisture.cosinePower" 91.727273')
    except:
        pass
    try:
        mel.eval('setAttr "EyeMoisture.color" -type double3 1 1 1')
    except:
        pass
    try:
        mel.eval('setAttr "Cornea.cosinePower" 64.36364')
    except:
        pass
    try:
        mel.eval(
            'setAttr "Cornea.specularColor" -type double3 0.75974 0.75974 0.75974')
    except:
        pass
    try:
        mel.eval('setAttr "Cornea.transparency" -type double3 1 1 1')
    except:
        pass


def sentinel_extra_finger():
    mel.eval('select -r lThumb2')
    mel.eval('selectKey -clear')
    mel.eval('duplicate -rr')
    mel.eval('parent lThumb3 lThumb2')
    mel.eval('setAttr "lThumb3.translateX" 2.17')
    mel.eval('setAttr "lThumb3.translateY" -1.75')
    mel.eval('setAttr "lThumb3.translateZ" 0.65')
    mel.eval('select -r rThumb2')
    mel.eval('selectKey -clear')
    mel.eval('duplicate -rr')
    mel.eval('parent rThumb3 rThumb2')
    mel.eval('setAttr "rThumb3.translateX" -1.98')
    mel.eval('setAttr "rThumb3.translateY" -1.62')
    mel.eval('setAttr "rThumb3.translateZ" 0.53')


def remove_limits():
    meshes_list = mel.eval('ls -type joint')
    for mesh in meshes_list:
        mel.eval('transformLimits -rx -20 20 -erx 0 0 %s' % mesh)
        mel.eval('transformLimits -ry -20 20 -ery 0 0 %s' % mesh)
        mel.eval('transformLimits -rz -25 25 -erz 0 0 %s' % mesh)


def hide_root_bone():
    joints_list = mel.eval('ls -type joint')
    hide_joint = joints_list[0] + ".drawStyle"
    mel.eval('setAttr %s 2' % hide_joint)


def eyelash_fix_gen3():
    try:
        mel.eval('disconnectAttr m5philliplashes.outColor Eyelashes.color')
        mel.eval('setAttr "Eyelashes.color" -type double3 0 0 0')
    except:
        pass


def eyelash_fix():
    all_objects = mel.eval('ls')
    for obj in all_objects:
        try:
            if "Lashes" in obj:
                print("Texture: " + obj)
            if "lash" in obj:
                lash_mat = obj
                conn = cmds.listConnections(lash_mat+'.'+"color", type='file')
        except:
            pass

    # disconnectAttr M5PhillipLashes.outColor FBXASC054_Eyelash.color;
    try:
        mel.eval('disconnectAttr %s.outColor %s.color' % (conn[0], lash_mat))
        mel.eval('setAttr "%s.color" -type double3 0.051 0.051 0.051'
                    % lash_mat)
    except:
        pass


def clean_mat_names():
    try:
        mats = mel.eval('ls -type "phong"')
        for mat in mats:
            try:
                mat_split = mat.split("_")
                mel.eval('rename %s %s' % (mat, mat_split[1]))
            except:
                pass
    except:
        print("no std mats")


def clean_namespace():
    joints_list = mel.eval('ls -type joint')
    for joint in joints_list:
        if ":" in joint:
            try:
                print("Namespace detected, try cleaning")
                joint_split = joint.split(":")
                mel.eval(
                        'namespace -mergeNamespaceWithRoot -removeNamespace %s'
                        % joint_split[0]
                    )
            except:
                print("namespace msg finished")
    print("namespace fix finished")


def scene_renamer():
    objs = mel.eval('ls')
    for obj in objs:
        obj_modified = obj.replace("FBXASC045", "_")
        obj_modified = obj.replace("FBXASC046", "_")

        obj_modified = obj_modified.replace("ShapeShapeOrig", "Shape")
        obj_modified = obj_modified.replace("ShapeShape", "Shape")
        obj_modified = obj_modified.replace("_Shape", "")
        obj_modified = obj_modified.replace("Shape", "")
        obj_modified = obj_modified.replace("FBXASC032", "_")
        obj_modified = obj_modified.replace("FBXASC048", "_0")
        obj_modified = obj_modified.replace("FBXASC049", "_1")
        obj_modified = obj_modified.replace("FBXASC050", "_2")
        obj_modified = obj_modified.replace("FBXASC051", "_3")
        obj_modified = obj_modified.replace("FBXASC052", "_4")
        obj_modified = obj_modified.replace("FBXASC053", "_5")
        obj_modified = obj_modified.replace("FBXASC054", "_6")
        obj_modified = obj_modified.replace("FBXASC055", "_7")
        obj_modified = obj_modified.replace("FBXASC056", "_8")
        obj_modified = obj_modified.replace("FBXASC057", "_9")

        #print obj + "  ---  " + obj_modified
        if obj == obj_modified:
            pass
        else:
            try:
                cmds.rename(obj, obj_modified)
            except:
                pass


def auto_ik():

    # cmds.scriptEditorInfo(suppressWarnings=True)
    # cmds.scriptEditorInfo(suppressErrors=True)

    try:
        pm.setAttr("defaultRenderGlobals.currentRenderer", "mayaSoftware")
        mel.eval('FrameAllInAllViews;')
    except:
        print("Can't set Software Render")

    joints_list = mel.eval('ls -type joint')

    count = 0
    for joint in joints_list:
        if "hip" in joint:
            count += 1

    if count > 10000000:
        error_msg = "Not valid Scene... possible solution: \nWhen export chose 'Merge Clothing Into Figure Skeleton' \nFor more info read the documentation"

        result = cmds.confirmDialog(
                                    title='DazToMaya: Not Valid Scene',
                                    message=error_msg,
                                    button=['Ok', 'View Info'],
                                    defaultButton='Yes',
                                    cancelButton='No',
                                    dismissString='No'
                                )

    else:
        try:
            mel.eval('setAttr "Cornea.transparency" -type double3 1 1 1')
            mel.eval('setAttr "EyeMoisture.transparency" -type double3 1 1 1')
        except:
            pass
        clean_namespace()
        clean_mat_names()
        eyelash_fix()
        eyelash_fix_gen3()
        hide_root_bone()
        try:
            remove_limits()
        except:
            pass

        # ROTATIONS FIX-----------------------------------
        #jointsList = mel.eval('ls -type joint')
        daz_figure = "Not Detected"
        if "Genesis" in joints_list:
            daz_figure = "Genesis1"
            gen1_rotations_fix()
        for joint in joints_list:
            if "Genesis2" in joint:
                gen2_rotations_fix()
                daz_figure = "Genesis2"
                break
            if "Genesis3" in joint:
                gen3_rotations_fix()
                daz_figure = "Genesis3"
                break
            if "SENTINEL" in joint:
                sentinel_extra_finger()
                sentinel_rotations_fix()
                daz_figure = "Sentinel"
                break
            if "Genesis8" in joint and not "Genesis8_1" in joint:

                try:
                    gen8_mat_fix()
                except:
                    pass
                try:
                    gen8_rotations_fix()
                except:
                    pass

                try:
                    mel.eval('setAttr "Genesis8Female.drawStyle" 2')
                except:
                    pass
                try:
                    mel.eval('setAttr "Genesis8Male.drawStyle" 2')
                except:
                    pass

                daz_figure = "Genesis8"
                break

            if "Genesis8" in joint and "Genesis8_1" in joint:

                try:
                    gen8_mat_fix()
                except:
                    pass
                try:
                    gen8_rotations_fix()
                except:
                    pass

                try:
                    mel.eval('setAttr "Genesis8_1Female.drawStyle" 2')
                except:
                    pass
                try:
                    mel.eval('setAttr "Genesis8_1Male.drawStyle" 2')
                except:
                    pass

                daz_figure = "Genesis8_1"
                break


        # -----Probar forzar ojos correctos...... agregado para male3 lion-o...
        gen8_mat_fix()

        # ROTATIONS FIX-----------------------------------
        print("------------------------------------")
        print("------------------------------------")
        clamp_textures()
        transparency_fix()

        try:
            morphs.fix_morphs()
        except:
            pass

        scene_modified_check()
        remove_hidden_objs()

        mel.eval('modelEditor -e -displayTextures true modelPanel4')

        if daz_figure == "Sentinel":
            sentinel_remove_finger()

        try:
            mel.eval('modelEditor -e -displayTextures true modelPanel4')
        except:
            pass
        try:
            mel.eval('setAttr "Genesis3Male.drawStyle" 2')
        except:
            pass
        try:
            mel.eval('setAttr "Genesis3Female.drawStyle" 2')
        except:
            pass

        extend_hand_fingers()
        try:
            mel.eval('HIKCharacterControlsTool')
            mel.eval('hikCreateDefinition()')
        except:
            pass

        try:
            compensate_hip()
        except:
            pass
        try:
            daz_to_ik()
        except:
            pass

        mel.eval('hikCreateControlRig')

        scalp_fix()
        lash_fix_2()
        gen8_lagrimal_fix()

        # maya2018_fix()

        cmds.scriptEditorInfo(suppressWarnings=False)
        cmds.scriptEditorInfo(suppressErrors=False)


def remove_joints_if_prop(parentObj):
    cacaChilds = cmds.listRelatives(parentObj, allDescendents=True)
    if "hip" not in cacaChilds:
        for x in cacaChilds:
            if cmds.objectType(x) == "joint":
                try:
                    cmds.delete(x)
                except:
                    pass
        pass


def group_stuff(parent_obj):
    group_name = parent_obj
    group_childs = cmds.listRelatives(group_name, allDescendents=True)
    cmds.spaceLocator(name=group_name+"_Group", p=[0, 0, 0])
    if len(group_childs) > 1:
        for o in group_childs:
            try:
                cmds.parent(o, world=True)
                cmds.parent(o, group_name+"_Group")
            except:
                pass


def get_parents_list():
    parents_list = []
    objs_and_joints = mel.eval('ls')
    for x in objs_and_joints:
        try:
            parents = cmds.ls(x, long=True)[0].split('|')[1:-1]
            if len(parents) == 1:
                parents_list.append(parents[0])
        except:
            pass
    return parents_list


def group_props():
    parents_list = get_parents_list()
    for x in parents_list:
        try:
            group_childs = cmds.listRelatives(x, allDescendents=True)
            if "hip" not in group_childs:
                if len(group_childs) > 1:
                    remove_joints_if_prop(x)
                    group_stuff(x)
                    try:
                        cmds.delete(x)
                    except:
                        pass
        except:
            pass


def remove_displacement_maps():
    mats = mel.eval('ls -type "displacementShader"')
    try:
        for m in mats:
            try:
                cmds.delete(m)
            except:
                pass
    except:
        pass


def break_connection_from_materials(matAttribute):
    try:
        mats = mel.eval('ls -type "phong"')
        connections = cmds.listConnections(mats, d=0, s=1, c=1, p=1)
        for i in range(0, len(connections), 2):
            if connections[i].rsplit('.', 1)[1] == matAttribute:
                cmds.disconnectAttr(connections[i+1], connections[i])
    except:
        pass


def import_fbx(daz_file_path):
    mel.eval('FBXImportMode -v Add')
    mel.eval('FBXImportMergeAnimationLayers -v false')
    mel.eval('FBXImportProtectDrivenKeys -v true')
    mel.eval('FBXImportConvertDeformingNullsToJoint -v true')
    mel.eval('FBXImportMergeBackNullPivots -v false')
    mel.eval('FBXImportSetLockedAttribute -v true')
    mel.eval('FBXImportConstraints -v false')
    # mel.eval('FBXImportConvertUnitString dm') --SCALE FIX?....... CHELO

    scale_menu_value = cmds.optionMenu("scaleMenu", query=True, value=True)
    if scale_menu_value == "Automatic":
        # FORCE cm Correct Unit....... CHELO
        mel.eval('FBXImportConvertUnitString cm')
    if scale_menu_value == "x1 (default)":
        # FORCE cm Correct Unit....... CHELO
        mel.eval('FBXImportConvertUnitString cm')
    if scale_menu_value == "x10 (biger)":
        # FORCE cm Correct Unit....... CHELO
        mel.eval('FBXImportConvertUnitString mm')
    if scale_menu_value == "x0.1 (small)":
        # FORCE cm Correct Unit....... CHELO
        mel.eval('FBXImportConvertUnitString dm')
    if scale_menu_value == "x0.01 (smaller)":
        # FORCE cm Correct Unit....... CHELO
        mel.eval('FBXImportConvertUnitString m')

    daz_file_path = daz_file_path.replace('\\', '/')
    import_cmd = "FBXImport -f \"" + daz_file_path + "\""
    mel.eval(import_cmd)


def auto_import_daz():

    # Importing only first figure for now
    daz_file_path = os.path.abspath(Definitions.EXPORT_DIR + "/FIG/FIG0/B_FIG.fbx")

    # exit if file not found
    if os.path.exists(daz_file_path) == False:
        open_import_not_found_window()
        return

    # Create a new scene or merge to existing one based on the check box
    merge_scene = cmds.checkBox(check_box_merge, query=True, value=True)
    if merge_scene == False:
        result = mel.eval("saveChanges(\"file -f -new\")")
        if result == 0:
            return
        else:
            cmds.NewScene()

    # Load and show wait dialog
    wait_dialog = WaitDialog()
    wait_dialog.show()

    # Refresh and import Fbx
    print("Importing Daz...")
    cmds.refresh()
    import_fbx(daz_file_path)
    print("AutoIK...")

    try:
        pm.setAttr("defaultRenderGlobals.currentRenderer", "mayaSoftware")
    except:
        pass

    break_connection_from_materials("specularColor")
    remove_displacement_maps()

    # Auto IK if figure in the scene, else it is a Prop
    all_joints = mel.eval('ls -type joint')
    group_props()
    if all_joints != None and "head" in all_joints:
        auto_ik()
    else:
        mel.eval('viewFit -all')  # View Fit All
        clamp_textures()
        try:
            mel.eval('modelEditor -e -displayTextures true modelPanel4')
        except:
            pass

    try:
        wait_dialog.close()
    except:
        pass

    cmds.refresh()

    scene_renamer()
    mat_refresh_fix()
    # Show remember to save with textures...
    try:
        if cmds.checkBox(check_box_save, query=True, value=True) == True:
            open_ask_to_save_window()
    except:
        pass

    print("DazToMaya Complete!")


# --------- Initialize ----------


def d2mstart():
    print("d2m start")

    maya_version = cmds.about(v=True)
#    if "2014" in maya_version or "2015" in maya_version or "2016" in maya_version or "2017" in maya_version or "2018" in maya_version or "2019" in maya_version or "2020" in maya_version or "2022" in maya_version:
    if int(maya_version) >= 2014:
        cmds.showWindow(window_daz_main)
        cmds.window(window_name, edit=True, widthHeight=(343, 470))
    else:
        print("Maya Version not Supported. Please visit www.daz3d.com")


def initialize():
    """
    Initialize and lauch UI window
    """
    global cfg_settings
    global figure

    print(sys.platform)

    # Get settings configuration
    with open(txtConf, 'r') as output:
        cfg_settings = output.read()

    # Detect figure Gen2 male or female
    objs = mel.eval('ls')
    for o in objs:
        if o.find("Genesis2Female") == 0:
            figure = "Genesis2MaleFBXASC046Shape"
        if o.find("Genesis2Female") == 0:
            figure = "Genesis2FemaleFBXASC046Shape"

    # Clear the active list
    mel.eval('select -cl')

    # Try loading mtoa (arnold) plugin if its not loaded yet
    if not cmds.pluginInfo('mtoa', query=True, loaded=True):
        try:
            cmds.loadPlugin('mtoa')
        except:
            pass

    open_main_window()
    d2mstart()
    # d2m58-mac


# ----------- UI --------------


def open_main_window():
    """
    Open main dialogue window for Daz to Maya
    """

    global window_daz_main
    global check_box_save
    global check_box_merge

    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)

    window_daz_main = cmds.window(
                                    window_name,
                                    toolbox=True,
                                    maximizeButton=False,
                                    minimizeButton=True,
                                    sizeable=False,
                                    title="DazToMaya 2022.1"
                                )

    cmds.columnLayout("columnName01", adjustableColumn=True)

    # Banner
    cmds.separator(height=5, style='none')
    cmds.image(image=d2m_banner)
    cmds.separator(height=10, style='in')

    # Import settings
    cmds.rowColumnLayout(
                            numberOfColumns=2,
                            columnWidth=[(1, 200), (2, 120)],
                            columnSpacing=[(1, 6), (2, 0)]
                        )
    label_text = "Merge Import to current scene"
    check_box_merge = cmds.checkBox(label=label_text, value=0)
    cmds.optionMenu("scaleMenu", w=130, label="  Scale:")
    cmds.menuItem(label="Automatic")
    cmds.menuItem(label="x10 (biger)")
    cmds.menuItem(label="x1 (default)")
    cmds.menuItem(label="x0.1 (small)")
    cmds.menuItem(label="x0.01 (smaller)")
    cmds.setParent('..')
    cmds.separator(height=5, style='none')

    cmds.button(
                    label='Auto-Import',
                    width=343,
                    height=50,
                    c=lambda *args: auto_import_daz()
                )
    cmds.separator(height=20, style='in')

    label_text = "If importing from Temp folder, save to another location (!)"
    cmds.text(label=label_text, align='center')
    cmds.separator(height=8, style='none')

    # Import button
    cmds.button(
                    label='Save Scene with Textures...',
                    width=343,
                    height=45,
                    c=lambda *args: btn_save_with_text_callback()
                )
    cmds.separator(height=5, style='none')

    # Check box to show popup for saving textures
    cmds.columnLayout("CheckBoxColumn", columnOffset=("left", 10))
    check_box_status = 0
    if "askToSaveSceneWithTextures=0" in cfg_settings:
        check_box_status = 0
    elif "askToSaveSceneWithTextures=1" in cfg_settings:
        check_box_status = 1
    check_box_label = "Show me a reminder after importing from Temp folder."
    check_box_save = cmds.checkBox(
                                label=check_box_label,
                                changeCommand=lambda *args: config_save_callback(),
                                value=check_box_status
                            )
    cmds.setParent('..')
    cmds.separator(height=15, style='in')

    # Convert materials button section
    cmds.rowColumnLayout(
                            numberOfColumns=3,
                            columnWidth=[(1, 225), (2, 8), (3, 95)],
                            columnSpacing=[(1, 6), (2, 0)]
                        )
    cmds.button(
                    label='Convert Materials',
                    width=43,
                    height=25,
                    c=lambda *args: btn_convert_callback()
                )
    cmds.separator(height=8, style='none')
    cmds.optionMenu("matConvertMenu", w=50, label="")
    cmds.menuItem(label="Arnold")
    cmds.menuItem(label="Vray")
    cmds.setParent('..')
    cmds.separator(height=20, style='in')

    # Global skin paramters section
    cmds.text(label='  Global Skin Parameters:', align='left')
    cmds.separator(height=5, style='none')
    cmds.floatSliderGrp(
                            'SpecWeight',
                            label='Specular Weight',
                            field=True,
                            precision=2,
                            value=0,
                            minValue=0,
                            maxValue=1,
                            dc=slider_drag_callback
                        )
    cmds.floatSliderGrp(
                            'SpecRough',
                            label='Specular Roughness',
                            field=True,
                            precision=2,
                            value=0,
                            minValue=0,
                            maxValue=1,
                            dc=slider_drag_callback
                        )
    cmds.separator(height=18, style='in')

    # Copyright section
    cmds.separator(height=5, style='none')
    cmds.rowColumnLayout(
                            numberOfColumns=4,
                            columnWidth=[(1, 43), (2, 200), (3, 50), (4, 50)]
                        )
    cmds.separator(style='none')
    cmds.text(label='Copyright (c) 2020. All Rights Reserved.')
    cmds.iconTextButton(
                            width=24,
                            height=24,
                            style='iconOnly',
                            image=d2m_help_icon,
                            annotation="DazToMaya: Help and Tutorials", c=lambda *args: btn_go_help_callback()
                        )
    cmds.separator(style='none')
    cmds.setParent('..')
    cmds.separator(height=5, style='none')


def btn_save_with_text_callback():
    try:
        cmds.deleteUI(ask_to_save_window_name)
    except:
        pass
    multiple_filters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb)"
    save_file_result = cmds.fileDialog2(
                                        fileFilter=multiple_filters,
                                        dialogStyle=2
                                    )

    if save_file_result != None:
        out_path = os.path.dirname(save_file_result[0]) + "/"

        try:
            os.makedirs(out_path + "/images")
        except:
            pass

        texture_file_nodes = pm.ls(typ='file')
        for file_node in texture_file_nodes:
            print(file_node)
            image_path = file_node.getAttr('fileTextureName')
            just_file_name = os.path.basename(image_path)
            out_file_name = out_path + "images/" + str(just_file_name)
            if image_path != out_file_name:
                from shutil import copyfile
                copyfile(image_path, out_file_name)
                file_node.setAttr('fileTextureName',
                                 "images/" + str(just_file_name))

        cmds.file(rename=save_file_result[0])
        if ".ma" in save_file_result[0]:
            cmds.file(save=True, type="mayaAscii")
        else:
            cmds.file(save=True, type="mayaBinary")


def btn_convert_callback():

    mat_conv = cmds.optionMenu("matConvertMenu", query=True, value=True)
    mats = mel.eval('ls -type "phong"')
    if mats == None or len(mats) < 1:
        errormsg = "Re-Convert Materials not supported yet:\nOriginal materials were already changed.\nImport again and convert to other material if needed."
        result = cmds.confirmDialog(
                                        title='DazToMaya',
                                        message=errormsg,
                                        button=['Ok'],
                                        defaultButton='Yes',
                                        cancelButton='No',
                                        dismissString='No'
                                    )
    else:
        if mat_conv == "Arnold":
            pm.setAttr("defaultRenderGlobals.currentRenderer", "arnold")
            # convert_all_to_arnold_daz_fixes()
            dzm.DazMaterials().convert_to_arnold()


        if mat_conv == "Vray":
            ConvertToVray().start_convert()
            eyelashes_fix1()
            eyelashes_fix2()
            extra_eye_fixes()
            vray_fixes()
            print("Convert Done")


def config_save_callback():
    try:
        if cmds.checkBox(check_box_save, q=True, value=True) == True:
            config_ask_to_save(1)
        else:
            config_ask_to_save(0)
    except:
        pass


def slider_drag_callback(*args):
    valor_spec_weight = cmds.floatSliderGrp(
                                                'SpecWeight', query=True,
                                                value=True
                                            )
    valor_spec_rough = cmds.floatSliderGrp('SpecRough', query=True, value=True)

    human_mats = (
                    "Skin",
                    "SkinFace",
                    "Face",
                    "Nipple",
                    "Head",
                    "Neck",
                    "Ears",
                    "Torso",
                    "Hips",
                    "Shoulders",
                    "Arms",
                    "Forearms",
                    "Nipples",
                    "Hands",
                    "Legs",
                    "Feet"
                )
    scene_mats = mel.eval('ls -mat')
    skin_mats = []
    for m in scene_mats:
        for h in human_mats:
            if h in m:
                if m not in skin_mats:
                    skin_mats.append(m)
    i = 0
    for o in skin_mats:
        # STANDARD--------------------------------------------------------------------------------
        try:
            # Arnold - Specular Weight
            obj_attr_spec_weight = skin_mats[i] + ".specularColor"
            cmds.setAttr(obj_attr_spec_weight, valor_spec_weight*2,
                         valor_spec_weight*2, valor_spec_weight*2)
        except:
            pass
        try:
            # Arnold - Specular Roughness
            obj_attr_spec_rough = skin_mats[i] + ".cosinePower"
            cmds.setAttr(obj_attr_spec_rough, 100 - (valor_spec_rough * 100))
        except:
            pass
        # ----------------------------------------------------------------------------------------
        # ARNOLD--------------------------------------------------------------------------------
        try:
            obj_attr_spec_weight = skin_mats[i] + ".Ks"  # Arnold - Specular Weight
            cmds.setAttr(obj_attr_spec_weight, valor_spec_weight)
        except:
            pass
        try:
            # Arnold - Specular Roughness
            obj_attr_spec_rough = skin_mats[i] + ".specularRoughness"
            cmds.setAttr(obj_attr_spec_rough, valor_spec_rough)
        except:
            pass
        # ----------------------------------------------------------------------------------------
        # VRAY--------------------------------------------------------------------------------
        try:
            # Arnold - Specular Weight
            obj_attr_spec_weight = skin_mats[i] + ".reflectionColorAmount"
            cmds.setAttr(obj_attr_spec_weight, valor_spec_weight)
        except:
            pass
        try:
            # Arnold - Specular Roughness
            obj_attr_spec_rough = skin_mats[i] + ".reflectionGlossiness"
            cmds.setAttr(obj_attr_spec_rough, valor_spec_rough)
        except:
            pass
        # ----------------------------------------------------------------------------------------
        i = i + 1


def open_import_not_found_window():
    """
    Window dialog when the fbx to import is not found
    """
    window_name = "d2mErrorNoImport9"

    def close_error_window():
        try:
            cmds.deleteUI(window_name)
        except:
            pass

    close_error_window()
    cmds.window(
                    window_name,
                    toolbox=True,
                    maximizeButton=False,
                    minimizeButton=False,
                    sizeable=False,
                    title="DazToMaya: Oops! - Nothing to Import",
                    widthHeight=(672, 480)
                )
    not_found_logo = "d2m_err_nf.png"
    error_text = "Nothing to Import.\nPrepare your character in DAZ Studio and execute DazToMaya from there first."

    cmds.columnLayout("columnName01", adjustableColumn=True)
    cmds.separator(height=10, style='none')
    cmds.text(label=error_text, align='center')
    cmds.separator(height=5, style='none')
    cmds.image(image=not_found_logo, width=672)

    cmds.rowColumnLayout(
                            numberOfColumns=4,
                            columnWidth=[(1, 160), (2, 150), (3, 50)],
                            columnSpacing=[(1, 1), (2, 0)]
                        )
    cmds.separator(height=5, style='none')
    cmds.button(
                    label='Get Daz Studio',
                    width=150,
                    height=40,
                    c=lambda *args: go_to_daz_callback()
                )
    cmds.separator(height=5, style='none')
    cmds.button(
                    label='OK',
                    width=150,
                    height=40,
                    c=lambda *args: close_error_window()
                )
    cmds.showWindow(window_name)


def open_ask_to_save_window():
    try:
        cmds.deleteUI(ask_to_save_window_name)
    except:
        pass

    window_ask_to_save = cmds.window(
                                    ask_to_save_window_name,
                                    toolbox=True,
                                    maximizeButton=False,
                                    minimizeButton=False,
                                    sizeable=False,
                                    title="DazToMaya",
                                    widthHeight=(400, 200)
                                )

    cmds.columnLayout("columnName01", adjustableColumn=True)
    cmds.separator(height=10, style='none')

    cmds.text(label='Done!', font="boldLabelFont")
    cmds.separator(height=10, style='none')
    label_text = "To transfer from Daz Studio to Maya you are using a Temp folder, \nnow is a good time to save the scene+textures to another location."
    cmds.text(label=label_text)
    cmds.separator(height=10, style='none')

    cmds.button(
                    label='Save Scene with Textures...',
                    bgc=[0.5, 0.5, 0.0],
                    command=lambda *args: btn_save_with_text_callback(),
                    height=40
                )
    cmds.separator(height=10, style='none')
    label_text = "You only need to do this special save one time after import, \nso you don't depend on the Temp folder for this scene."
    cmds.text(label=label_text)

    cmds.separator(height=25, style='in')
    cmds.button(
                    label='Ok',
                    width=200,
                    c=lambda *args: close_ask_to_save_callback(),
                    height=20
                )

    cmds.showWindow(window_ask_to_save)


def close_ask_to_save_callback():
    try:
        cmds.deleteUI(ask_to_save_window_name)
    except:
        pass


def go_to_daz_callback():
    cmds.launch(web="https://www.daz3d.com/home")


def btn_go_help_callback():
    webbrowser.open(
        "http://docs.daz3d.com/doku.php/public/read_me/index/71381/start")


class WaitDialog(object):
    wait_window_name = "DazToMayaPleaseWait11"
    wait_window = None

    def __init__(self):
        if cmds.window(self.wait_window_name, exists=True):
            cmds.deleteUI(self.wait_window_name)
        self.wait_window = pm.window(
                                    self.wait_window_name,
                                    toolbox=True,
                                    maximizeButton=False,
                                    minimizeButton=False,
                                    sizeable=False,
                                    title="DazToMaya",
                                    widthHeight=(343, 55)
                                )
        cmds.columnLayout("columnName01", adjustableColumn=True)
        cmds.separator(height=20, style='in')
        cmds.text(label='Importing please wait...')
        cmds.separator(height=20, style='in')

    def show(self):
        self.wait_window.show()

    def close(self):
        pm.deleteUI(self.wait_window_name)


class ConvertToVray:
    target_shaders = ['phong']

    mapping_phong = [
        ['color', 'color'],
        ['transparency', 'opacityMap']
    ]

    def convert_ui(self):
        self.convert_all_shaders()
        # setupOpacities()

    def convert_all_shaders(self):
        """
        Converts each (in-use) material in the scene
        """
        # better to loop over the types instead of calling
        # ls -type targetShader
        # if a shader in the list is not registered (i.e. VrayMtl)
        # everything would fail

        for shd_type in self.target_shaders:
            shader_coll = cmds.ls(exactType=shd_type)
            if shader_coll:
                for x in shader_coll:
                    # query the objects assigned to the shader
                    # only convert things with members
                    shd_group = cmds.listConnections(x, type="shadingEngine")
                    set_mem = cmds.sets(shd_group, query=True)
                    if set_mem:
                        ret = self.do_mapping(x)

    def do_mapping(self, in_shd):
        """
        Figures out which attribute mapping to use, and does the thing.

        @param inShd: Shader name
        @type inShd: String
        """
        ret = None

        shader_type = cmds.objectType(in_shd)
        if 'phong' in shader_type:
            ret = self.shader_to_ai_standard(in_shd, 'VRayMtl', self.mapping_phong)
            self.convert_phong(in_shd, ret)

        if ret:
            # assign objects to the new shader
            self.assign_to_new_shader(in_shd, ret)

    def assign_to_new_shader(self, old_shd, new_shd):
        """
        Creates a shading group for the new shader, and assigns members of the old shader to it

        @param oldShd: Old shader to upgrade
        @type oldShd: String
        @param newShd: New shader
        @type newShd: String
        """

        ret_val = False

        shd_group = cmds.listConnections(old_shd, type="shadingEngine")

        if shd_group:
            print(">>>>>>>>" + new_shd)
            if "Eye" in new_shd:
                try:
                    # CHELO LINE...
                    cmds.connectAttr(
                                        new_shd + '.outColor',
                                        shd_group[0] + '.aiSurfaceShader',
                                        force=True
                                    )
                except:
                    pass
            else:
                try:
                    cmds.connectAttr(
                                        new_shd + '.outColor',
                                        shd_group[0] + '.surfaceShader',
                                        force=True
                                    )
                    cmds.delete(old_shd)
                except:
                    pass

            ret_val = True

        return ret_val

    def setup_connections(self, in_shd, from_attr, out_shd, to_attr):
        conns = cmds.listConnections(
                                        in_shd + '.' + from_attr,
                                        d=False,
                                        s=True,
                                        plugs=True
                                    )
        if conns:
            cmds.connectAttr(conns[0], out_shd + '.' + to_attr, force=True)
            return True

        return False

    def shader_to_ai_standard(self, in_shd, node_type, mapping):
        """
        'Converts' a shader to arnold, using a mapping table.

        @param inShd: Shader to convert
        @type inShd: String
        @param nodeType: Arnold shader type to create
        @type nodeType: String
        @param mapping: List of attributes to map from old to new
        @type mapping: List
        """

        # print 'Converting material:', inShd
        if ':' in in_shd:
            ai_name = in_shd.rsplit(':')[-1] + '_vr'
        else:
            ai_name = in_shd + '_vr'

        ai_node = cmds.shadingNode(node_type, name=ai_name, asShader=True)
        for chan in mapping:
            from_attr = chan[0]
            to_attr = chan[1]

            if cmds.objExists(in_shd + '.' + from_attr):
                if not self.setup_connections(in_shd, from_attr, ai_node, to_attr):
                    # copy the values
                    val = cmds.getAttr(in_shd + '.' + from_attr)
                    self.set_value(ai_node + '.' + to_attr, val)

        return ai_node

    def set_value(self, attr, value):
        """Simplified set attribute function.

        @param attr: Attribute to set. Type will be queried dynamically
        @param value: Value to set to. Should be compatible with the attr type.
        """

        a_type = None

        if cmds.objExists(attr):
            # temporarily unlock the attribute
            is_locked = cmds.getAttr(attr, lock=True)
            if is_locked:
                cmds.setAttr(attr, lock=False)

            # one last check to see if we can write to it
            if cmds.getAttr(attr, settable=True):
                attr_type = cmds.getAttr(attr, type=True)

                # print value, type(value)

                if attr_type in ['string']:
                    a_type = 'string'
                    cmds.setAttr(attr, value, type=a_type)

                elif attr_type in ['long', 'short', 'float', 'byte', 'double', 'doubleAngle', 'doubleLinear', 'bool']:
                    a_type = None
                    cmds.setAttr(attr, value)

                elif attr_type in ['long2', 'short2', 'float2',  'double2', 'long3', 'short3', 'float3',  'double3']:
                    if isinstance(value, float):
                        if attr_type in ['long2', 'short2', 'float2',  'double2']:
                            value = [(value, value)]
                        elif attr_type in ['long3', 'short3', 'float3',  'double3']:
                            value = [(value, value, value)]

                    cmds.setAttr(attr, *value[0], type=attr_type)

                # else:
                #    print 'cannot yet handle that data type!!'

            if is_locked:
                # restore the lock on the attr
                cmds.setAttr(attr, lock=True)

    def transparency_to_opacity(self, in_shd, out_shd):
        transp_map = cmds.listConnections(
            in_shd + '.transparency', d=False, s=True, plugs=True)
        if transp_map:
            # map is connected, argh...
            # need to add a reverse node in the shading tree

            # create reverse
            #invertNode = cmds.shadingNode('reverse', name=outShd + '_rev', asUtility=True)

            # connect transparency Map to reverse 'input'
            #cmds.connectAttr(transpMap[0], invertNode + '.input', force=True)

            # connect reverse to opacity

            #cmds.connectAttr(transpMap[0], outShd + '.opacityMap', force=True)
            try:
                print("-*-*-*-*-*-*-")
                print(transp_map[0])
                trans_map_to_invert = transp_map[0].replace(".outTransparency", "")
                mel.eval('setAttr "%s.invert" 1' % trans_map_to_invert)
            except:
                print("already inv")

    def convert_phong(self, in_shd, out_shd):
        cosine_power = cmds.getAttr(in_shd + '.cosinePower')
        roughness = math.sqrt(1.0 / (0.454 * cosine_power + 3.357))

        transp_values = cmds.getAttr(in_shd + '.transparency')
        caca2 = str(transp_values[0]).split(",")

        transp_r = float(str(caca2[0])[1:])
        transp_r = float(str(caca2[1])[1:])
        transp_b = float(str(caca2[2])[1:-1])

        #setValue(outShd + '.opacityMap', 1.0)
        try:
            cmds.setAttr(out_shd + '.' + "opacityMap", 1.0 - transp_r,
                         1.0 - transp_r, 1.0 - transp_b, type='double3')
        except:
            print("map detected")
        self.transparency_to_opacity(in_shd, out_shd)

    def convert_vray_mtl(self, inShd, outShd):

        # anisotropy from -1:1 to 0:1
        anisotropy = cmds.getAttr(inShd + '.anisotropy')
        anisotropy = (anisotropy * 2.0) + 1.0
        set_value(outShd + '.specularAnisotropy', anisotropy)

        # do we need to check lockFresnelIORToRefractionIOR
        # or is fresnelIOR modified automatically when refractionIOR changes ?
        ior = 1.0
        if cmds.getAttr(inShd + '.lockFresnelIORToRefractionIOR'):
            ior = cmds.getAttr(inShd + '.refractionIOR')
        else:
            ior = cmds.getAttr(inShd + '.fresnelIOR')

        reflectivity = 1.0
        conn_reflectivity = cmds.listConnections(
            outShd + '.Ks', d=False, s=True, plugs=True)
        if not conn_reflectivity:
            reflectivity = cmds.getAttr(outShd+'.Ks')

        front_refl = (ior - 1.0) / (ior + 1.0)
        front_refl *= front_refl

        set_value(outShd + '.Ksn', front_refl * reflectivity)

        refl_gloss = cmds.getAttr(inShd + '.reflectionGlossiness')
        set_value(outShd + '.specularRoughness', 1.0 - refl_gloss)

        refr_gloss = cmds.getAttr(inShd + '.refractionGlossiness')
        set_value(outShd + '.refractionRoughness', 1.0 - refr_gloss)

        # bumpMap, bumpMult, bumpMapType ?

        if cmds.getAttr(inShd + '.sssOn'):
            set_value(outShd + '.Ksss', 1.0)

        # selfIllumination is missing  but I need to know the exact attribute name in maya or this will fail

    def convert_options(self):
        cmds.setAttr("defaultArnoldRenderOptions.GIRefractionDepth", 10)

    def is_opaque(self, shapeName):

        my_sgs = cmds.listConnections(shapeName, type='shadingEngine')
        if not my_sgs:
            return 1

        surface_shader = cmds.listConnections(my_sgs[0] + ".aiSurfaceShader")

        if surface_shader == None:
            surface_shader = cmds.listConnections(my_sgs[0] + ".surfaceShader")

        if surface_shader == None:
            return 1

        for shader in surface_shader:
            if cmds.attributeQuery("opacity", node=shader, exists=True) == 0:
                continue

            opacity = cmds.getAttr(shader + ".opacity")

            if opacity[0][0] < 1.0 or opacity[0][1] < 1.0 or opacity[0][2] < 1.0:
                return 0

        return 1

    def setup_opacities(self):
        shapes = cmds.ls(type='geometryShape')
        for shape in shapes:

            if is_opaque(shape) == 0:
                # print shape + ' is transparent'
                cmds.setAttr(shape+".aiOpaque", 0)

    def start_convert(self):
        try:
            pm.setAttr("defaultRenderGlobals.currentRenderer", "vray")
        except:
            print("can't set Vray")
        try:
            mel.eval('setAttr "EyeMoisture.transparency" -type double3 1 1 1')
            mel.eval('setAttr "Cornea.transparency" -type double3 1 1 1')
        except:
            pass
        print("Done.")
        self.convert_ui()
