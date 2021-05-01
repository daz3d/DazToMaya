from __future__ import absolute_import
from __future__ import print_function
import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
from sys import version_info
if version_info[0] < 3:
    pass # Python 2 has built in reload
elif version_info[0] == 3 and version_info[1] <= 4:
    from imp import reload # Python 3.0 - 3.4 
else:
    from importlib import reload # Python 3.5+


commandName = 'daztomaya'

class DazToMayaClass( OpenMayaMPx.MPxCommand ):
    
    def __init__(self):
        ''' Constructor. '''
        OpenMayaMPx.MPxCommand.__init__(self)
    
    def doIt(self, args):
        ''' Command execution. '''     
        import sys
        import os
        from os import path
        import maya.mel as mel
        import maya.cmds as cmds
        scriptPath = os.path.expanduser("~/maya/plug-ins/DazToMaya_Files/d2m.py")
        scriptPathPyc = os.path.expanduser("~/maya/plug-ins/DazToMaya_Files/d2m.pyc")
        scriptPathPyMac = "/users/Shared/Autodesk/maya/plug-ins/DazToMaya_Files/d2m.py"
        scriptPathPycMac = "/users/Shared/Autodesk/maya/plug-ins/DazToMaya_Files/d2m.pyc"
        if os.path.exists(scriptPathPyc): scriptPath = scriptPathPyc
        if os.path.exists(scriptPath): scriptPath = scriptPath
        if os.path.exists(scriptPathPyMac): scriptPath = scriptPathPyMac
        if os.path.exists(scriptPathPycMac): scriptPath = scriptPathPycMac
        def psource(module):
            file = os.path.basename( module )
            dir = os.path.dirname( module )
            toks = file.split( '.' )
            modname = toks[0]
            if( os.path.exists( dir ) ):
                paths = sys.path
                pathfound = 0
                for path in paths:
                    if(dir == path):
                        pathfound = 1
                if not pathfound:
                    sys.path.append( dir )
            exec(('import ' + modname), globals())
            exec(( 'reload( ' + modname + ' )' ), globals())
            return modname
        def DazToMayastart():
            # When you import a file you must give it the full path
            print("d2mRun: " + scriptPath)
            psource( scriptPath )
        print("executed")
        DazToMayastart()
        #-------------------------------------------------------------------------------------

def cmdCreator():
    ''' Create an instance of our command. '''
    return OpenMayaMPx.asMPxPtr( DazToMayaClass() )

def initializePlugin( mobject ):
    import maya.mel as mel
    import maya.cmds as cmds
    import sys
    import os
    from os import path
    from sys import path as sysPath

    #--------------------- ADD ITEMS IN MENU --------------------------
    scriptPath = os.path.expanduser("~/maya/plug-ins/DazToMaya_Files")
    scriptPathMac = "/users/Shared/Autodesk/maya/plug-ins/DazToMaya_Files"
    if os.path.exists(scriptPathMac): scriptPath = scriptPathMac
    sysPath.append(scriptPath)
    import d2m_menu
    d2m_menu.start()
    #--------------------- ADD ITEMS IN MENU // END --------------------------
    
    ''' Initialize the plug-in when Maya loads it. '''
    mplugin = OpenMayaMPx.MFnPlugin( mobject, "Daz3D", "1.7" )
    try:
        mplugin.registerCommand( commandName, cmdCreator )
    except:
        sys.stderr.write( 'Failed to register command: ' + commandName )

def uninitializePlugin( mobject ):
    ''' Uninitialize the plug-in when Maya un-loads it. '''
    print("Unloaded!")
    import d2m_menu
    d2m_menu.remove() 
    mplugin = OpenMayaMPx.MFnPlugin( mobject )
    try:
        mplugin.deregisterCommand( commandName )
    except:
        sys.stderr.write( 'Failed to unregister command: ' + commandName )