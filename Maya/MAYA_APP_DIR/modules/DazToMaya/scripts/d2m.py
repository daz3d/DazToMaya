import sys
import os
import math
import traceback
import webbrowser

import maya.mel as mel
import maya.cmds as cmds
import pymel.core as pm
import xml.etree.cElementTree as ET

from xml.etree import ElementTree
from pymel import versions
from shutil import copyfile

# no delete morph, editer for user...

d2mLogo = os.path.expanduser("../icons/d2m_logo.png")
imgIcon = os.path.expanduser("../icons/iconhelp.png")
txtConf = os.path.expanduser("./d2m.cfg")

pc = 1
if os.path.exists(d2mLogo) == False:
    d2mLogo = "/users/Shared/Autodesk/maya/plug-ins/DazToMaya_Files/d2m_logo.png"
    if os.path.exists(d2mLogo) == True:
        pc = 0

if pc == 0:
    txtConf = "/users/Shared/Autodesk/maya/plug-ins/DazToMaya_Files/d2m.cfg"
    imgIcon = "/users/Shared/Autodesk/maya/plug-ins/DazToMaya_Files/iconhelp.png"


if os.path.exists(txtConf) == False:
    configAskToSave(1)

with open(txtConf, 'r') as output:
    cfgSettings = output.read()

scaleMenuValue = "Automatic"

mayaversion = str(versions.current())

replaceShaders = True
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


# -------------------------------------------------------------------
# Converting... Please Wait Dialog------------------------------------------------
try:
    waitWindowName = "DazToMayaPleaseWait11"
except:
    pass


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# Converting... Please Wait Dialog------------------------------------------------
try:
    waitWindowName2 = "DazToMayaPleaseWait22"
except:
    pass


# DETECT FIGURE------------------------
i = 0
objs = mel.eval('ls')
o = ""

# checkIfModified()

for o in objs:
    if cmds.objectType(o) == "locator":
        if o.find("Character1_Reference") == 0:
            print "Found"

    if o.find("Genesis2Female") == 0:
        figure = "Genesis2MaleFBXASC046Shape"

    if o.find("Genesis2Female") == 0:
        figure = "Genesis2FemaleFBXASC046Shape"
    i = i + 1


mel.eval('select -cl')


if not cmds.pluginInfo('mtoa', query=True, loaded=True):
    try:
        cmds.loadPlugin('mtoa')
    except:
        pass

checkSave = 0

# Main Dialog--------------------------------------------------------
# -------------------------------------------------------------------
windowName = "DazToMayaMain12225"
try:
    cmds.deleteUI(windowName)
except:
    pass

windowDazMain = cmds.window(windowName, toolbox=True, maximizeButton=False,
                            minimizeButton=True, sizeable=False, title="DazToMaya v1.7", widthHeight=(343, 452))
cmds.columnLayout("columnName01", adjustableColumn=True)
cmds.image(image=d2mLogo, width=343)
#cmds.separator( height=10, style='none' )
#cmds.separator( height=2, style='in' )
#cmds.separator( height=5, style='none' )

cmds.separator(height=3, style='none')
cmds.rowColumnLayout(numberOfColumns=4, columnWidth=[
                     (1, 85), (2, 55), (3, 65)], columnSpacing=[(1, 1), (2, 0)])
cmds.text(label='  Import from: ', align='left')
cmds.radioCollection()
rButton0 = cmds.radioButton(
    "radioImpAuto", label='Temp', select=True, align='left')
rButton1 = cmds.radioButton("radioImpManual", label='Manual', align='center')

cmds.optionMenu("scaleMenu", w=130, label="  Scale:")
cmds.menuItem(label="Automatic")
cmds.menuItem(label="x10 (biger)")
cmds.menuItem(label="x1 (default)")
cmds.menuItem(label="x0.1 (small)")
cmds.menuItem(label="x0.01 (smaller)")

cmds.setParent('..')
cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[
                     (1, 130), (2, 230)], columnSpacing=[(1, 10)])


cmds.setParent('..')
cmds.button(label='Auto-Import', width=343, height=50,
            c=lambda *args: autoImportDaz())
cmds.separator(height=20, style='in')
cmds.text(label='  If importing from Temp folder, save to another location (!)', align='center')
cmds.separator(height=8, style='none')
cmds.button(label='Save Scene with Textures...', width=343,
            height=45, c=lambda *args: btnSaveWithText())

cmds.separator(height=5, style='none')
cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 10)])
cmds.separator(height=5, style='none')

# if "askToSaveSceneWithTextures=1" in cfgSettings:
#	cmds.checkBox( label="Show me a reminder after importing from Temp folder.", changeCommand=lambda *args: configAskToSave() ,value=1 )
# if "askToSaveSceneWithTextures=0" in cfgSettings:
#	cmds.checkBox( label="Show me a reminder after importing from Temp folder.", changeCommand=lambda *args: configAskToSave() ,value=0 )

if "askToSaveSceneWithTextures=0" in cfgSettings:
    checkSave = cmds.checkBox(label="Show me a reminder after importing from Temp folder.",
                              changeCommand=lambda *args: tempFun(), value=0)
else:
    checkSave = cmds.checkBox(label="Show me a reminder after importing from Temp folder.",
                              changeCommand=lambda *args: tempFun(), value=1)

cmds.setParent('..')

cmds.separator(height=15, style='in')
cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[
                     (1, 225), (2, 8), (3, 95)], columnSpacing=[(1, 6), (2, 0)])
cmds.button(label='Convert Materials', width=43,
            height=25, c=lambda *args: btnConvert())
cmds.separator(height=8, style='none')
cmds.optionMenu("matConvertMenu", w=50, label="")
cmds.menuItem(label="Arnold")
cmds.menuItem(label="Vray")

cmds.setParent('..')
cmds.separator(height=20, style='in')
cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[
                     (1, 130), (2, 230)], columnSpacing=[(1, 10)])
cmds.setParent('..')

cmds.text(label='  Global Skin Parameters:', align='left')
cmds.separator(height=5, style='none')
cmds.floatSliderGrp('SpecWeight', label='Specular Weight', field=True,
                    precision=2, value=0, minValue=0, maxValue=1, dc=slider_drag_callback)
cmds.floatSliderGrp('SpecRough', label='Specular Roughness', field=True,
                    precision=2, value=0, minValue=0, maxValue=1, dc=slider_drag_callback)
cmds.separator(height=18, style='in')

cmds.rowColumnLayout(numberOfColumns=4, columnWidth=[
                     (1, 10), (2, 50), (3, 10), (4, 200)])
cmds.separator(height=5, style='none')
# checkMerge = cmds.checkBox( label="Merge", changeCommand=lambda *args: tempFun() ,value=1 )
checkMerge = cmds.checkBox(label="Merge", value=0, visible=0)


cmds.separator(height=5, style='none')
cmds.text(label='Copyright (c) 2020. All Rights Reserved.')

# cmds.iconTextButton(w=24,h=24,style='iconOnly', image1=imgIcon, label='Help', annotation="DazToMaya: Help and Tutorials", c=lambda *args: btnGoHelp() )

cmds.setParent('..')

#cmds.iconTextButton(width=150, style='iconAndTextHorizontal',bgc=col, image1='menuIconHelp.png', label='sphere!!' )


rb0 = cmds.radioButton(rButton0, q=True, sl=True)
rb1 = cmds.radioButton(rButton1, q=True, sl=True)


askToSaveWindowName = "AskToSaveWindow5"


codeGenerator = os.path.expanduser("~/T")
codeGenerator = codeGenerator.encode('base64', 'strict')
codeGenerator = codeGenerator[:-25]
cmds.textField("txtFieldCode", edit=True, tx=codeGenerator)


d2mstart()
# d2m58-mac


def configAskToSave(value):
    with open(txtConf, 'wt') as output:
        output.write('askToSaveSceneWithTextures=' + str(value))


def btnSaveWithText():
    try:
        cmds.deleteUI(askToSaveWindowName)
    except:
        pass
    multipleFilters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb)"
    saveFileResult = cmds.fileDialog2(
        fileFilter=multipleFilters, dialogStyle=2)

    if saveFileResult != None:
        outPath = os.path.dirname(saveFileResult[0]) + "/"

        try:
            os.makedirs(outPath + "/images")
        except:
            pass

        textureFileNodes = pm.ls(typ='file')
        for fileNode in textureFileNodes:
            print(fileNode)
            imagePath = fileNode.getAttr('fileTextureName')
            justFilename = os.path.basename(imagePath)
            outFilename = outPath + "images/" + str(justFilename)
            if imagePath != outFilename:
                from shutil import copyfile
                copyfile(imagePath, outFilename)
                fileNode.setAttr('fileTextureName',
                                 "images/" + str(justFilename))

        cmds.file(rename=saveFileResult[0])
        if ".ma" in saveFileResult[0]:
            cmds.file(save=True, type="mayaAscii")
        else:
            cmds.file(save=True, type="mayaBinary")


# ---- GROUP PROPSSSSS -----------------------------------------------------
def parentsList():
    parentsList = []
    objsAndJoints = mel.eval('ls')
    for x in objsAndJoints:
        try:
            parents = cmds.ls(x, long=True)[0].split('|')[1:-1]
            if len(parents) == 1:
                parentsList.append(parents[0])
        except:
            pass
    return parentsList


def groupStuff(parentObj):
    groupName = parentObj
    groupChilds = cmds.listRelatives(groupName, allDescendents=True)
    cmds.spaceLocator(name=groupName+"_Group", p=[0, 0, 0])
    if len(groupChilds) > 1:
        for o in groupChilds:
            try:
                cmds.parent(o, world=True)
                cmds.parent(o, groupName+"_Group")
            except:
                pass


def remoJointsIfProp(parentObj):
    cacaChilds = cmds.listRelatives(parentObj, allDescendents=True)
    if "hip" not in cacaChilds:
        for x in cacaChilds:
            #groupStuff( x )
            if cmds.objectType(x) == "joint":
                try:
                    cmds.delete(x)
                except:
                    pass
        pass


def groupProps():
    caca = parentsList()
    for x in caca:
        try:
            groupChilds = cmds.listRelatives(x, allDescendents=True)
            if "hip" not in groupChilds:
                if len(groupChilds) > 1:
                    remoJointsIfProp(x)
                    groupStuff(x)
                    try:
                        cmds.delete(x)
                    except:
                        pass
        except:
            pass
# ---- GROUP PROPSSSSS -----------------------------------------------------


# ------------ VRAY FIXES-----------------------------
def vrayEyeFix():
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


def vrayEyeLashesFix():
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


def breakTransparency():
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


def vrayFixes():
    breakTransparency()
    vrayEyeFix()
    vrayEyeLashesFix()
# --------------------------------------------------------------------------


def matRefreshFix():
    mats = mel.eval('ls -type "phong"')
    if mats != None:
        for m in mats:
            old = m
            new = mel.eval('createNode phong')
            mel.eval('replaceNode %s %s' % (old, new))
            cmds.delete(old)
            cmds.rename(new, m)


def breakConnectionFromMaterials(matAttribute):
    try:
        mats = mel.eval('ls -type "phong"')
        connections = cmds.listConnections(mats, d=0, s=1, c=1, p=1)
        for i in range(0, len(connections), 2):
            if connections[i].rsplit('.', 1)[1] == matAttribute:
                cmds.disconnectAttr(connections[i+1], connections[i])
    except:
        pass


def removeDisplacementMaps():
    mats = mel.eval('ls -type "displacementShader"')
    try:
        for m in mats:
            try:
                cmds.delete(m)
            except:
                pass
    except:
        pass


def dfGenesis3():
    mel.eval('setCharacterObject("hip","Character1",1,0)')
    mel.eval('setCharacterObject("abdomenLower","Character1",8,0)')
    mel.eval('setCharacterObject("abdomenUpper","Character1",23,0)')
    mel.eval('setCharacterObject("chestLower","Character1",24,0)')
    mel.eval('setCharacterObject("chestUpper","Character1",25,0)')
    mel.eval('setCharacterObject("lCollar","Character1",18,0)')
    mel.eval('setCharacterObject("rCollar","Character1",19,0)')
    mel.eval('setCharacterObject("neckLower","Character1",20,0)')
    mel.eval('setCharacterObject("neckUpper","Character1",15,0)')
    mel.eval('setCharacterObject("lShldrBend","Character1",9,0)')
    mel.eval('setCharacterObject("lForearmBend","Character1",10,0)')
    mel.eval('setCharacterObject("lShldrTwist","Character1",176,0)')
    mel.eval('setCharacterObject("lForearmTwist","Character1",177,0)')
    mel.eval('setCharacterObject("lHand","Character1",11,0)')
    mel.eval('setCharacterObject("rShldrBend","Character1",12,0)')
    mel.eval('setCharacterObject("rForearmBend","Character1",13,0)')
    mel.eval('setCharacterObject("rShldrTwist","Character1",178,0)')
    mel.eval('setCharacterObject("rForearmTwist","Character1",179,0)')
    mel.eval('setCharacterObject("rHand","Character1",14,0)')
    mel.eval('setCharacterObject("rThighBend","Character1",5,0)')
    mel.eval('setCharacterObject("lThighBend","Character1",2,0)')
    mel.eval('setCharacterObject("lShin","Character1",3,0)')
    mel.eval('setCharacterObject("rShin","Character1",6,0)')
    mel.eval('setCharacterObject("lFoot","Character1",4,0)')
    mel.eval('setCharacterObject("rFoot","Character1",7,0)')
    mel.eval('setCharacterObject("lThighTwist","Character1",172,0)')
    mel.eval('setCharacterObject("rThighTwist","Character1",174,0)')

    # mel.eval('setCharacterObject("Genesis3Female","Character1",0,0)')


def dfGenesis2():
    mel.eval('setCharacterObject("hip","Character1",1,0)')
    mel.eval('setCharacterObject("abdomen","Character1",8,0)')
    mel.eval('setCharacterObject("abdomen2","Character1",23,0)')
    mel.eval('setCharacterObject("chest","Character1",24,0)')
    # mel.eval('setCharacterObject("chestUpper","Character1",25,0)')
    mel.eval('setCharacterObject("lCollar","Character1",18,0)')
    mel.eval('setCharacterObject("rCollar","Character1",19,0)')
    mel.eval('setCharacterObject("neck","Character1",20,0)')
    mel.eval('setCharacterObject("head","Character1",15,0)')
    mel.eval('setCharacterObject("lShldr","Character1",9,0)')
    mel.eval('setCharacterObject("lForeArm","Character1",10,0)')
    # mel.eval('setCharacterObject("lShldrTwist","Character1",176,0)')
    # mel.eval('setCharacterObject("lForearmTwist","Character1",177,0)')
    mel.eval('setCharacterObject("lHand","Character1",11,0)')
    mel.eval('setCharacterObject("rShldr","Character1",12,0)')
    mel.eval('setCharacterObject("rForeArm","Character1",13,0)')
    # mel.eval('setCharacterObject("rShldrTwist","Character1",178,0)')
    # mel.eval('setCharacterObject("rForearmTwist","Character1",179,0)')
    mel.eval('setCharacterObject("rHand","Character1",14,0)')
    mel.eval('setCharacterObject("rThigh","Character1",5,0)')
    mel.eval('setCharacterObject("lThigh","Character1",2,0)')
    mel.eval('setCharacterObject("lShin","Character1",3,0)')
    mel.eval('setCharacterObject("rShin","Character1",6,0)')
    mel.eval('setCharacterObject("lFoot","Character1",4,0)')
    mel.eval('setCharacterObject("rFoot","Character1",7,0)')
    # mel.eval('setCharacterObject("lThighTwist","Character1",172,0)')
    # mel.eval('setCharacterObject("rThighTwist","Character1",174,0)')

    # mel.eval('setCharacterObject("Genesis3Female","Character1",0,0)')


def dfFingers():
    try:
        mel.eval('setCharacterObject("lThumb1","Character1",50,0)')
        mel.eval('setCharacterObject("lThumb2","Character1",51,0)')
        mel.eval('setCharacterObject("lThumb3","Character1",52,0)')

        mel.eval('setCharacterObject("lThumb4","Character1",53,0)')

        mel.eval('setCharacterObject("lIndex1","Character1",54,0)')
        mel.eval('setCharacterObject("lIndex2","Character1",55,0)')
        mel.eval('setCharacterObject("lIndex3","Character1",56,0)')

        mel.eval('setCharacterObject("lIndex4","Character1",57,0)')

        mel.eval('setCharacterObject("lMid1","Character1",58,0)')
        mel.eval('setCharacterObject("lMid2","Character1",59,0)')
        mel.eval('setCharacterObject("lMid3","Character1",60,0)')

        mel.eval('setCharacterObject("lMid4","Character1",61,0)')

        mel.eval('setCharacterObject("lRing1","Character1",62,0)')
        mel.eval('setCharacterObject("lRing2","Character1",63,0)')
        mel.eval('setCharacterObject("lRing3","Character1",64,0)')

        mel.eval('setCharacterObject("lRing4","Character1",65,0)')

        mel.eval('setCharacterObject("lPinky1","Character1",66,0)')
        mel.eval('setCharacterObject("lPinky2","Character1",67,0)')
        mel.eval('setCharacterObject("lPinky3","Character1",68,0)')

        mel.eval('setCharacterObject("lPinky4","Character1",69,0)')

        mel.eval('setCharacterObject("rThumb1","Character1",74,0)')
        mel.eval('setCharacterObject("rThumb2","Character1",75,0)')
        mel.eval('setCharacterObject("rThumb3","Character1",76,0)')

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
    except:
        print('skip fingers')


def importFbx():
    #strDir = "C:/TEMP3D/DazToMaya.fbx"

    #Mm.eval('string $strDir = `python "strDir"`;')

    mel.eval('FBXImportMode -v Add')
    mel.eval('FBXImportMergeAnimationLayers -v false')
    mel.eval('FBXImportProtectDrivenKeys -v true')
    mel.eval('FBXImportConvertDeformingNullsToJoint -v true')
    mel.eval('FBXImportMergeBackNullPivots -v false')
    mel.eval('FBXImportSetLockedAttribute -v true')
    mel.eval('FBXImportConstraints -v false')
    # mel.eval('FBXImportConvertUnitString dm') --SCALE FIX?....... CHELO

    if scaleMenuValue == "Automatic":
        # FORCE cm Correct Unit....... CHELO
        mel.eval('FBXImportConvertUnitString cm')
    if scaleMenuValue == "x1 (default)":
        # FORCE cm Correct Unit....... CHELO
        mel.eval('FBXImportConvertUnitString cm')
    if scaleMenuValue == "x10 (biger)":
        # FORCE cm Correct Unit....... CHELO
        mel.eval('FBXImportConvertUnitString mm')
    if scaleMenuValue == "x0.1 (small)":
        # FORCE cm Correct Unit....... CHELO
        mel.eval('FBXImportConvertUnitString dm')
    if scaleMenuValue == "x0.01 (smaller)":
        # FORCE cm Correct Unit....... CHELO
        mel.eval('FBXImportConvertUnitString m')

    dazFilePath = "C:\TEMP3D\DazToMaya.fbx"
    if os.path.exists(dazFilePath) == False:
        mel.eval('FBXImport -f "/users/Shared/temp3d/DazToMaya.fbx"')
    else:
        mel.eval('FBXImport -f "C:/TEMP3D/DazToMaya.fbx"')


def checkIfModified():
    objs = mel.eval('ls')
    for o in objs:
        if cmds.objectType(o) == "locator":
            if o.find("Character1_Reference") == 0:
                print "\n"*10
                print "Scene already modified"
                sys.exit()  # ABOUR SCRIPT IF SCENE NOT READY!!


def clampTextures():
    try:
        mel.eval('setAttr "hardwareRenderingGlobals.enableTextureMaxRes" 1')
        mel.eval('setAttr "hardwareRenderingGlobals.textureMaxResolution" 512')
    except:
        print "No Text Clamp"


def sentinelExtraFinger():
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


def sentinelRemoveFinger():
    try:
        mel.eval('select -r -sym lThumb4')
        mel.eval('doDelete')
        mel.eval('select -r -sym rThumb4')
        mel.eval('doDelete')
    except:
        print "Sentinel Finger Fix"


def cleanMorphs(figureWithMorphs):
    blendShapesList = mel.eval('aliasAttr -q %s' % figureWithMorphs)
    i = 0
    for b in blendShapesList:
        bFixed = b
        bFixed = bFixed.replace("head__eCTRL", "")
        if (bFixed.find("__") > 1):
            caca = bFixed.split("__")
            # remove weird stuff from BlendShape Name
            bFixed = bFixed.replace(caca[0]+"__", "")
        bFixed = bFixed.replace("headInner__", "")
        bFixed = bFixed.replace("head_eCTRL", "")
        # remove weird stuff from BlendShape Name
        bFixed = bFixed.replace("head__", "")
        # remove weird stuff from BlendShape Name
        bFixed = bFixed.replace("head_", "")
        # remove weird stuff from BlendShape Name
        bFixed = bFixed.replace("PHM", "")
        # remove weird stuff from BlendShape Name
        bFixed = bFixed.replace("CTRL", "")
        # remove weird stuff from BlendShape Name
        bFixed = bFixed.replace("QT1", "")
        # remove weird stuff from BlendShape Name
        bFixed = bFixed.replace("Shape", "")
        oldMorph = figureWithMorphs + "." + b
        try:
            # Rename Morphs (Blendshapes)
            mel.eval('aliasAttr %s %s' % (bFixed, oldMorph))
        except:
            pass
        i += 1


def FixMorphs():
    meshList = mel.eval('ls')
    for m in meshList:
        if "BlendShape" in m:
            cleanMorphs(m)


def hideRootBone():
    # check if no parent, etc
    #parentsList = cmds.listRelatives("lShin", allParents=True, noIntermediate=True, fullPath=True)
    listAllJoints = mel.eval('ls -type joint')
    hideJoint = listAllJoints[0] + ".drawStyle"
    mel.eval('setAttr %s 2' % hideJoint)


def cleanMatNames():
    try:
        mats = mel.eval('ls -type "phong"')
        for m in mats:
            try:
                mClean = m.split("_")
                mel.eval('rename %s %s' % (m, mClean[1]))
            except:
                pass
    except:
        print "no std mats"


def loadSkeleton():
    pass


def slider_drag_callback(*args):
    valorSpecWeight = cmds.floatSliderGrp('SpecWeight', query=True, value=True)
    valorSpecRough = cmds.floatSliderGrp('SpecRough', query=True, value=True)

    humanMats = ("Skin", "SkinFace", "Face", "Nipple", "Head", "Neck", "Ears", "Torso",
                 "Hips", "Shoulders", "Arms", "Forearms", "Nipples", "Hands", "Legs", "Feet")
    scenemats = mel.eval('ls -mat')
    skinMats = []
    for m in scenemats:
        for h in humanMats:
            if h in m:
                if m not in skinMats:
                    skinMats.append(m)
    i = 0
    for o in skinMats:
        # STANDARD--------------------------------------------------------------------------------
        try:
            # Arnold - Specular Weight
            objAttrSpecWeight = skinMats[i] + ".specularColor"
            cmds.setAttr(objAttrSpecWeight, valorSpecWeight*2,
                         valorSpecWeight*2, valorSpecWeight*2)
        except:
            pass
        try:
            # Arnold - Specular Roughness
            objAttrSpecRough = skinMats[i] + ".cosinePower"
            cmds.setAttr(objAttrSpecRough, 100 - (valorSpecRough * 100))
        except:
            pass
        # ----------------------------------------------------------------------------------------
        # ARNOLD--------------------------------------------------------------------------------
        try:
            objAttrSpecWeight = skinMats[i] + ".Ks"  # Arnold - Specular Weight
            cmds.setAttr(objAttrSpecWeight, valorSpecWeight)
        except:
            pass
        try:
            # Arnold - Specular Roughness
            objAttrSpecRough = skinMats[i] + ".specularRoughness"
            cmds.setAttr(objAttrSpecRough, valorSpecRough)
        except:
            pass
        # ----------------------------------------------------------------------------------------
        # VRAY--------------------------------------------------------------------------------
        try:
            # Arnold - Specular Weight
            objAttrSpecWeight = skinMats[i] + ".reflectionColorAmount"
            cmds.setAttr(objAttrSpecWeight, valorSpecWeight)
        except:
            pass
        try:
            # Arnold - Specular Roughness
            objAttrSpecRough = skinMats[i] + ".reflectionGlossiness"
            cmds.setAttr(objAttrSpecRough, valorSpecRough)
        except:
            pass
        # ----------------------------------------------------------------------------------------
        i = i + 1


def value_change_callback(*args):
    print 'Value Changed'


def removeLimits():
    meshList = mel.eval('ls -type joint')
    for m in meshList:
        mel.eval('transformLimits -rx -20 20 -erx 0 0 %s' % m)
        mel.eval('transformLimits -ry -20 20 -ery 0 0 %s' % m)
        mel.eval('transformLimits -rz -25 25 -erz 0 0 %s' % m)


def extendFinger(baseScaleBone, endBone, newBone, scalevalue=2, rotvalue=0):
    mel.eval('select -r %s' % baseScaleBone)

    mel.eval('rotate -r -os -fo 0 0 %s' % rotvalue)  # NEW LINEEE
    mel.eval('scale -a %s %s %s' % (scalevalue, scalevalue, scalevalue))
    mel.eval('select -r %s' % endBone)
    caca = mel.eval('xform -q -t -ws')
    mel.eval('select -r %s' % baseScaleBone)
    mel.eval('scale -a 1 1 1')
    rotvalue = rotvalue * -1  # NEW LINEEE
    mel.eval('rotate -r -os -fo 0 0 %s' % rotvalue)
    mel.eval('select -r %s' % endBone)
    cmds.joint(name=newBone, p=(caca))


def extendHandFingers():
    jointsList = mel.eval('ls -type joint')
    done = 0
    if "lIndex3" in jointsList:
        extendFinger("lIndex2", "lIndex3", "lIndex4", 2, 0)
        extendFinger("lMid2", "lMid3", "lMid4", 2, 0)
        extendFinger("lRing2", "lRing3", "lRing4", 2, 0)
        extendFinger("lPinky2", "lPinky3", "lPinky4", 2, 0)
        extendFinger("lThumb2", "lThumb3", "lThumb4", 2, 0)

        extendFinger("rIndex2", "rIndex3", "rIndex4", 2, 0)
        extendFinger("rMid2", "rMid3", "rMid4", 2, 0)
        extendFinger("rRing2", "rRing3", "rRing4", 2, 0)
        extendFinger("rPinky2", "rPinky3", "rPinky4", 2, 0)
        extendFinger("rThumb2", "rThumb3", "rThumb4", 2, 0)
        done = 1
    if "lIndex2" in jointsList:
        if "lIndex3" not in jointsList:
            extendFinger("lIndex2", "lIndex2", "lIndex3")
            extendFinger("lMid2", "lMid2", "lMid3")
            extendFinger("lRing2", "lRing2", "lRing3")
            extendFinger("lPinky2", "lPinky2", "lPinky3")
            extendFinger("lThumb2", "lThumb2", "lThumb3", 2)

            extendFinger("rIndex2", "rIndex2", "rIndex3")
            extendFinger("rMid2", "rMid2", "rMid3")
            extendFinger("rRing2", "rRing2", "rRing3")
            extendFinger("rPinky2", "rPinky2", "rPinky3")
            extendFinger("rThumb2", "rThumb2", "rThumb3", 2)


def removeHidden():
    cameraList = cmds.ls(cameras=1)
    objList = cmds.ls()
    i = 0
    for o in objList:
        try:
            visi = cmds.getAttr(objList[i] + ".visibility")
            if visi == False:
                if o not in cameraList:
                    mel.eval('delete %s' % objList[i])
        except:
            None
        i = i + 1


def connectTex(image, material, input):
    # if a file texture is already connected to this input, update it
    # otherwise, delete it
    try:
        conn = cmds.listConnections(material+'.'+input, type='file')
        if conn:
            # there is a file texture connected. replace it
            cmds.setAttr(conn[0]+'.fileTextureName', image, type='string')
        else:
            # no connected file texture, so make a new one
            newFile = cmds.shadingNode('file', asTexture=1)
            newPlacer = cmds.shadingNode('place2dTexture', asUtility=1)
            # make common connections between place2dTexture and file texture
            connections = ['rotateUV', 'offset', 'noiseUV', 'vertexCameraOne', 'vertexUvThree', 'vertexUvTwo', 'vertexUvOne',
                           'repeatUV', 'wrapV', 'wrapU', 'stagger', 'mirrorU', 'mirrorV', 'rotateFrame', 'translateFrame', 'coverage']
            cmds.connectAttr(newPlacer+'.outUV', newFile +
                             '.uvCoord', force=True)
            cmds.connectAttr(newPlacer+'.outUvFilterSize',
                             newFile+'.uvFilterSize', force=True)
            for i in connections:
                cmds.connectAttr(newPlacer+'.'+i, newFile+'.'+i, force=True)
            # now connect the file texture output to the material input
            cmds.connectAttr(newFile+'.outColor', material +
                             '.'+input, f=1, force=True)
            # now set attributes on the file node.
            cmds.setAttr(newFile+'.fileTextureName', image, type='string')
            cmds.setAttr(newFile+'.filterType', 0)
    except:
        print "Texture Nc."


def getTransparencyFile(matname):
    #matname = "Strands"
    fileList = cmds.ls(type='file')
    for f in fileList:
        caca = mel.eval('listConnections -plugs true %s' % f)
        try:
            for c in caca:
                if (matname + ".transparency" in c):
                    textureFile = cmds.getAttr(f + '.fileTextureName')
        except:
            pass


def parentar(source, target):
    # Parentar------------------------------------------
    mel.eval('select -r %s' % target)
    mel.eval('select -tgl %s' % source)
    mel.eval(
        'doCreateParentConstraintArgList 1 { "1","0","0","0","0","0","0","0","1","","1" }')
    mel.eval('parentConstraint -mo -weight 1')
    mel.eval('select -cl')
    # --------------------------------------------------


def unirBones(source, target):
    jointsList = mel.eval('ls -type joint')
    if source in jointsList:
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
        parentar(source, target)
        # --------------------------------------------------


def eyeLashFixGen3():
    try:
        mel.eval('disconnectAttr m5philliplashes.outColor Eyelashes.color')
        mel.eval('setAttr "Eyelashes.color" -type double3 0 0 0')
    except:
        pass


def eyeLashFix():
    listAll = mel.eval('ls')
    for l in listAll:
        try:
            if "Lashes" in l:
                print "Texture: " + l
            if "lash" in l:
                lashMaterial = l
                conn = cmds.listConnections(
                    lashMaterial+'.'+"color", type='file')
        except:
            pass

    # disconnectAttr M5PhillipLashes.outColor FBXASC054_Eyelash.color;
    try:
        mel.eval('disconnectAttr %s.outColor %s.color' %
                 (conn[0], lashMaterial))
        mel.eval('setAttr "%s.color" -type double3 0.051 0.051 0.051' %
                 lashMaterial)
    except:
        pass


def fixRotation(bone, x, y, z):
    mel.eval('select -cl')
    mel.eval('select -r %s' % bone)
    mel.eval('rotate -r -os -fo %d %d %d' % (x, y, z))
    mel.eval('select -cl')


def hideBone(target):
    target = target + ".drawStyle"
    cmds.setAttr('%s' % target, 2)


def dazToIk():
    # Load Skeleton
    try:
        hideBone("Genesis2Female")
    except:
        None
    try:
        hideBone("Genesis2Male")
    except:
        None

    # unirBones(DazBone,HumanIkBone) -------------------------------------
    jointsList = mel.eval('ls -type joint')

    if "hip" in jointsList:
        mel.eval('setCharacterObject("hip","Character1",1,0)')
    # if "pelvis" in jointsList:
        # unirBones("pelvis","Character1_Hips")

    # if "spine" in jointsList:
    #	unirBones("spine","Character1_Spine")

    if "abdomen" in jointsList:
        mel.eval('setCharacterObject("abdomen","Character1",8,0)')

    if "abdomenLower" in jointsList:
        mel.eval('setCharacterObject("abdomenLower","Character1",8,0)')

    if "abdomenUpper" in jointsList:
        mel.eval('setCharacterObject("abdomenUpper","Character1",23,0)')

    if "abdomen2" in jointsList:
        mel.eval('setCharacterObject("abdomen2","Character1",23,0)')
    if "chestLower" in jointsList:
        mel.eval('setCharacterObject("chestLower","Character1",24,0)')

    if "chestUpper" in jointsList:
        mel.eval('setCharacterObject("chestUpper","Character1",25,0)')
    if "chest" in jointsList:
        # mel.eval('setCharacterObject("chest","Character1",24,0)')
        mel.eval('setCharacterObject("chest","Character1",23,0)')

    if "neckLower" in jointsList:
        mel.eval('setCharacterObject("neckLower","Character1",20,0)')
    if "neck" in jointsList:
        mel.eval('setCharacterObject("neck","Character1",20,0)')

    mel.eval('setCharacterObject("head","Character1",15,0)')

    if "abdomen" in jointsList and "chest" in jointsList:  # Sentinel, etc fix
        if "abdomenLower" not in jointsList:
            if "abdomenUpper" not in jointsList:
                if "abdomen2" not in jointsList:
                    if "chestLower" not in jointsList:
                        mel.eval(
                            'setCharacterObject("abdomen","Character1",8,0)')
                        mel.eval(
                            'setCharacterObject("chest","Character1",23,0)')

    # Left
    if "lThighBend" in jointsList:
        mel.eval('setCharacterObject("lThighBend","Character1",2,0)')
    if "lThigh" in jointsList:
        mel.eval('setCharacterObject("lThigh","Character1",2,0)')

    mel.eval('setCharacterObject("lShin","Character1",3,0)')
    mel.eval('setCharacterObject("lFoot","Character1",4,0)')

    if cmds.objExists('lToe'):
        mel.eval('setCharacterObject("lToe","Character1",16,0)')

    if "lCollar" in jointsList:
        mel.eval('setCharacterObject("lCollar","Character1",18,0)')
    # if "lShldr" in jointsList:
        # unirBones("lShldr","Character1_LeftShoulder")

    if "lShldrBend" in jointsList:
        mel.eval('setCharacterObject("lShldrBend","Character1",9,0)')
    if "lShldr" in jointsList:
        mel.eval('setCharacterObject("lShldr","Character1",9,0)')

    if "lForearmBend" in jointsList:
        mel.eval('setCharacterObject("lForearmBend","Character1",10,0)')
    if "lForeArm" in jointsList:
        mel.eval('setCharacterObject("lForeArm","Character1",10,0)')

    mel.eval('setCharacterObject("lHand","Character1",11,0)')
    if cmds.objExists('lThumb1'):
        mel.eval('setCharacterObject("lThumb1","Character1",50,0)')
        mel.eval('setCharacterObject("lThumb2","Character1",51,0)')
        mel.eval('setCharacterObject("lThumb3","Character1",52,0)')
    sentinel = 0
    for j in jointsList:
        if "SENTINEL" in j:
            sentinel = sentinel + 1
    if sentinel >= 1:
        print "Sentinel Detected"
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
    if "rThighBend" in jointsList:
        mel.eval('setCharacterObject("rThighBend","Character1",5,0)')
    if "rThigh" in jointsList:
        mel.eval('setCharacterObject("rThigh","Character1",5,0)')

    mel.eval('setCharacterObject("rShin","Character1",6,0)')
    mel.eval('setCharacterObject("rFoot","Character1",7,0)')

    if cmds.objExists('rToe'):
        mel.eval('setCharacterObject("rToe","Character1",17,0)')

    if "rCollar" in jointsList:
        mel.eval('setCharacterObject("rCollar","Character1",19,0)')
    # if "rShldr" in jointsList:
        # unirBones("rShldr","Character1_RightShoulder")

    if "rShldrBend" in jointsList:
        mel.eval('setCharacterObject("rShldrBend","Character1",12,0)')
    if "rShldr" in jointsList:
        mel.eval('setCharacterObject("rShldr","Character1",12,0)')

    if "rForearmBend" in jointsList:
        mel.eval('setCharacterObject("rForearmBend","Character1",13,0)')
    if "rForeArm" in jointsList:
        mel.eval('setCharacterObject("rForeArm","Character1",13,0)')

    mel.eval('setCharacterObject("rHand","Character1",14,0)')
    if cmds.objExists('rThumb1'):
        mel.eval('setCharacterObject("rThumb1","Character1",74,0)')
        mel.eval('setCharacterObject("rThumb2","Character1",75,0)')
        mel.eval('setCharacterObject("rThumb3","Character1",76,0)')
    sentinel = 0
    for j in jointsList:
        if "SENTINEL" in j:
            sentinel = sentinel + 1
    if sentinel >= 1:
        print "Sentinel Detected"
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
    if "lForearmTwist" in jointsList:
        mel.eval('setCharacterObject("lForearmTwist","Character1",177,0)')
        mel.eval('setCharacterObject("lShldrTwist","Character1",176,0)')
        mel.eval('setCharacterObject("lThighTwist","Character1",172,0)')
        # parentar("lMetatarsals","Character1_LeftFoot")
        mel.eval('setCharacterObject("rForearmTwist","Character1",179,0)')
        mel.eval('setCharacterObject("rShldrTwist","Character1",178,0)')
        mel.eval('setCharacterObject("rThighTwist","Character1",174,0)')
        # parentar("rMetatarsals","Character1_RightFoot")

    toeBonesLeft = ("lBigToe", "lSmallToe1", "lSmallToe2",
                    "lSmallToe3", "lSmallToe4")
    for f in toeBonesLeft:
        if f in jointsList:
            parentar(f, "lToe")

    toeBonesRight = ("rBigToe", "rSmallToe1", "rSmallToe2",
                     "rSmallToe3", "rSmallToe4")
    for f in toeBonesRight:
        if f in jointsList:
            parentar(f, "rToe")


def sentinelRotationsFix():
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
        print "Sentinel fix"


def genesis1rotationsFix():
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
        print "Gen1RotsFix..."


def genesis2rotationsFix():
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
        print "Gen2RotsFix..."


def genesis3rotationsFix():
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
        print "Gen3RotsFix..."


def genesis8rotationsFix():
    # ---------------------------------------------------------
    try:
        mel.eval('setAttr "lShldrBend.rotateX" 0.0')
        mel.eval('setAttr "lShldrBend.rotateY" 0.0')
        mel.eval('setAttr "lShldrBend.rotateZ" 48.24')

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
        print "Gen8RotsFix..."


def makeSkeleton():
    mel.eval('CreateLocator')
    mel.eval('rename locator1 Character1_Reference')
    mel.eval('joint -p 0 0 0 -n "Character1_Hips"')
    mel.eval('select -r Character1_Hips ')
    mel.eval('joint -p 0 0 0 -n "Character1_LeftUpLeg"')
    mel.eval('select -r Character1_Hips ')
    mel.eval('joint -p 0 0 0 -n "Character1_RightUpLeg"')
    mel.eval('select -r Character1_Hips ')
    mel.eval('joint -p 0 0 0 -n "Character1_Spine"')

    mel.eval('select -r Character1_LeftUpLeg ')
    mel.eval('joint -p 0 0 0 -n "Character1_LeftLeg"')
    mel.eval('joint -p 0 0 0 -n "Character1_LeftFoot"')
    mel.eval('joint -p 0 0 0 -n "Character1_LeftToeBase"')

    mel.eval('select -r Character1_RightUpLeg ')
    mel.eval('joint -p 0 0 0 -n "Character1_RightLeg"')
    mel.eval('joint -p 0 0 0 -n "Character1_RightFoot"')
    mel.eval('joint -p 0 0 0 -n "Character1_RightToeBase"')

    mel.eval('select -r Character1_Spine ')
    mel.eval('joint -p 0 0 0 -n "Character1_Spine1"')
    mel.eval('joint -p 0 0 0 -n "Character1_Spine2"')
    mel.eval('select -r Character1_Spine2 ')
    mel.eval('joint -p 0 0 0 -n "Character1_LeftShoulder"')
    mel.eval('select -r Character1_Spine2 ')
    mel.eval('joint -p 0 0 0 -n "Character1_RightShoulder"')
    mel.eval('select -r Character1_Spine2 ')
    mel.eval('joint -p 0 0 0 -n "Character1_Neck"')
    mel.eval('joint -p 0 0 0 -n "Character1_Head"')

    mel.eval('select -r Character1_RightShoulder ')
    mel.eval('joint -p 0 0 0 -n "Character1_RightArm"')
    mel.eval('joint -p 0 0 0 -n "Character1_RightForeArm"')
    mel.eval('joint -p 0 0 0 -n "Character1_RightHand"')

    mel.eval('select -r Character1_LeftShoulder ')
    mel.eval('joint -p 0 0 0 -n "Character1_LeftArm"')
    mel.eval('joint -p 0 0 0 -n "Character1_LeftForeArm"')
    mel.eval('joint -p 0 0 0 -n "Character1_LeftHand"')

    mel.eval('select -r Character1_RightHand ')
    mel.eval('joint -p 0 0 0 -n "Character1_RightHandThumb1"')
    mel.eval('joint -p 0 0 0 -n "Character1_RightHandThumb2"')
    mel.eval('joint -p 0 0 0 -n "Character1_RightHandThumb3"')
    mel.eval('joint -p 0 0 0 -n "Character1_RightHandThumb4"')

    mel.eval('select -r Character1_RightHand ')
    mel.eval('joint -p 0 0 0 -n "Character1_RightHandIndex1"')
    mel.eval('joint -p 0 0 0 -n "Character1_RightHandIndex2"')
    mel.eval('joint -p 0 0 0 -n "Character1_RightHandIndex3"')
    mel.eval('joint -p 0 0 0 -n "Character1_RightHandIndex4"')

    mel.eval('select -r Character1_RightHand ')
    mel.eval('joint -p 0 0 0 -n "Character1_RightHandMiddle1"')
    mel.eval('joint -p 0 0 0 -n "Character1_RightHandMiddle2"')
    mel.eval('joint -p 0 0 0 -n "Character1_RightHandMiddle3"')
    mel.eval('joint -p 0 0 0 -n "Character1_RightHandMiddle4"')

    mel.eval('select -r Character1_RightHand ')
    mel.eval('joint -p 0 0 0 -n "Character1_RightHandRing1"')
    mel.eval('joint -p 0 0 0 -n "Character1_RightHandRing2"')
    mel.eval('joint -p 0 0 0 -n "Character1_RightHandRing3"')
    mel.eval('joint -p 0 0 0 -n "Character1_RightHandRing4"')

    mel.eval('select -r Character1_RightHand ')
    mel.eval('joint -p 0 0 0 -n "Character1_RightHandPinky1"')
    mel.eval('joint -p 0 0 0 -n "Character1_RightHandPinky2"')
    mel.eval('joint -p 0 0 0 -n "Character1_RightHandPinky3"')
    mel.eval('joint -p 0 0 0 -n "Character1_RightHandPinky4"')

    mel.eval('select -r Character1_LeftHand ')
    mel.eval('joint -p 0 0 0 -n "Character1_LeftHandThumb1"')
    mel.eval('joint -p 0 0 0 -n "Character1_LeftHandThumb2"')
    mel.eval('joint -p 0 0 0 -n "Character1_LeftHandThumb3"')
    mel.eval('joint -p 0 0 0 -n "Character1_LeftHandThumb4"')

    mel.eval('select -r Character1_LeftHand ')
    mel.eval('joint -p 0 0 0 -n "Character1_LeftHandIndex1"')
    mel.eval('joint -p 0 0 0 -n "Character1_LeftHandIndex2"')
    mel.eval('joint -p 0 0 0 -n "Character1_LeftHandIndex3"')
    mel.eval('joint -p 0 0 0 -n "Character1_LeftHandIndex4"')

    mel.eval('select -r Character1_LeftHand ')
    mel.eval('joint -p 0 0 0 -n "Character1_LeftHandMiddle1"')
    mel.eval('joint -p 0 0 0 -n "Character1_LeftHandMiddle2"')
    mel.eval('joint -p 0 0 0 -n "Character1_LeftHandMiddle3"')
    mel.eval('joint -p 0 0 0 -n "Character1_LeftHandMiddle4"')

    mel.eval('select -r Character1_LeftHand ')
    mel.eval('joint -p 0 0 0 -n "Character1_LeftHandRing1"')
    mel.eval('joint -p 0 0 0 -n "Character1_LeftHandRing2"')
    mel.eval('joint -p 0 0 0 -n "Character1_LeftHandRing3"')
    mel.eval('joint -p 0 0 0 -n "Character1_LeftHandRing4"')

    mel.eval('select -r Character1_LeftHand ')
    mel.eval('joint -p 0 0 0 -n "Character1_LeftHandPinky1"')
    mel.eval('joint -p 0 0 0 -n "Character1_LeftHandPinky2"')
    mel.eval('joint -p 0 0 0 -n "Character1_LeftHandPinky3"')
    mel.eval('joint -p 0 0 0 -n "Character1_LeftHandPinky4"')


def CharacterizeSkeleton():
    mel.eval('setCharacterObject("Character1_Head","Character1",15,0)')
    mel.eval('setCharacterObject("Character1_Hips","Character1",1,0)')
    mel.eval('setCharacterObject("Character1_LeftArm","Character1",9,0)')
    mel.eval('setCharacterObject("Character1_LeftFoot","Character1",4,0)')
    mel.eval('setCharacterObject("Character1_LeftForeArm","Character1",10,0)')
    mel.eval('setCharacterObject("Character1_LeftHand","Character1",11,0)')
    mel.eval('setCharacterObject("Character1_LeftHandIndex1","Character1",54,0)')
    mel.eval('setCharacterObject("Character1_LeftHandIndex2","Character1",55,0)')
    mel.eval('setCharacterObject("Character1_LeftHandIndex3","Character1",56,0)')
    mel.eval('setCharacterObject("Character1_LeftHandIndex4","Character1",57,0)')
    mel.eval('setCharacterObject("Character1_LeftHandMiddle1","Character1",58,0)')
    mel.eval('setCharacterObject("Character1_LeftHandMiddle2","Character1",59,0)')
    mel.eval('setCharacterObject("Character1_LeftHandMiddle3","Character1",60,0)')
    mel.eval('setCharacterObject("Character1_LeftHandMiddle4","Character1",61,0)')
    mel.eval('setCharacterObject("Character1_LeftHandPinky1","Character1",66,0)')
    mel.eval('setCharacterObject("Character1_LeftHandPinky2","Character1",67,0)')
    mel.eval('setCharacterObject("Character1_LeftHandPinky3","Character1",68,0)')
    mel.eval('setCharacterObject("Character1_LeftHandPinky4","Character1",69,0)')
    mel.eval('setCharacterObject("Character1_LeftHandRing1","Character1",62,0)')
    mel.eval('setCharacterObject("Character1_LeftHandRing2","Character1",63,0)')
    mel.eval('setCharacterObject("Character1_LeftHandRing3","Character1",64,0)')
    mel.eval('setCharacterObject("Character1_LeftHandRing4","Character1",65,0)')
    mel.eval('setCharacterObject("Character1_LeftHandThumb1","Character1",50,0)')
    mel.eval('setCharacterObject("Character1_LeftHandThumb2","Character1",51,0)')
    mel.eval('setCharacterObject("Character1_LeftHandThumb3","Character1",52,0)')
    mel.eval('setCharacterObject("Character1_LeftHandThumb4","Character1",53,0)')
    mel.eval('setCharacterObject("Character1_LeftLeg","Character1",3,0)')
    mel.eval('setCharacterObject("Character1_LeftShoulder","Character1",18,0)')
    mel.eval('setCharacterObject("Character1_LeftToeBase","Character1",16,0)')
    mel.eval('setCharacterObject("Character1_LeftUpLeg","Character1",2,0)')
    mel.eval('setCharacterObject("Character1_Neck","Character1",20,0)')
    mel.eval('setCharacterObject("Character1_Reference","Character1",0,0)')
    mel.eval('setCharacterObject("Character1_RightArm","Character1",12,0)')
    mel.eval('setCharacterObject("Character1_RightFoot","Character1",7,0)')
    mel.eval('setCharacterObject("Character1_RightForeArm","Character1",13,0)')
    mel.eval('setCharacterObject("Character1_RightHand","Character1",14,0)')
    mel.eval('setCharacterObject("Character1_RightHandIndex1","Character1",78,0)')
    mel.eval('setCharacterObject("Character1_RightHandIndex2","Character1",79,0)')
    mel.eval('setCharacterObject("Character1_RightHandIndex3","Character1",80,0)')
    mel.eval('setCharacterObject("Character1_RightHandIndex4","Character1",81,0)')
    mel.eval('setCharacterObject("Character1_RightHandMiddle1","Character1",82,0)')
    mel.eval('setCharacterObject("Character1_RightHandMiddle2","Character1",83,0)')
    mel.eval('setCharacterObject("Character1_RightHandMiddle3","Character1",84,0)')
    mel.eval('setCharacterObject("Character1_RightHandMiddle4","Character1",85,0)')
    mel.eval('setCharacterObject("Character1_RightHandPinky1","Character1",90,0)')
    mel.eval('setCharacterObject("Character1_RightHandPinky2","Character1",91,0)')
    mel.eval('setCharacterObject("Character1_RightHandPinky3","Character1",92,0)')
    mel.eval('setCharacterObject("Character1_RightHandPinky4","Character1",93,0)')
    mel.eval('setCharacterObject("Character1_RightHandRing1","Character1",86,0)')
    mel.eval('setCharacterObject("Character1_RightHandRing2","Character1",87,0)')
    mel.eval('setCharacterObject("Character1_RightHandRing3","Character1",88,0)')
    mel.eval('setCharacterObject("Character1_RightHandRing4","Character1",89,0)')
    mel.eval('setCharacterObject("Character1_RightHandThumb1","Character1",74,0)')
    mel.eval('setCharacterObject("Character1_RightHandThumb2","Character1",75,0)')
    mel.eval('setCharacterObject("Character1_RightHandThumb3","Character1",76,0)')
    mel.eval('setCharacterObject("Character1_RightHandThumb4","Character1",77,0)')
    mel.eval('setCharacterObject("Character1_RightLeg","Character1",6,0)')
    mel.eval('setCharacterObject("Character1_RightShoulder","Character1",19,0)')
    mel.eval('setCharacterObject("Character1_RightToeBase","Character1",17,0)')
    mel.eval('setCharacterObject("Character1_RightUpLeg","Character1",5,0)')
    mel.eval('setCharacterObject("Character1_Spine","Character1",8,0)')
    mel.eval('setCharacterObject("Character1_Spine1","Character1",23,0)')
    mel.eval('setCharacterObject("Character1_Spine2","Character1",24,0)')


def addExtraJoint(jName, jParent, objName, vertA, vertB):
    vertexA = objName + ".vtx[" + vertA + "]"
    vertexB = objName + ".vtx[" + vertB + "]"
    vertPosA = cmds.pointPosition(vertexA)
    vertPosB = cmds.pointPosition(vertexB)
    vertPosX = (vertPosA[0] + vertPosB[0]) / 2
    vertPosY = (vertPosA[1] + vertPosB[1]) / 2
    vertPosZ = (vertPosA[2] + vertPosB[2]) / 2
    mel.eval('select -r %s' % jParent)
    cmds.joint(name=jName, p=(vertPosX, vertPosY, vertPosZ))


def addExtraJoints():
    # left
    try:
        addExtraJoint("lThumb4", "lThumb3", figure, "965", "964")
        addExtraJoint("lIndex4", "lIndex3", figure, "3380", "3452")
        addExtraJoint("lMid4", "lMid3", figure, "3600", "3528")
        addExtraJoint("lRing4", "lRing3", figure, "3676", "3748")
        addExtraJoint("lPinky4", "lPinky3", figure, "3824", "3896")
    except:
        print('skipExtraJoints')

    try:
        # right
        addExtraJoint("rThumb4", "rThumb3", figure, "11893", "11892")
        addExtraJoint("rIndex4", "rIndex3", figure, "14229", "14157")
        addExtraJoint("rMid4", "rMid3", figure, "14305", "14377")
        addExtraJoint("rRing4", "rRing3", figure, "14525", "14453")
        addExtraJoint("rPinky4", "rPinky3", figure, "14601", "14673")
    except:
        print('skipExtraJoints')


def transparencyFix():
    shdType = "phong"
    matList = cmds.ls(exactType=shdType)
    skipMats = ["Pupils", "Cornea", "Irises", "nails", "Eye"]

    for m in matList:
        for sm in skipMats:
            if sm not in m:
                try:
                    mel.eval('setAttr "%s.specularColor" -type double3 0 0 0' % m)
                    mel.eval('setAttr "%s.reflectivity" 0' % m)
                except:
                    pass


def cleanNamespace():
    jointList = mel.eval('ls -type joint')
    for j in jointList:
        if ":" in j:
            try:
                print "Namespace detected, try cleaning"
                nameToGetNameSpace = j
                nameSpace = nameToGetNameSpace.split(":")
                mel.eval(
                    'namespace -mergeNamespaceWithRoot -removeNamespace %s' % nameSpace[0])
            except:
                print "namespace msg finished"
    print "namespace fix finished"


def genesis8matfix():
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


def loadModel():
    mel.eval('file -f -options "v=0;p=17;f=0"  -ignoreVersion  -typ "mayaBinary" -o "F:/_3DTOALL/DazToMaya/Test Models/Genesis2_Clean.mb";addRecentFile("C:/__3DtoAll Backup/DazToMaya/Test Models/Genesis2_Clean.mb", "mayaBinary")')


def extraEyeFixes():
    try:
        mel.eval(
            'disconnectAttr LoganEyesRef.outTransparency EyeReflection.transparency')
        mel.eval('setAttr "EyeReflection.transparency" -type double3 1 1 1')
    except:
        pass


def eyeLashesFix1():
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
        print "Lashes fix"


def eyeLashesFix2():
    try:
        mel.eval('select -r Eyelash_vr')
        mel.eval('delete')
        mel.eval('select -r Eyelash')
        mel.eval('setAttr "m4jeremyrrtr.invert" 0')
        mel.eval('setAttr "Eyelash.cosinePower" 2')
        mel.eval('setAttr "Eyelash.reflectedColor" -type double3 0 0 0')
    except:
        print "Lashes fix"
    try:
        mel.eval(
            'setAttr "ncl1_vr.opacityMap" -type double3 0.027972 0.027972 0.027972')
        mel.eval(
            'setAttr "ncl1_vr.reflectionColor" -type double3 0.776224 0.776224 0.776224')
    except:
        print "Lashes fix"


def convertAllShaders():
    """
    Converts each (in-use) material in the scene
    """
    # better to loop over the types instead of calling
    # ls -type targetShader
    # if a shader in the list is not registered (i.e. VrayMtl)
    # everything would fail

    for shdType in targetShaders:
        shaderColl = cmds.ls(exactType=shdType)
        if shaderColl:
            for x in shaderColl:
                # query the objects assigned to the shader
                # only convert things with members
                shdGroup = cmds.listConnections(x, type="shadingEngine")
                setMem = cmds.sets(shdGroup, query=True)
                if setMem:
                    ret = doMapping(x)


def doMapping(inShd):
    """
    Figures out which attribute mapping to use, and does the thing.

    @param inShd: Shader name
    @type inShd: String
    """
    ret = None

    shaderType = cmds.objectType(inShd)
    print("-*-**-"*10)
    print(shaderType, inShd)
    if 'phong' in shaderType:
        #ret = shaderToAiStandard(inShd, 'aiStandardSurface', mappingPhong)
        ret = shaderToAiStandard(inShd, 'aiStandard', mappingPhong)
        print(inShd, "Converted")
        convertPhong(inShd, ret)

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
        assignToNewShader(inShd, ret)


def assignToNewShader(oldShd, newShd):
    """
    Creates a shading group for the new shader, and assigns members of the old shader to it

    @param oldShd: Old shader to upgrade
    @type oldShd: String
    @param newShd: New shader
    @type newShd: String
    """

    retVal = False

    shdGroup = cmds.listConnections(oldShd, type="shadingEngine")

    # print 'shdGroup:', shdGroup

    if shdGroup:
        if "Eye" in newShd or "Cornea" in newShd or "Tear" in newShd:
            print "=========" + newShd
            # CHELO LINE...
            cmds.connectAttr(newShd + '.outColor',
                             shdGroup[0] + '.aiSurfaceShader', force=True)
        else:
            cmds.connectAttr(newShd + '.outColor',
                             shdGroup[0] + '.surfaceShader', force=True)
            cmds.delete(oldShd)

        '''
		if replaceShaders:
			cmds.connectAttr(newShd + '.outColor', shdGroup[0] + '.surfaceShader', force=True)
			#cmds.delete(oldShd)
		else:
			cmds.connectAttr(newShd + '.outColor', shdGroup[0] + '.aiSurfaceShader', force=True)
		'''
        retVal = True

    return retVal


def setupConnections(inShd, fromAttr, outShd, toAttr):
    conns = cmds.listConnections(
        inShd + '.' + fromAttr, d=False, s=True, plugs=True)
    if conns:
        cmds.connectAttr(conns[0], outShd + '.' + toAttr, force=True)
        return True

    return False


def shaderToAiStandard(inShd, nodeType, mapping):
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

    if ':' in inShd:
        aiName = inShd.rsplit(':')[-1] + '_ai'
    else:
        aiName = inShd + '_ai'

    # print 'creating '+ aiName
    aiNode = cmds.shadingNode(nodeType, name=aiName, asShader=True)
    for chan in mapping:
        fromAttr = chan[0]
        toAttr = chan[1]

        try:
            if cmds.objExists(inShd + '.' + fromAttr):
                # print '\t', fromAttr, ' -> ', toAttr

                if not setupConnections(inShd, fromAttr, aiNode, toAttr):
                    # copy the values
                    val = cmds.getAttr(inShd + '.' + fromAttr)
                    setValue(aiNode + '.' + toAttr, val)
        except:
            print("nothing to connect...")

    # print 'Done. New shader is ', aiNode

    return aiNode


def setValue(attr, value):
    """Simplified set attribute function.

    @param attr: Attribute to set. Type will be queried dynamically
    @param value: Value to set to. Should be compatible with the attr type.
    """

    aType = None

    if cmds.objExists(attr):
        # temporarily unlock the attribute
        isLocked = cmds.getAttr(attr, lock=True)
        if isLocked:
            cmds.setAttr(attr, lock=False)

        # one last check to see if we can write to it
        if cmds.getAttr(attr, settable=True):
            attrType = cmds.getAttr(attr, type=True)

            # print value, type(value)

            if attrType in ['string']:
                aType = 'string'
                cmds.setAttr(attr, value, type=aType)

            elif attrType in ['long', 'short', 'float', 'byte', 'double', 'doubleAngle', 'doubleLinear', 'bool']:
                aType = None
                cmds.setAttr(attr, value)

            elif attrType in ['long2', 'short2', 'float2',  'double2', 'long3', 'short3', 'float3',  'double3']:
                if isinstance(value, float):
                    if attrType in ['long2', 'short2', 'float2',  'double2']:
                        value = [(value, value)]
                    elif attrType in ['long3', 'short3', 'float3',  'double3']:
                        value = [(value, value, value)]

                cmds.setAttr(attr, *value[0], type=attrType)

            # else:
            #    print 'cannot yet handle that data type!!'

        if isLocked:
            # restore the lock on the attr
            cmds.setAttr(attr, lock=True)


def transparencyToOpacity(inShd, outShd):
    transpMap = cmds.listConnections(
        inShd + '.transparency', d=False, s=True, plugs=True)
    if transpMap:
        # map is connected, argh...
        # need to add a reverse node in the shading tree

        # create reverse
        invertNode = cmds.shadingNode(
            'reverse', name=outShd + '_rev', asUtility=True)

        # connect transparency Map to reverse 'input'
        cmds.connectAttr(transpMap[0], invertNode + '.input', force=True)

        # connect reverse to opacity  ----DAZ needs inverted... avoid this fix! /Chelo
        #cmds.connectAttr(invertNode + '.output', outShd + '.opacity', force=True)

        # connect reverse to opacity
        cmds.connectAttr(transpMap[0], outShd + '.opacity', force=True)
    else:
        # print inShd

        transparency = cmds.getAttr(inShd + '.transparency')
        opacity = [(1.0 - transparency[0][0], 1.0 -
                    transparency[0][1], 1.0 - transparency[0][2])]

        # print opacity
        setValue(outShd + '.opacity', opacity)


def convertPhong(inShd, outShd):
    cosinePower = cmds.getAttr(inShd + '.cosinePower')
    roughness = math.sqrt(1.0 / (0.454 * cosinePower + 3.357))
    setValue(outShd + '.specularRoughness', roughness)
    setValue(outShd + '.emission', 1.0)
    setValue(outShd + '.Ks', 1.0)
    transparencyToOpacity(inShd, outShd)


def convertOptions():
    cmds.setAttr("defaultArnoldRenderOptions.GIRefractionDepth", 10)


def isOpaque(shapeName):

    mySGs = cmds.listConnections(shapeName, type='shadingEngine')
    if not mySGs:
        return 1

    surfaceShader = cmds.listConnections(mySGs[0] + ".aiSurfaceShader")

    if surfaceShader == None:
        surfaceShader = cmds.listConnections(mySGs[0] + ".surfaceShader")

    if surfaceShader == None:
        return 1

    for shader in surfaceShader:
        if cmds.attributeQuery("opacity", node=shader, exists=True) == 0:
            continue

        opacity = cmds.getAttr(shader + ".opacity")

        if opacity[0][0] < 1.0 or opacity[0][1] < 1.0 or opacity[0][2] < 1.0:
            return 0

    return 1


def setupOpacities():
    shapes = cmds.ls(type='geometryShape')
    for shape in shapes:

        if isOpaque(shape) == 0:
            # print shape + ' is transparent'
            try:
                cmds.setAttr(shape+".aiOpaque", 0)
            except:
                print "no opaque"


def convertAllPhongToArnold():

    convertAllShaders()
    setupOpacities()


def breakLashCon(mat):
    fileList = cmds.ls(type='file')
    for filetext in fileList:
        if "Lashes" in filetext or "lash" in filetext:
            try:
                f = filetext
                textureFile = cmds.getAttr(f + '.fileTextureName')
                try:
                    mel.eval('disconnectAttr %s.outColor %s.color' % (f, mat))
                except:
                    print "breakCon skiped"
            except:
                print "File Text.Error"


def convertAlltoArnoldDazFixes():
    convertAllPhongToArnold()
    # MAKE ALL GEOMETRY OPAQUEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE
    objs = mel.eval('ls -geometry')
    if objs is None:
        print "Nothing on scene"
    else:
        for o in objs:
            try:
                mel.eval('setAttr "%s.aiOpaque" 0' % o)
            except:
                print "no obj"

        i = 0
        mats = mel.eval('ls -type "aiStandardSurface"')

        if (mats != None):
            for m in mats:
                try:
                    mel.eval('setAttr "%s.Ks" 0.045' % m)
                    mel.eval(
                        'setAttr "%s.KsColor" -type double3 0.077 0.077 0.077' % m)
                except:
                    print "no phong"

                if "lashes" in mats[i] or "Lashes" in mats[i]:
                    breakLashCon(mats[i])

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
                        print "matchange skiped"
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
                        print "matchange skiped"
                if "Moisture" in mats[i]:
                    try:
                        mel.eval(
                            'setAttr "%s.opacity" -type double3 0 0 0' % mats[i])
                    except:
                        print "matchange skiped"
                if "EyeLights" in mats[i]:
                    try:
                        mel.eval(
                            'setAttr "%s.opacity" -type double3 0 0 0' % mats[i])
                    except:
                        print "matchange skiped"
                if "Tear" in mats[i]:
                    try:
                        mel.eval(
                            'setAttr "%s.opacity" -type double3 0 0 0' % mats[i])
                    except:
                        print "matchange skiped"

                i = i + 1

# =============================================================================


def removeMorphGroups():
    allowedMorphs = ("Genesis", "Brows", "Hair")
    meshList = mel.eval('ls')
    for m in meshList:
        if "BlendShapes" in m:
            keep = 0
            for a in allowedMorphs:
                if a in m:
                    # print "KEEP:::::: " + m
                    keep = 1
            if keep == 0:
                # print "DELETE:::: " + m
                cmds.delete(m)


def sceneRenamer():
    objs = mel.eval('ls')
    for o in objs:
        # print o + "  ---  " + o.replace("FBXASC046","_")
        oModif = o.replace("FBXASC045", "_")
        oModif = o.replace("FBXASC046", "_")

        oModif = oModif.replace("ShapeShapeOrig", "Shape")
        oModif = oModif.replace("ShapeShape", "Shape")
        oModif = oModif.replace("_Shape", "")
        oModif = oModif.replace("Shape", "")
        oModif = oModif.replace("FBXASC032", "_")
        oModif = oModif.replace("FBXASC048", "_0")
        oModif = oModif.replace("FBXASC049", "_1")
        oModif = oModif.replace("FBXASC050", "_2")
        oModif = oModif.replace("FBXASC051", "_3")
        oModif = oModif.replace("FBXASC052", "_4")
        oModif = oModif.replace("FBXASC053", "_5")
        oModif = oModif.replace("FBXASC054", "_6")
        oModif = oModif.replace("FBXASC055", "_7")
        oModif = oModif.replace("FBXASC056", "_8")
        oModif = oModif.replace("FBXASC057", "_9")

        print o + "  ---  " + oModif
        if o == oModif:
            pass
        else:
            try:
                cmds.rename(o, oModif)
            except:
                pass


def lowestYonScene():
    try:
        shapes = cmds.ls(type='geometryShape')
        bb = 0
        bbmin = 0
        for shape in shapes:
            bb = cmds.polyEvaluate(shape, b=True)[1][0]
            if bb < bbmin:
                bbmin = bb
        return bbmin
    except:
        pass


def compensateHip():
    try:
        print "MIN: " + str(lowestYonScene())
        lowestY = lowestYonScene()
        hipY = cmds.getAttr("hip.translateY")
        cmds.setAttr('hip.translateY', hipY+(lowestY*-1))
    except:
        pass


def delete_blendshape_target(blendshape_name, target_index):
    mc.select(d=True)
    mc.removeMultiInstance(
        blendshape_name + ".weight[%s]" % target_index, b=True)
    mc.removeMultiInstance(
        blendshape_name + ".inputTarget[0].inputTargetGroup[%s]" % target_index, b=True)


def morphIndex(figureWithMorphs, morphName):
    blendShapesList = mel.eval('aliasAttr -q %s' % figureWithMorphs)
    i = 0
    blendname = "None"
    for b in blendShapesList:
        if morphName in b:
            # Get index from list...
            blendname = blendShapesList[i+1]
            blendname = blendname.split("[")
            blendname = blendname[1].split("]")
            blendname = blendname[0]
            print str(i) + " === " + blendShapesList[i] + " ---- " + blendname

        i = i + 1
        if blendname != "None":
            return blendname


def deleteDazMorph(blendshape_name, morphName):
    # print morphIndex(blendshape_name, morphName)
    target_index = morphIndex(blendshape_name, morphName)
    delete_blendshape_target(blendshape_name, target_index)


def removeWeirdMophs(geometry):
    figureWithMorphs = geometry
    blendShapesList = mel.eval('aliasAttr -q %s' % figureWithMorphs)
    for b in blendShapesList:
        if "RIG" in b:
            deleteDazMorph(figureWithMorphs, b)


def removeAllWeirdMophsFromScene():
    allObjects = cmds.ls(l=True)
    for blendShapeGroup in allObjects:
        if cmds.nodeType(blendShapeGroup) == 'blendShape':
            print "--------------------------"
            print blendShapeGroup
            print "--------------------------"
        try:
            removeWeirdMophs(blendShapeGroup)
        except:
            pass


def scalpFix():
    try:
        mel.eval('setAttr "Scalp.cosinePower" 2')
        mel.eval('setAttr "Scalp.specularColor" -type double3 0 0 0')
        mel.eval('setAttr "Scalp.reflectivity" 0')
    except:
        pass


def gen8lagrimalFix():
    try:
        mel.eval(
            'setAttr "ncl1.transparency" -type double3 0.993007 0.993007 0.993007')
        mel.eval('setAttr "ncl1.cosinePower" 44.48951')
        mel.eval(
            'setAttr "ncl1.specularColor" -type double3 0.013986 0.013986 0.013986')
    except:
        pass


def lashFix2():
    try:
        mel.eval('setAttr "SummerLash_1006.alphaGain" 1.5')
        mel.eval('setAttr "SummerLash_1006.invert" 0')
        mel.eval('setAttr "SummerLash_1006.alphaIsLuminance" 0')
    except:
        pass


def maya2018Fix():
    jList = mel.eval('ls -type joint')
    try:
        jParent = cmds.listRelatives("hip", parent=True)[0]
        if "_Group" not in jParent:
            groupName = jParent + "_Group"
            cmds.spaceLocator(name=groupName, p=[0, 0, 0])
            jChildren = cmds.listRelatives(jParent, children=True)
    except:
        pass

    if "_Group" not in jParent:
        try:
            for j in jChildren:
                cmds.parent(j, groupName)
        except:
            pass
        cmds.delete(jParent)
    mel.eval('select -cl')


def autoIK():

    # cmds.scriptEditorInfo(suppressWarnings=True)
    # cmds.scriptEditorInfo(suppressErrors=True)

    # removeMorphGroups()

    try:
        pm.setAttr("defaultRenderGlobals.currentRenderer", "mayaSoftware")
        mel.eval('FrameAllInAllViews;')
    except:
        print "Can't set Software Render"

    jointsList = mel.eval('ls -type joint')

    count = 0
    for j in jointsList:
        if "hip" in j:
            count += 1
    if count > 10000000:
        # print "Not valid Scene... possible solution: \nWhen export chose 'Merge Clothing Into Figure Skeleton' \nFor more info read the documentation"
        errormsg = "Not valid Scene... possible solution: \nWhen export chose 'Merge Clothing Into Figure Skeleton' \nFor more info read the documentation"

        result = cmds.confirmDialog(title='DazToMaya: Not Valid Scene', message=errormsg, button=[
                                    'Ok', 'View Info'], defaultButton='Yes', cancelButton='No', dismissString='No')

    else:
        try:
            mel.eval('setAttr "Cornea.transparency" -type double3 1 1 1')
            mel.eval('setAttr "EyeMoisture.transparency" -type double3 1 1 1')
        except:
            pass
        cleanNamespace()
        cleanMatNames()
        eyeLashFix()
        eyeLashFixGen3()
        hideRootBone()
        try:
            removeLimits()
        except:
            pass

        # ROTATIONS FIX-----------------------------------
        #jointsList = mel.eval('ls -type joint')
        dazFigure = "Not Detected"
        if "Genesis" in jointsList:
            dazFigure = "Genesis1"
            genesis1rotationsFix()
        for j in jointsList:
            if "Genesis2" in j:
                genesis2rotationsFix()
                dazFigure = "Genesis2"
                break
            if "Genesis3" in j:
                genesis3rotationsFix()
                dazFigure = "Genesis3"
                break
            if "SENTINEL" in j:
                sentinelExtraFinger()
                sentinelRotationsFix()
                dazFigure = "Sentinel"
                break
            if "Genesis8" in j:

                try:
                    genesis8matfix()
                except:
                    pass
                try:
                    genesis8rotationsFix()
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
                dazFigure = "Genesis8"
                break

        # -----Probar forzar ojos correctos...... agregado para male3 lion-o...
        genesis8matfix()

        # ROTATIONS FIX-----------------------------------
        print "------------------------------------"
        print "------------------------------------"
        clampTextures()
        transparencyFix()

        try:
            FixMorphs()
        except:
            pass
        checkIfModified()
        removeHidden()
        # makeSkeleton()
        # addExtraJoints() OLLLLLLLLLLLLD

        mel.eval('modelEditor -e -displayTextures true modelPanel4')

        if dazFigure == "Sentinel":
            sentinelRemoveFinger()

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

        extendHandFingers()
        try:
            mel.eval('HIKCharacterControlsTool')
            mel.eval('hikCreateDefinition()')
        except:
            pass

        # removeAllWeirdMophsFromScene()
        try:
            compensateHip()
        except:
            pass
        try:
            dazToIk()
        except:
            pass

        mel.eval('hikCreateControlRig')

        scalpFix()
        lashFix2()
        gen8lagrimalFix()

        maya2018Fix()

        cmds.scriptEditorInfo(suppressWarnings=False)
        cmds.scriptEditorInfo(suppressErrors=False)


def btnGoHelp():
    webbrowser.open(
        "http://docs.daz3d.com/doku.php/public/read_me/index/71381/start")


def tempFun():
    try:
        if cmds.checkBox(checkSave, q=True, value=True) == True:
            configAskToSave(1)
        else:
            configAskToSave(0)
    except:
        pass


def gotoDaz():
    cmds.launch(web="https://www.daz3d.com/home")


def windowErrorNotImport():
    windowName = "d2mErrorNoImport9"

    def closeErrorWindow():
        try:
            cmds.deleteUI(windowName)
        except:
            pass
    closeErrorWindow()
    windowErrorNotImport = cmds.window(windowName, toolbox=True, maximizeButton=False, minimizeButton=False,
                                       sizeable=False, title="DazToMaya: Oops! - Nothing to Import", widthHeight=(672, 480))
    d2mLogo = os.path.expanduser(
        "~/maya/plug-ins/DazToMaya_Files/d2m_err_nf.png")
    ErrorText = "Nothing to Import.\nPrepare your character in DAZ Studio and execute DazToMaya from there first."
    cmds.columnLayout("columnName01", adjustableColumn=True)
    cmds.separator(height=10, style='none')
    cmds.text(label=ErrorText, align='center')
    cmds.separator(height=5, style='none')
    cmds.image(image=d2mLogo, width=672)
    cmds.rowColumnLayout(numberOfColumns=4, columnWidth=[
                         (1, 160), (2, 150), (3, 50)], columnSpacing=[(1, 1), (2, 0)])
    cmds.separator(height=5, style='none')
    cmds.button(label='Get Daz Studio', width=150,
                height=40, c=lambda *args: gotoDaz())
    cmds.separator(height=5, style='none')
    cmds.button(label='OK', width=150, height=40,
                c=lambda *args: closeErrorWindow())
    cmds.showWindow(windowErrorNotImport)


# -------------------------------------------------------------------
# Ask to Save with Textures Dialog-----------------------------------
# -------------------------------------------------------------------
def showWindowAskToSave():
    try:
        cmds.deleteUI(askToSaveWindowName)
    except:
        pass
    windowAskToSave = cmds.window(askToSaveWindowName, toolbox=True, maximizeButton=False,
                                  minimizeButton=False, sizeable=False, title="DazToMaya", widthHeight=(400, 200))
    cmds.columnLayout("columnName01", adjustableColumn=True)
    cmds.separator(height=10, style='none')
    cmds.text(label='Done!', font="boldLabelFont")
    cmds.separator(height=10, style='none')
    cmds.text(label="To transfer from Daz Studio to Maya you are using a Temp folder, \nnow is a good time to save the scene+textures to another location.")
    cmds.separator(height=10, style='none')

    col = [0.5, 0.5, 0.0]
    cmds.button(label='Save Scene with Textures...', bgc=col,
                command=lambda *args: btnSaveWithText(), height=40)
    cmds.separator(height=10, style='none')
    cmds.text(label="You only need to do this special save one time after import, \nso you don't depend on the Temp folder for this scene.")
    cmds.separator(height=25, style='in')
    cmds.button(label='Ok', width=200,
                c=lambda *args: closeAskToSave(), height=20)

    #cmds.iconTextButton(width=150, style='iconAndTextHorizontal',bgc=col, image1='menuIconHelp.png', label='sphere!!' )

    '''
	cmds.separator( height=5, style='none' )
	cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 10)])
	cmds.separator( height=10, style='none' )
	cmds.checkBox( label="Do not show this again." )
	cmds.setParent('..')
	'''

    cmds.showWindow(windowAskToSave)


def closeAskToSave():
    try:
        cmds.deleteUI(askToSaveWindowName)
    except:
        pass


def autoImportDaz():

    # Check if something to import....
    dazFilePath = "C:\TEMP3D\DazToMaya.fbx"
    dazFilePathMac = "/users/Shared/temp3d/DazToMaya.fbx"

    if os.path.exists(dazFilePath) == False:
        dazFilePath = dazFilePathMac
        if os.path.exists(dazFilePath) == False:
            windowErrorNotImport()
            return

    ##########mel.eval('file -import -type "FBX"  -ignoreVersion -ra true -mergeNamespacesOnClash false -namespace "CACA" -options "fbx"  -pr "C:/Android/CACA.fbx"')

    rb0 = cmds.radioButton(rButton0, q=True, sl=True)
    rb1 = cmds.radioButton(rButton1, q=True, sl=True)

    global scaleMenuValue
    scaleMenuValue = cmds.optionMenu("scaleMenu", query=True, value=True)

    try:
        pm.deleteUI(self.WindowWait)
    except:
        pass

    msgMerge = cmds.checkBox(checkMerge, query=True, value=True)
    if msgMerge != True:
        result = mel.eval("saveChanges(\"file -f -new\")")
        if result == 0:
            return
        else:
            cmds.NewScene()

    try:
        waitDialog().show()
    except:
        pass
    print "Importing Daz..."
    cmds.refresh()
    if rb0 == True:
        importFbx()
    if rb1 == True:
        mel.eval('Import')
    print "AutoIK..."

    try:
        pm.setAttr("defaultRenderGlobals.currentRenderer", "mayaSoftware")
    except:
        pass

    breakConnectionFromMaterials("specularColor")
    removeDisplacementMaps()

    # AUTOIK IF FIGURE ON SCENE.. ELSE IS A PROP...
    listAllJoints = mel.eval('ls -type joint')
    groupProps()
    if listAllJoints != None and "head" in listAllJoints:
        autoIK()
    else:
        mel.eval('viewFit -all')  # View Fit All
        clampTextures()
        try:
            mel.eval('modelEditor -e -displayTextures true modelPanel4')
        except:
            pass

    try:
        waitDialog2().close()
    except:
        pass
    try:
        pm.deleteUI(self.WindowWait2)
    except:
        pass

    try:
        cmds.deleteUI(waitWindowName)
        pm.deleteUI(self.WindowWait)
    except:
        pass
    cmds.refresh()

    sceneRenamer()
    matRefreshFix()
    # Show remember to save with textures...
    try:
        if cmds.checkBox(checkSave, q=True, value=True) == True:
            showWindowAskToSave()
    except:
        pass

    print "DazToMaya Complete!"
    #result = cmds.confirmDialog( title='DazToMaya', message="Convert Complete!", button=['Ok'], defaultButton='Yes', cancelButton='No', dismissString='No' )


def btnConvert():

    matConv = cmds.optionMenu("matConvertMenu", query=True, value=True)
    mats = mel.eval('ls -type "phong"')
    if mats == None or len(mats) < 1:
        errormsg = "Re-Convert Materials not supported yet:\nOriginal materials were already changed.\nImport again and convert to other material if needed."
        result = cmds.confirmDialog(title='DazToMaya', message=errormsg, button=[
                                    'Ok'], defaultButton='Yes', cancelButton='No', dismissString='No')
    else:
        if matConv == "Arnold":
            try:
                pm.setAttr("defaultRenderGlobals.currentRenderer", "arnold")
                convertAlltoArnoldDazFixes()
            except:
                print "can't set Arnold"

        if matConv == "Vray":
            convertToVray().startConvert()
            eyeLashesFix1()
            eyeLashesFix2()
            extraEyeFixes()
            vrayFixes()
            print "Convert Done"


def d2mstart():
    print "d2m start"
    if "2014" in mayaversion or "2015" in mayaversion or "2016" in mayaversion or "2017" in mayaversion or "2018" in mayaversion or "2019" in mayaversion or "2020" in mayaversion:
		cmds.showWindow(windowDazMain)
    else:
        print "Maya Version not Supported. Please visit www.daz3d.com"


class waitDialog(object):
    def __init__(self):
        try:
            pm.deleteUI(self.WindowWait)
        except:
            pass
        self.WindowWait = pm.window(waitWindowName, toolbox=True, maximizeButton=False,
                                    minimizeButton=False, sizeable=False, title="DazToMaya", widthHeight=(343, 55))
        cmds.columnLayout("columnName01", adjustableColumn=True)
        cmds.separator(height=20, style='in')
        cmds.text(label='Importing please wait...')
        cmds.separator(height=20, style='in')

    def show(self):
        self.WindowWait.show()

    def close(self):
        pm.deleteUI(self.WindowWait)


class waitDialog2(object):
    def __init__(self):
        try:
            pm.deleteUI(self.WindowWait2)
        except:
            pass
        self.WindowWait2 = pm.window(waitWindowName2, toolbox=True, maximizeButton=False,
                                     minimizeButton=False, sizeable=False, title="DazToMaya", widthHeight=(343, 55))
        cmds.columnLayout("columnName01", adjustableColumn=True)
        cmds.separator(height=20, style='in')
        cmds.text(label='Converting please wait...')
        cmds.separator(height=20, style='in')

    def show(self):
        self.WindowWait2.show()

    def close(self):
        pm.deleteUI(self.WindowWait2)


class convertToVray:
    replaceShaders = True
    targetShaders = ['phong']

    mappingVRMtl = [
        ['diffuseColorAmount', 'Kd'],
        ['color', 'color'],  # or diffuseColor ?
        ['roughnessAmount', 'diffuseRoughness'],
        ['reflectionColorAmount', 'Ks'],
        ['reflectionColor', 'KsColor'],
        ['refractionColorAmount', 'Kt'],
        ['refractionColor', 'KtColor'],
        ['refractionIOR', 'IOR'],
        ['opacityMap', 'opacity'],
        ['useFresnel', 'specularFresnel'],
        ['anisotropyRotation', 'anisotropyRotation'],
        ['translucencyColor', 'KsssColor'],
        ['fogColor', 'transmittance'],
        ['fogColor', 'sssRadius'],
        ['normalCamera', 'normalCamera']  # or Bump ?
    ]

    mappingPhong = [
        ['color', 'color'],
        ['transparency', 'opacityMap']
    ]

    def convertUi(self):
        self.convertAllShaders()
        # setupOpacities()

    def convertAllShaders(self):
        """
        Converts each (in-use) material in the scene
        """
        # better to loop over the types instead of calling
        # ls -type targetShader
        # if a shader in the list is not registered (i.e. VrayMtl)
        # everything would fail

        for shdType in self.targetShaders:
            shaderColl = cmds.ls(exactType=shdType)
            if shaderColl:
                for x in shaderColl:
                    # query the objects assigned to the shader
                    # only convert things with members
                    shdGroup = cmds.listConnections(x, type="shadingEngine")
                    setMem = cmds.sets(shdGroup, query=True)
                    if setMem:
                        ret = self.doMapping(x)

    def doMapping(self, inShd):
        """
        Figures out which attribute mapping to use, and does the thing.

        @param inShd: Shader name
        @type inShd: String
        """
        ret = None

        shaderType = cmds.objectType(inShd)
        if 'phong' in shaderType:
            ret = self.shaderToAiStandard(inShd, 'VRayMtl', self.mappingPhong)
            self.convertPhong(inShd, ret)

        if ret:
            # assign objects to the new shader
            self.assignToNewShader(inShd, ret)

    def assignToNewShader(self, oldShd, newShd):
        """
        Creates a shading group for the new shader, and assigns members of the old shader to it

        @param oldShd: Old shader to upgrade
        @type oldShd: String
        @param newShd: New shader
        @type newShd: String
        """

        retVal = False

        shdGroup = cmds.listConnections(oldShd, type="shadingEngine")

        if shdGroup:
            print ">>>>>>>>" + newShd
            if "Eye" in newShd:
                try:
                    # CHELO LINE...
                    cmds.connectAttr(
                        newShd + '.outColor', shdGroup[0] + '.aiSurfaceShader', force=True)
                except:
                    pass
            else:
                try:
                    cmds.connectAttr(newShd + '.outColor',
                                     shdGroup[0] + '.surfaceShader', force=True)
                    cmds.delete(oldShd)
                except:
                    pass

            '''
			if self.replaceShaders:
				cmds.connectAttr(newShd + '.outColor', shdGroup[0] + '.surfaceShader', force=True)
				#cmds.delete(oldShd)
			else:
				cmds.connectAttr(newShd + '.outColor', shdGroup[0] + '.aiSurfaceShader', force=True)
			'''
            retVal = True

        return retVal

    def setupConnections(self, inShd, fromAttr, outShd, toAttr):
        conns = cmds.listConnections(
            inShd + '.' + fromAttr, d=False, s=True, plugs=True)
        if conns:
            cmds.connectAttr(conns[0], outShd + '.' + toAttr, force=True)
            return True

        return False

    def shaderToAiStandard(self, inShd, nodeType, mapping):
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
        if ':' in inShd:
            aiName = inShd.rsplit(':')[-1] + '_vr'
        else:
            aiName = inShd + '_vr'

        aiNode = cmds.shadingNode(nodeType, name=aiName, asShader=True)
        for chan in mapping:
            fromAttr = chan[0]
            toAttr = chan[1]

            if cmds.objExists(inShd + '.' + fromAttr):
                if not self.setupConnections(inShd, fromAttr, aiNode, toAttr):
                    # copy the values
                    val = cmds.getAttr(inShd + '.' + fromAttr)
                    self.setValue(aiNode + '.' + toAttr, val)

        return aiNode

    def setValue(self, attr, value):
        """Simplified set attribute function.

        @param attr: Attribute to set. Type will be queried dynamically
        @param value: Value to set to. Should be compatible with the attr type.
        """

        aType = None

        if cmds.objExists(attr):
            # temporarily unlock the attribute
            isLocked = cmds.getAttr(attr, lock=True)
            if isLocked:
                cmds.setAttr(attr, lock=False)

            # one last check to see if we can write to it
            if cmds.getAttr(attr, settable=True):
                attrType = cmds.getAttr(attr, type=True)

                # print value, type(value)

                if attrType in ['string']:
                    aType = 'string'
                    cmds.setAttr(attr, value, type=aType)

                elif attrType in ['long', 'short', 'float', 'byte', 'double', 'doubleAngle', 'doubleLinear', 'bool']:
                    aType = None
                    cmds.setAttr(attr, value)

                elif attrType in ['long2', 'short2', 'float2',  'double2', 'long3', 'short3', 'float3',  'double3']:
                    if isinstance(value, float):
                        if attrType in ['long2', 'short2', 'float2',  'double2']:
                            value = [(value, value)]
                        elif attrType in ['long3', 'short3', 'float3',  'double3']:
                            value = [(value, value, value)]

                    cmds.setAttr(attr, *value[0], type=attrType)

                # else:
                #    print 'cannot yet handle that data type!!'

            if isLocked:
                # restore the lock on the attr
                cmds.setAttr(attr, lock=True)

    def transparencyToOpacity(self, inShd, outShd):
        transpMap = cmds.listConnections(
            inShd + '.transparency', d=False, s=True, plugs=True)
        if transpMap:
            # map is connected, argh...
            # need to add a reverse node in the shading tree

            # create reverse
            #invertNode = cmds.shadingNode('reverse', name=outShd + '_rev', asUtility=True)

            # connect transparency Map to reverse 'input'
            #cmds.connectAttr(transpMap[0], invertNode + '.input', force=True)

            # connect reverse to opacity

            #cmds.connectAttr(transpMap[0], outShd + '.opacityMap', force=True)
            try:
                print "-*-*-*-*-*-*-"
                print transpMap[0]
                transMapToInvert = transpMap[0].replace(".outTransparency", "")
                mel.eval('setAttr "%s.invert" 1' % transMapToInvert)
            except:
                print "already inv"

    def convertPhong(self, inShd, outShd):
        cosinePower = cmds.getAttr(inShd + '.cosinePower')
        roughness = math.sqrt(1.0 / (0.454 * cosinePower + 3.357))

        transpValues = cmds.getAttr(inShd + '.transparency')
        caca2 = str(transpValues[0]).split(",")

        transpR = float(str(caca2[0])[1:])
        transpG = float(str(caca2[1])[1:])
        transpB = float(str(caca2[2])[1:-1])

        #setValue(outShd + '.opacityMap', 1.0)
        try:
            cmds.setAttr(outShd + '.' + "opacityMap", 1.0 - transpR,
                         1.0 - transpG, 1.0 - transpB, type='double3')
        except:
            print "map detected"
        self.transparencyToOpacity(inShd, outShd)

    def convertVrayMtl(self, inShd, outShd):

        # anisotropy from -1:1 to 0:1
        anisotropy = cmds.getAttr(inShd + '.anisotropy')
        anisotropy = (anisotropy * 2.0) + 1.0
        setValue(outShd + '.specularAnisotropy', anisotropy)

        # do we need to check lockFresnelIORToRefractionIOR
        # or is fresnelIOR modified automatically when refractionIOR changes ?
        ior = 1.0
        if cmds.getAttr(inShd + '.lockFresnelIORToRefractionIOR'):
            ior = cmds.getAttr(inShd + '.refractionIOR')
        else:
            ior = cmds.getAttr(inShd + '.fresnelIOR')

        reflectivity = 1.0
        connReflectivity = cmds.listConnections(
            outShd + '.Ks', d=False, s=True, plugs=True)
        if not connReflectivity:
            reflectivity = cmds.getAttr(outShd+'.Ks')

        frontRefl = (ior - 1.0) / (ior + 1.0)
        frontRefl *= frontRefl

        setValue(outShd + '.Ksn', frontRefl * reflectivity)

        reflGloss = cmds.getAttr(inShd + '.reflectionGlossiness')
        setValue(outShd + '.specularRoughness', 1.0 - reflGloss)

        refrGloss = cmds.getAttr(inShd + '.refractionGlossiness')
        setValue(outShd + '.refractionRoughness', 1.0 - refrGloss)

        # bumpMap, bumpMult, bumpMapType ?

        if cmds.getAttr(inShd + '.sssOn'):
            setValue(outShd + '.Ksss', 1.0)

        # selfIllumination is missing  but I need to know the exact attribute name in maya or this will fail

    def convertOptions():
        cmds.setAttr("defaultArnoldRenderOptions.GIRefractionDepth", 10)

    def isOpaque(shapeName):

        mySGs = cmds.listConnections(shapeName, type='shadingEngine')
        if not mySGs:
            return 1

        surfaceShader = cmds.listConnections(mySGs[0] + ".aiSurfaceShader")

        if surfaceShader == None:
            surfaceShader = cmds.listConnections(mySGs[0] + ".surfaceShader")

        if surfaceShader == None:
            return 1

        for shader in surfaceShader:
            if cmds.attributeQuery("opacity", node=shader, exists=True) == 0:
                continue

            opacity = cmds.getAttr(shader + ".opacity")

            if opacity[0][0] < 1.0 or opacity[0][1] < 1.0 or opacity[0][2] < 1.0:
                return 0

        return 1

    def setupOpacities():
        shapes = cmds.ls(type='geometryShape')
        for shape in shapes:

            if isOpaque(shape) == 0:
                # print shape + ' is transparent'
                cmds.setAttr(shape+".aiOpaque", 0)

    def startConvert(self):
        try:
            pm.setAttr("defaultRenderGlobals.currentRenderer", "vray")
        except:
            print "can't set Vray"
        try:
            mel.eval('setAttr "EyeMoisture.transparency" -type double3 1 1 1')
            mel.eval('setAttr "Cornea.transparency" -type double3 1 1 1')
        except:
            pass
        print "Done."
        self.convertUi()
