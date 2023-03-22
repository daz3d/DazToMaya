import os
import sys

import maya.cmds as cmds
import maya.api.OpenMaya as om2
import maya.mel as mel

import Definitions
import DtuLoader

if int(cmds.about(v=True)) > 2020:
    import importlib
    importlib.reload(Definitions)
    importlib.reload(DtuLoader)
else:
    reload(Definitions)
    reload(DtuLoader)

dtu_loader = None

def fix_morphs():
    """
    Add centralized morph controls using exported Dtu data and clean blendshapes
    """
    morph_links = load_morph_links()
    create_morphs_node(morph_links)
    create_custom_template(morph_links)
    clean_morphs()


def load_dtu():
    global dtu_loader
    dtu_path = os.path.abspath(Definitions.EXPORT_DIR + "\FIG\FIG0")
    dtu_loader = DtuLoader.DtuLoader(dtu_path)
    return dtu_loader

def load_morph_links():
    """
    Load morph links from Dtu file
    """
    global dtu_loader
    if dtu_loader is None:
        dtu_loader = load_dtu()
    morph_links = dtu_loader.get_morph_links_dict()
    return morph_links

def clean_name(blendtarget):
    if (blendtarget.find("__") > 1):
        bs_split = blendtarget.split("__")
        bs_fixed = blendtarget.replace(bs_split[0]+"__", "")
        return bs_fixed

def create_autojcm_node(joint_name, blendshape_target_dest, jcm_axis, joint_min, joint_max, blendshape_min, blendshape_max):
    # Create a setRange node to remap joint rotation to blendshape weight
    set_range_node = cmds.shadingNode("setRange", asUtility=True, name="JCM_" + joint_name)

    # Configure the setRange node
    cmds.setAttr(set_range_node + ".minX", blendshape_min)  # minimum output value
    cmds.setAttr(set_range_node + ".maxX", blendshape_max)  # maximum output value
    cmds.setAttr(set_range_node + ".oldMinX", joint_min)  # input value when the blendshape is not activated
    cmds.setAttr(set_range_node + ".oldMaxX", joint_max)  # input value when the blendshape is fully activated

    # Connect the joint rotation to the setRange input
    if jcm_axis == "XRotate":
        cmds.connectAttr(joint_name + ".rotateX", set_range_node + ".valueX")
    if jcm_axis == "YRotate":
        cmds.connectAttr(joint_name + ".rotateY", set_range_node + ".valueX")
    if jcm_axis == "ZRotate":
        cmds.connectAttr(joint_name + ".rotateZ", set_range_node + ".valueX")

    # Connect the setRange output to the blendshape weight using the target alias
    cmds.connectAttr(set_range_node + ".outValueX", blendshape_target_dest)

def create_autojcm(morph_link, blendshape_target_dest):
    # Parse dtu morphlinks data to recreate Daz Studio joint-controlled-morph behaviors
    global dtu_loader
    # Load joint limit dictionary to query later (may not be needed)
    bone_limits_dict = dtu_loader.get_bone_limits_dict()
    # Iterate through all ERC links to find joint-controlled data
    for links_dict in morph_link["Links"]:
        # print("DEBUG: link_dict=" + str(links_dict) )
        if links_dict["Bone"] != "None":
            # Retrieve Daz data and remap to Maya compatible data
            joint_name = links_dict["Bone"]
            jcm_axis = links_dict["Property"]
            jcm_link_equation = links_dict["Type"]
            jcm_scalar = links_dict["Scalar"]
            jcm_addend = links_dict["Addend"]
            blendshape_min = morph_link["Minimum"]
            blendshape_max = morph_link["Maximum"]
            joint_min = None
            joint_max = None
            if joint_name in bone_limits_dict:
                limit_data = bone_limits_dict[joint_name]
                axis_index = -1
                if jcm_axis == "XRotate":
                    axis_index = 0
                elif jcm_axis == "YRotate":
                    axis_index = 1
                elif jcm_axis == "ZRotate":
                    axis_index = 2
                if axis_index != -1:
                    axis_index += 1
                    if jcm_link_equation == 6:
                        jcm_keyed_curve_type = links_dict["Key Type"]
                        curve_points = links_dict["Keys"]
                        first_point = curve_points[next(iter(curve_points))]
                        joint_min = first_point["Rotate"]
                        blendshape_min = first_point["Value"]
                        last_point = curve_points[list(curve_points.keys())[-1]]
                        joint_max = last_point["Rotate"]
                        blendshape_max = last_point["Value"]
                    elif jcm_link_equation == 0:
                        joint_min = (blendshape_min - jcm_addend)/jcm_scalar
                        joint_max = (blendshape_max - jcm_addend)/jcm_scalar
                    else:
                        print("ERROR: unhandled jcm_link_equation=" + str(jcm_link_equation) )
                        joint_min = limit_data[axis_index*2]
                        joint_max = limit_data[axis_index*2 + 1]
                    if joint_min is not None and joint_min > joint_max:
                        temp = joint_max
                        joint_max = joint_min
                        joint_min = temp
                        temp = blendshape_max
                        blendshape_max = blendshape_min
                        blendshape_min = temp
            # # morph_link info
            # print("DEBUG: link[Label]=" + str(morph_link["Label"]) )
            # print("DEBUG: link[Maximum]=" + str(morph_link["Maximum"]) )
            # print("DEBUG: link[Minimum]=" + str(morph_link["Minimum"]) )
            # # bone_link info
            # print("DEBUG: link[Links][Bone]=" + str(links_dict["Bone"]) )
            # print("DEBUG: link[Links][Property]=" + str(links_dict["Property"]) )
            # print("DEBUG: link[Links][Type]=" + str(links_dict["Type"]) )
            # print("DEBUG: link[Links][Scalar]=" + str(links_dict["Scalar"]) )
            # print("DEBUG: link[Links][Addend]=" + str(links_dict["Addend"]) )
            # print("DEBUG: joint_min=" + str(joint_min) )
            # print("DEBUG: joint_max=" + str(joint_max) )
            # print("DEBUG: blendshape_min=" + str(blendshape_min) )
            # print("DEBUG: blendshape_max=" + str(blendshape_max) )

            # Create an auto-JCM node using setRange node and the data converted from the ERC link
            if joint_min is not None:
                create_autojcm_node(joint_name, blendshape_target_dest, jcm_axis, joint_min, joint_max, blendshape_min, blendshape_max)
                return True

    return False

def create_morphs_node(morph_links):
    """
    Create a node for adding controls to blendshapes.
    """
    morph_node = cmds.createNode("transform", n="Morphs")
    cmds.select(morph_node)

    for link in morph_links:
        morph_label = morph_links[link]["Label"]
        morph_label_ns = morph_label.replace(" ", "")
        morph_min = morph_links[link]["Minimum"]
        morph_max = morph_links[link]["Maximum"]
        cmds.addAttr(longName=morph_label_ns, niceName=morph_label, min=morph_min, max=morph_max)
        cmds.setAttr(morph_node + "." + morph_label_ns, e=True, k=True)

    blendshapes = cmds.ls(type="blendShape")
    for blendshape in blendshapes:
        blend_targets = cmds.listAttr(blendshape + ".w", m=True)
        for blend_target in blend_targets:
            link = clean_name(blend_target)
            if link not in morph_links.keys(): continue
            morph_label_ns = morph_links[link]["Label"].replace(" ", "")
            source = morph_node + "." + morph_label_ns
            dest = blendshape + "." + blend_target

            if (create_autojcm(morph_links[link], dest)):
                continue

            try:
                cmds.connectAttr(source, dest)
            except:
                pass


def create_custom_template(morph_links):
    """
    Create custom template to be used for morphList node
    """
    template_text = "<?xml version='1.0' encoding='UTF-8'?>\n"
    template_text += "<templates>\n"

    template_text += "<template name='AEtransform'>\n"
    for link in morph_links:
        morph_label = morph_links[link]["Label"]
        morph_label_ns = morph_label.replace(" ", "")
        template_text += "<attribute name='" + morph_label_ns + "' type='maya.double'>\n"
        template_text += "<label>" + morph_label + "</label>\n"
        template_text += "</attribute>\n"
    template_text += "</template>\n"

    template_text += "<view name='Morphs' template='AEtransform'>\n"
    for link in morph_links:
        groups = morph_links[link]["Path"].split('/')
        groups = list(filter(None, groups))
        for group in groups:
            group = group.replace(" ", "")
            #template_text += "<group name='" + group + "'>\n"
        morph_label = morph_links[link]["Label"]
        morph_label_ns = morph_label.replace(" ", "")
        template_text += "<property name='" + morph_label_ns + "'/>\n"
        for group in groups:
            template_text += "" #"</group>\n"
    template_text += "</view>\n"

    template_text += "</templates>\n"

    template_path = Definitions.DAZTOMAYA_MODULE_DIR + "\scripts\\AETemplates\AEtransform.MorphsTemplate.xml"
    template_file = open(template_path, "w")
    template_file.write(template_text)
    template_file.close()

    #cmds.refreshEditorTemplates()
    mel.eval("refreshCustomTemplate")


def clean_morphs():
    """
    Clean blend shape name from unenecessary parts
    """
    blendshapes = cmds.ls(type="blendShape")
    for blendShape in blendshapes:
        blend_target_list = cmds.listAttr(blendShape + '.w', m=True)

        for blend_target in blend_target_list:
            bs_fixed = blend_target.replace("head__eCTRL", "")
            if (bs_fixed.find("__") > 1):
                bs_split = bs_fixed.split("__")
                bs_fixed = bs_fixed.replace(bs_split[0]+"__", "")
            bs_fixed = bs_fixed.replace("headInner__", "")
            bs_fixed = bs_fixed.replace("head_eCTRL", "")
            bs_fixed = bs_fixed.replace("head__", "")
            bs_fixed = bs_fixed.replace("head_", "")
            bs_fixed = bs_fixed.replace("PHM", "")
            bs_fixed = bs_fixed.replace("CTRL", "")
            bs_fixed = bs_fixed.replace("QT1", "")
            bs_fixed = bs_fixed.replace("Shape", "")

            oldMorph = blendShape + "." + blend_target
            try:
                # Rename Morphs (Blendshapes)
                cmds.aliasAttr(bs_fixed, oldMorph)
            except:
                pass
