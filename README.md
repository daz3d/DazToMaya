# Daz To Maya Bridge
A Daz Studio Plugin based on Daz Bridge Library, allowing transfer of Daz Studio characters and props to Maya.

* Owner: [Daz 3D][OwnerURL] – [@Daz3d][TwitterURL]
* License: [Apache License, Version 2.0][LicenseURL] - see ``LICENSE`` and ``NOTICE`` for more information.
* Offical Release: [Daz to Maya Bridge][ProductURL]
* Official Project: [github.com/daz3d/DazToMaya][RepositoryURL]


## Table of Contents
1. About the Bridge
2. Prerequisites
3. How to Install
4. How to Use
5. How to Build
6. How to Develop
7. Directory Structure


## 1. About the Bridge
This is an updated version of the original DazToMaya Bridge that is rewritten in C++ using the Daz Bridge Library as a foundation.  This allows it to share the same source code and features with other bridges such as the DazToUnreal and DazToBlender Bridges.

The Daz To maya Bridge consists of two parts: a Daz Studio Plugin which exports assets to Maya and a Maya module to import the assets and help recreate the look of the original Daz Studio asset in Maya.


## 2. Prerequisites
* A compatible version of the [Daz Studio][DazStudioURL] application
  * Minimum: 4.10
* A compatible version of the [Maya][MayaURL] application
  * Minimum: 2019
  * [PyMEL](https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2022/ENU/Maya-Scripting/files/GUID-2AA5EFCE-53B1-46A0-8E43-4CD0B2C72FB4-htm.html)
* Operating System:
  * Windows 7 or newer
  * macOS 10.13 (High Sierra) or newer


## 3. How do I install the Daz To Maya Bridge?
### Daz Studio:
-	You can install the Daz To Maya Bridge automatically through the Daz Install Manager.  This will automatically add a new menu option under File -> Send To -> Daz To Maya.
-	Alternatively, you can manually install by downloading the latest build from Github Release Page and following the instructions there to install into Daz Studio.

### Maya:
1.	The Daz Studio Plugin comes embedded with an installer for the Maya Bridge module.  From the Daz To Maya Bridge dialog, there is now a section in the Advanced Settings section for Installing the Maya module.
2.	Click the “Install Plugin...” button.  You will see a window popup to choose a folder to install the Maya module.  The starting folder should be the default location for maya plugins and modules.
3.	On Windows, the path to install modules should be “Documents\maya\modules”.  On Mac, the path should be “/Users/<username>/Library/Preferences/Autodesk/maya/modules”.
4.	For most Maya setups, you should be able to just click “Select Folder”.  You will then see a confirmation dialog stating if the plugin installation was successful.
5.	If Maya is running, you will need to restart for the Daz To Maya Bridge module to load.
6.	In Maya, you should now see a “DazToMaya” tab in the Maya Shelf toolbar.  Click this tab to find the DazToMaya options.
7.	If you have tabs disabled in the Maya Shelf, you may need to click the “cog” icon and select “Shelf Tabs” to find and select the “DazToMaya” tab.
8.	From the DazToMaya tab of the Shelf, you should now see an icon for “DAZ IMPORT”.  You are done installing Daz To Maya Bridge!
9. If you recieve an error when trying to click the "DAZ IMPORT" icon, make sure you have [PyMEL installed](https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2022/ENU/Maya-Scripting/files/GUID-2AA5EFCE-53B1-46A0-8E43-4CD0B2C72FB4-htm.html).

 
## 4. How do I use the Maya Bridge?
1.	Open your character in Daz Studio.
2.	Make sure any clothing or hair is parented to the main body.
3.	From the main menu, select File -> Send To -> Daz To Maya.  Alternatively, you may select File -> Export and then choose "Maya Ascii File" or "Maya Binary File" from the Save as type drop down option.
4.	A dialog will pop up: choose what type of conversion you wish to do, “Static Mesh” (no skeleton), “Skeletal Mesh” (Character or with joints),  "Animation", or "Environment" (all meshes in scene).
5.	To enable Morphs or Subdivision levels, click the CheckBox to Enable that option, then click the "Choose Morphs" or "Bake  Subdivisions" button to configure your selections.
6.	Click Accept, then wait for a dialog popup to notify you when to switch to Maya.
7.	From Maya, click the “DAZ IMPORT” icon from the DazToMaya toolshelf to open the DazToMaya Bridge dialog window.
8.	Select “Auto-Import”.

### Morphs:
-	If you enabled the Export Morphs option, there will be a “Morphs” node in the Outliner panel.  Select this node and you will see morph sliders appear in the “Attribute Editor” panel, under the “Extra Attributes” heading.

### Animation:
-	To use the “Animation” asset type option, your Figure must use animations on the Daz Studio “Timeline” system.  
-	If you are using “aniMate” or “aniBlocks” based animations, you need to right-click in the "aniMate” panel and select “Bake To Studio Keyframes”.  
-	Once your animation is on the “Timeline” system, you can start the transfer using File -> Send To -> Daz To Maya.  
-	The transferred animation should now be usable through the Maya Animation interface.

### Subdivision Support:
-	Daz Studio uses Catmull-Clark Subdivision Surface technology which is a mathematical way to describe an infinitely smooth surface in a very efficient manner. Similar to how an infinitely smooth circle can be described with just the radius, the base resolution mesh of a Daz Figure is actually the mathematical data in an equation to describe an infinitely smooth surface. For Software which supports Catmull-Clark Subdivision and subdivision surface-based morphs (also known as HD Morphs), there is no loss in quality or detail by exporting the base resolution mesh (subdivision level 0), and then using the native Catmull-Clark subdivision functions.
-	For Software which does not fully support Catmull-Clark Subdivision or HD Morphs, we can "Bake" additional subdivision detail levels into the mesh to more closely approximate the detail of the original surface. However, baking each additional subdivision level requires exponentially more CPU time, memory, and storage space.  **If you do not have a high-end PC, it is likely that your system may run out of memory and crash if you set the exported subdivision level above 2.**
-	When you enable Bake Subdivision options in the Daz To Maya bridge, the asset is transferred to Maya as a standard mesh with higher resolution vertex counts.


## 5. How to Build
Setup and configuration of the build system is done via CMake to generate project files for Windows or Mac.  The CMake configuration requires:
-	Modern CMake (tested with 3.27.2 on Win and 3.27.0-rc4 on Mac)
-	Daz Studio 4.5+ SDK (from DIM)
-	Fbx SDK 2020.1 (win) / Fbx SDK 2015.1 (mac)
-	OpenSubdiv 3.4.4

(Please note that you MUST use the Qt 4.8.1 build libraries that are built-into the Daz Studio SDK.  Using an external Qt library will result in build errors and program instability.)

Download or clone the DazToMaya github repository to your local machine. The Daz Bridge Library is linked as a git submodule to the DazBridge repository. Depending on your git client, you may have to use `git submodule init` and `git submodule update` to properly clone the Daz Bridge Library.

The build setup process is designed to be run with CMake gui in an interactive session.  After setting up the source code folder and an output folder, the user can click Configure.  CMake will stop during the configurtaion process to prompt the user for the following paths:

-	DAZ_SDK_DIR – the root folder to the Daz Studio 4.5+ SDK.  This MUST be the version purchased from the Daz Store and installed via the DIM.  Any other versions will NOT work with this source code project and result in build errors and failure. example: C:/Users/Public/Documents/My DAZ 3D Library/DAZStudio4.5+ SDK
-	DAZ_STUDIO_EXE_DIR – the folder containing the Daz Studio executable file.  example: C:/Program Files/DAZ 3D/DAZStudio4
-	FBX_SDK_DIR – the root folder containing the “include” and “lib” subfolders.  example: C:/Program Files/Autodesk/FBX/FBX SDK/2020.0.1
-	OPENSUBDIV_DIR – root folder containing the “opensubdiv”, “examples”, “cmake” folders.  It assumes the output folder was set to a subfolder named “build” and that the osdCPU.lib or libosdCPU.a static library files were built at: <root>/build/lib/Release/osdCPU.lib or <root>/build/lib/Release/libosdCPU.a.  A pre-built library for Mac and Windows can be found at https://github.com/danielbui78/OpenSubdiv/releases that contains the correct location for include and prebuilt Release static library  binaries.  If you are not using this precompiled version, then you must ensure the correct location for the OPENSUBDIV_INCLUDE folder path and OPENSUBDIV_LIB filepath.

Once these paths are correctly entered into the CMake gui, the Configure button can be clicked and the configuration process should resume to completion.  The project files can then be generated and the project may be opened.  Please note that a custom version of Qt 4.8 build tools and libraries are included in the DAZ_SDK_DIR.  If another version of Qt is installed in your system and visible to CMake, it will likely cause errors with finding the correct version of Qt supplied in the DAZ_SDK_DIR and cause build errors and failure.

The resulting project files should have “DzBridge-Maya", “DzBridge Static” and "MayaModule ZIP" as project targets.  The DLL/DYLIB binary file produced by "DzBridge-Maya" should be a working Daz Studio plugin.  The "MayaModule ZIP" project contains the automation scripts which package the Maya Module files into a zip file and prepares it for embedding into the main Daz Studio plugin DLL/DYLIB binary.


## 6. How to Modify and Develop
The Daz Studio Plugin source code is contained in the `DazStudioPlugin` folder. The main C++ class entrypoint for the plugin is "DzBlenderAction" (.cpp/.h).  The Maya Module source code and resources are available in the `/Maya/MAYA_APP_DIR/modules/DazToMaya` folder.  Daz Studio SDK API and Qt API reference information can be found within the "DAZ Studio SDK Docs" package.  On Windows, the main page of this documentation is installed by default to: `C:\Users\Public\Documents\My DAZ 3D Library\DAZStudio4.5+ SDK\docs\index.html`.

**DZ_BRIDGE_NAMESPACE**: The DazToMaya Bridge is derived from base classes in the Daz Bridge Library that are within the DZ_BRIDGE_NAMESPACE (see bridge.h). Prior published versions of the official Daz Bridge plugins used custom namespaces to isolate shared class names from each plugin.  While this theoretically works to prevent namespace collisions for platforms that adhere to C++ namespaces, it may not hold true for some implementations of Qt and the Qt meta-object programming model, which is heavily used by Daz Studio and the Bridge plugins.  Notably, C++ namespaces may not be isolating code on the Mac OS implementation of Qt.  With these limitations in mind, I have decided to remove the recommendation to rename the DZ_BRIDGE_NAMESPACE in order to streamline and reduce deployment complexity for potential bridge plugin developers.

In order to link and share C++ classes between this plugin and the Daz Bridge Library, a custom `CPP_PLUGIN_DEFINITION()` macro is used instead of the standard DZ_PLUGIN_DEFINITION macro and usual .DEF file (see bridge.h). NOTE: Use of the DZ_PLUGIN_DEFINITION macro and DEF file use will disable C++ class export in the Visual Studio compiler.


## 7. Directory Structure
Within the Maya directory are hierarchies of subdirectories that correspond to locations on the target machine. Portions of the hierarchy are consistent between the supported platforms and should be replicated exactly while others serve as placeholders for locations that vary depending on the platform of the target machine.

Placeholder directory names used in this repository are:

Name  | Windows  | macOS
------------- | ------------- | -------------
appdir_common  | The directory containing the primary executable (.exe) for the target application.  Sub-hierarchy is common between 32-bit and 64-bit architectures.  | The directory containing the primary application bundle (.app) for the target application.  Sub-hierarchy is common between 32-bit and 64-bit architectures.
MAYA_APP_DIR  | The directory that represents your personal Maya application directory - see [Maya Documentation][MayaDocsURL]  | Same on both platforms.
MAYA_SCRIPT_PATH  | The search path for MEL scripts - see [Maya Documentation][MayaDocsURL]  | Same on both platforms.

The directory structure is as follows:

- `Maya`:                  Files that pertain to the _Maya_ side of the bridge
  - `MAYA_APP_DIR`:  See table above
    - `...`:            Remaining sub-hierarchy
- `DazStudioPlugin`:          Files that pertain to the _Daz Studio_ side of the DazToMaya bridge
  - `Resources` :             Data files to be embedded into the Daz Studio Plugin and support scripts to facilitate this build stage.
- `dzbridge-common`:          Files from the Daz Bridge Library used by DazStudioPlugin
  - `Extras` :                Supplemental scripts and support files to help the conversion process, especially for game-engines and other real-time appllications.
- `Test`:                     Scripts and generated output (reports) used for Quality Assurance Testing.

[OwnerURL]: https://www.daz3d.com
[TwitterURL]: https://twitter.com/Daz3d
[LicenseURL]: http://www.apache.org/licenses/LICENSE-2.0
[ProductURL]: https://www.daz3d.com/daz-to-maya-bridge
[RepositoryURL]: https://github.com/daz3d/DazToMaya/
[DazStudioURL]: https://www.daz3d.com/get_studio
[MayaURL]: https://www.autodesk.com/products/maya
[MayaDocsURL]: https://knowledge.autodesk.com/support/maya/getting-started/caas/CloudHelp/cloudhelp/2019/ENU/Maya-EnvVar/files/GUID-228CCA33-4AFE-4380-8C3D-18D23F7EAC72-htm.html#
