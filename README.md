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
5. Directory Structure


## 1. About the Bridge
This is an updated version of the original DazToMaya Bridge that is being rewritten in C++ using the Daz Bridge Library as a foundation.  This allows it to share the same source code and features with other bridges such as the DazToUnreal and DazToBlender Bridges.

The Daz To maya Bridge consists of two parts: a Daz Studio Plugin which exports assets to Maya and a Maya module to import the assets and help recreate the look of the original Daz Studio asset in Maya.


## 2. Prerequisites
* A compatible version of the [Daz Studio][DazStudioURL] application
  * Minimum: 4.10
* A compatible version of the [Maya][MayaURL] application
  * Minimum: 2016
* Operating System:
  * Windows 7 or newer
  * macOS 10.13 (High Sierra) or newer


## 3. How do I install the Daz To Maya Bridge?
### Daz Studio:
-	You can install the Daz To Cinema 4D Bridge automatically through the Daz Install Manager or Daz Central.  This will automatically add a new menu option under File -> Send To -> Daz To Cinema 4D.
-	Alternatively, you can manually install by downloading the latest build from Github Release Page and following the instructions there to install into Daz Studio.

### Maya:
1.	The Daz Studio Plugin comes embedded with an installer for the Maya Bridge module.  From the Daz To Maya Bridge dialog, there is now section in the Advanced Settings section for Installing the Maya module.
2.	Click the “Install Plugin” button.  You will see a window popup to choose a folder to install the Maya module.  The starting folder should be the default location for maya plugins and modules.
3.	On Windows, the path to install modules should be “\Users\<username>\Documents\maya\modules”.  On Mac, the path should be “/Users/<username>/Library/Preferences/Autodesk/maya/modules”.
4.	For most Maya setups, you should be able to just click “Select Folder”.  You will then see a confirmation dialog stating if the plugin installation was successful.
5.	If Maya is running, you will need to restart for the Daz To Maya Bridge module to load.
6.	In Maya, you should now see a “DazToMaya” tab in the Maya Shelf toolbar.  Click this tab to find the DazToMaya options.
7.	If you have tabs disabled in the Maya Shelf, you may need to click the “cog” icon and select “Shelf Tabs” to find and select the “DazToMaya” tab.
8.	From the DazToMaya tab of the Shelf, you should now see an icon for “DAZ IMPORT”.  You are done installing Daz To Maya Bridge!

 
## 4. How do I use the Maya Bridge?
1.	Open your character in Daz Studio.
2.	Make sure any clothing or hair is parented to the main body.
3.	From the main menu, select File -> Send To -> Daz To Cinema 4D.
4.	A dialog will pop up: choose what type of conversion you wish to do, “Static Mesh” (no skeleton), “Skeletal Mesh” (Character or with joints), or “Animation”.
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
-	For Software which does not fully support Catmull-Clark Subdivision or HD Morphs, we can "Bake" additional subdivision detail levels into the mesh to more closely approximate the detail of the original surface. However, baking each additional subdivision level requires exponentially more CPU time, memory, and storage space.
-	When you enable Bake Subdivision options in the Daz To Cinema4D bridge, the asset is transferred to Cinema4D as a standard mesh with higher resolution vertex counts.


## 5. Directory Structure
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
- `DazStudioPlugin`:          Files that pertain to the _Daz Studio_ side of the DazToBlender bridge
- `dzbridge-common`:          Files from the Daz Bridge Library used by DazStudioPlugin
- `Test`:                     Scripts and generated output (reports) used for Quality Assurance Testing.

[OwnerURL]: https://www.daz3d.com
[TwitterURL]: https://twitter.com/Daz3d
[LicenseURL]: http://www.apache.org/licenses/LICENSE-2.0
[ProductURL]: https://www.daz3d.com/daz-to-maya-bridge
[RepositoryURL]: https://github.com/daz3d/DazToMaya/
[DazStudioURL]: https://www.daz3d.com/get_studio
[MayaURL]: https://www.autodesk.com/products/maya
[MayaDocsURL]: https://knowledge.autodesk.com/support/maya/getting-started/caas/CloudHelp/cloudhelp/2019/ENU/Maya-EnvVar/files/GUID-228CCA33-4AFE-4380-8C3D-18D23F7EAC72-htm.html#
