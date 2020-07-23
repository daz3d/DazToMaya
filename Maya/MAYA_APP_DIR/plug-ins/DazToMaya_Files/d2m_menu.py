import maya.cmds as cmds
import pymel.core as pm
import os
import xml.etree.ElementTree as ET
import maya.mel as mel
class generateMenu():
	import maya.cmds as cmds
	import pymel.core as pm
	import os
	import xml.etree.ElementTree as ET
	import maya.mel as mel

	menuName = "- Daz3D -" #parent menu to create if not found
	oldMenuNameToDelete = "DazToMaya" #old menu to delete if found
	gMainWindow = mel.eval('$tmpVar=$gMainWindow')
	mayaVersion = cmds.about(v=True)
	pathMayaIcons = os.path.expanduser("~/maya/")
	pathIcon = os.path.expanduser("~/maya/plug-ins/DazToMaya_Files/DazToMaya_Icon.png")
	pathIconMac = "/users/Shared/Autodesk/maya/plug-ins/DazToMaya_Files/DazToMaya_Icon.png"
	
	try:
		print("path icon: ", pathIcon)
		print("path icon: ", pathMayaIcons + mayaVersion + "/prefs/icons/DazToMaya_Icon.png")
		cmds.sysFile( pathIcon, copy= pathMayaIcons + mayaVersion + "/prefs/icons/DazToMaya_Icon.png" )# Windows
	except:
		pass
	try:
		cmds.sysFile( pathIconMac, copy= "/users/Shared/Autodesk/maya/icons/DazToMaya_Icon.png" )# Mac
	except:
		pass
	try:
		cmds.sysFile( pathIconMac, copy= "/users/Shared/Autodesk/maya/" + mayaVersion + "/icons/DazToMaya_Icon.png" )# Mac
	except:
		pass
	
	
	def menuCreate(self, gMainWindow, menuName):
		parentMenu = cmds.menu(parent=gMainWindow, tearOff=True, label=menuName)
		return parentMenu
	
	def menuSubItemCreate(self, menuId):
		# cmds.menuItem( parent=menuId, d=True, dl="DazToMaya" )
		cmds.menuItem( parent=menuId, l="DazToMaya", i="DazToMaya_Icon.png", c="mel.eval('daztomaya')")
	
	def menuSubItemFind(self, menuId, menuSubItemName):
		menuItems = cmds.menu(menuId, query=True, itemArray=True)
		if menuItems == None:
			return "EMPTY"
		else:
			for mi in menuItems:
				itemLabel = cmds.menuItem( mi, query=True, label=True )
				if itemLabel == menuSubItemName:
					return mi
	
	def menuFind(self, menuName):
		for x in range(0,200):
			menuNumber = "menu" + str(x)
			try:
				itemLabel = cmds.menu(menuNumber, query=True, label=True)
				if itemLabel == menuName:
					return "menu" + str(x)
			except:
				pass

	#---- START ------------------------------------------------------------------
	def start(self):
		mayamenu = self.menuFind(self.oldMenuNameToDelete)
		threedtoallmenu = self.menuFind(self.menuName)

		if mayamenu != None:
			cmds.deleteUI(mayamenu) #Eliminar menu
			
		if threedtoallmenu != None:
			menuSubItem = self.menuSubItemFind(threedtoallmenu, ">> Import from DAZ Studio") #Depende del producto
			try:
				cmds.deleteUI(menuSubItem)
			except:
				pass
			menuSubItem = self.menuSubItemFind(threedtoallmenu, "DazToMaya") #Depende del producto
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
			menuSubItem = self.menuSubItemFind(threedtoallmenu, "DazToMaya")
			if menuSubItem != None and menuSubItem != "EMPTY":
				cmds.deleteUI(menuSubItem)
			menuSubItem = self.menuSubItemFind(threedtoallmenu, ">> Import from DAZ Studio")
			if menuSubItem != None and menuSubItem != "EMPTY":
				cmds.deleteUI(menuSubItem)
			menuSubItem = self.menuSubItemFind(threedtoallmenu, "DazToMaya")
			if menuSubItem == "EMPTY":
				cmds.deleteUI(threedtoallmenu)
				
			
			
print "START"
def start():
	generateMenu().start()
def remove():
	generateMenu().remove()
#generateMenu().remove()
start()