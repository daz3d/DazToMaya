import os
import sys

import maya.cmds as cmds
import maya.api.OpenMaya as om2

import Definitions
import DtuLoader

python_version = sys.version_info[0]
if python_version > 3:
    import importlib
    importlib.reload(Definitions)
    importlib.reload(DtuLoader)
else:
    reload(Definitions)
    reload(DtuLoader)


def fix_morphs():
    """
    Add centralized morph controls using exported Dtu data and clean blendshapes
    """
    morph_links = load_morph_links()
    create_morphs_node(morph_links)
    create_custom_template(morph_links)
    clean_morphs()


def load_morph_links():
    """
    Load morph links from Dtu file
    """
    dtu_path = os.path.abspath(Definitions.EXPORT_DIR + "\FIG\FIG0")
    dtu_loader = DtuLoader.DtuLoader(dtu_path)
    morph_links = dtu_loader.get_morph_links_dict()
    return morph_links


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
    for link in morph_links:
        controlled_meshes = morph_links[link]["Controlled Meshes"]
        morph_label_ns = morph_links[link]["Label"].replace(" ", "")
        for blendshape in blendshapes:
            blend_targets = cmds.listAttr(blendshape + ".w", m=True)
            for blend_target in blend_targets:
                if morph_label_ns not in blend_target: continue
                source = morph_node + "." + morph_label_ns
                dest = blendshape + "." + blend_target
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

    template_path = os.path.abspath("..\scripts\\AETemplates\AEtransform.MorphsTemplate.xml")
    template_file = open(template_path, "w")
    template_file.write(template_text)
    template_file.close()

    cmds.refreshEditorTemplates()


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
