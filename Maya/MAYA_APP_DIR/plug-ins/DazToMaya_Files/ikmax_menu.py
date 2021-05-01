from __future__ import absolute_import
from __future__ import print_function
import maya.cmds as cmds
import pymel.core as pm
import os
import xml.etree.ElementTree as ET
import maya.mel as mel
from six.moves import range
class generateMenu():
	import maya.cmds as cmds
	import pymel.core as pm
	import os
	import xml.etree.ElementTree as ET
	import maya.mel as mel

	menuName = "- Daz 3D -" #parent menu to create if not found
	oldMenuNameToDelete = "IKMAX" #old menu to delete if found
	gMainWindow = mel.eval('$tmpVar=$gMainWindow')
	mayaVersion = cmds.about(v=True)
	pathMayaIcons = os.path.expanduser("~/maya/")
	pathIcon = os.path.expanduser("~/maya/plug-ins/IKMAX_Files/IKMAX_icon.png")
	pathIconMac = "/users/Shared/Autodesk/maya/plug-ins/IKMAX_Files/IKMAX_icon.png"
	
	try:
		cmds.sysFile( pathIcon, copy= pathMayaIcons + mayaVersion + "/prefs/icons/IKMAX_icon.png" )# Windows
	except:
		pass
	try:
		cmds.sysFile( pathIconMac, copy= "/users/Shared/Autodesk/maya/icons/IKMAX_icon.png" )# Mac
	except:
		pass
	try:
		cmds.sysFile( pathIconMac, copy= "/users/Shared/Autodesk/maya/" + mayaVersion + "/icons/IKMAX_icon.png" )# Mac
	except:
		pass
	
	
	def menuCreate(self, gMainWindow, menuName):
		parentMenu = cmds.menu(parent=gMainWindow, tearOff=True, label=menuName)
		return parentMenu
	
	def menuSubItemCreate(self, menuId):
		cmds.menuItem( parent=menuId, d=True, dl="IKMAX" )
		cmds.menuItem( parent=menuId, l=">> Rig Character", i="IKMAX_icon.png", c="mel.eval('ikmax')")
	
	def menuSubItemFind(self, menuId, menuSubItemName):
		menuItems = cmds.menu(menuId, query=True, itemArray=True)
		if menuItems == None:
			return "EMPTY"
		else:
			for mi in menuItems:
				itemLabel = cmds.menuItem( mi, query=True, label=True )
				if itemLabel == menuSubItemName:
					print('SubItem Found')
					return mi
	
	def menuFind(self, menuName):
		for x in range(0,200):
			menuNumber = "menu" + str(x)
			try:
				itemLabel = cmds.menu(menuNumber, query=True, label=True)
				if itemLabel == menuName:
					print("Found!", str(x))
					return "menu" + str(x)
			except:
				pass


	def daztomayaMenuFix(self):
		#Source Files:
		fileDaztomayaNew = os.path.expanduser("~/maya/plug-ins/IKMAX_Files/fix_dtm.py")
		fileDaztomayaMenuNew = os.path.expanduser("~/maya/plug-ins/IKMAX_Files/fix_dtmmenu.pyc")
		
		#Target to Overwrite:
		fileDaztomayaOld = os.path.expanduser("~/maya/plug-ins/DazToMaya.py")
		fileDaztomayaMenuOld = os.path.expanduser("~/maya/plug-ins/DazToMaya_Files/ikmax_menu.pyc")
		
		#Check if DazToMaya files found, overwrite them.
		
		if os.path.isfile(fileDaztomayaOld):
			try:
				cmds.sysFile( fileDaztomayaNew, copy=fileDaztomayaOld )# Windows
				cmds.sysFile( fileDaztomayaMenuNew, copy=fileDaztomayaMenuOld )# Windows
			except:
				pass
			
	#---- START ------------------------------------------------------------------
	def start(self):
		mayamenu = self.menuFind(self.oldMenuNameToDelete)
		threedtoallmenu = self.menuFind(self.menuName)

		if mayamenu != None:
			cmds.deleteUI(mayamenu) #Eliminar menu
			
		if threedtoallmenu != None:
			menuSubItem = self.menuSubItemFind(threedtoallmenu, ">> Rig Character")
			try:
				cmds.deleteUI(menuSubItem)
			except:
				pass
			menuSubItem = self.menuSubItemFind(threedtoallmenu, "IKMAX") #Depende del producto
			try:
				cmds.deleteUI(menuSubItem)
			except:
				pass
			self.menuSubItemCreate(threedtoallmenu)
		else:
			threedtoallmenu = self.menuCreate(self.gMainWindow, self.menuName)
			self.menuSubItemCreate(threedtoallmenu)
	
	#---- REMOVE MENU ------------------------------------------------------------
	# Remove subItems, if main menu empty remove menu too
	
	def remove(self):
		threedtoallmenu = self.menuFind(self.menuName)
		
		if threedtoallmenu != None:
			menuSubItem = self.menuSubItemFind(threedtoallmenu, "IKMAX")
			if menuSubItem != None and menuSubItem != "EMPTY":
				cmds.deleteUI(menuSubItem)
			menuSubItem = self.menuSubItemFind(threedtoallmenu, ">> Rig Character")
			if menuSubItem != None and menuSubItem != "EMPTY":
				cmds.deleteUI(menuSubItem)
			menuSubItem = self.menuSubItemFind(threedtoallmenu, "IKMAX")
			if menuSubItem == "EMPTY":
				cmds.deleteUI(threedtoallmenu)
				
			
			
print("START")
def start():
	generateMenu().start()
def remove():
	generateMenu().remove()
#generateMenu().remove()
start()