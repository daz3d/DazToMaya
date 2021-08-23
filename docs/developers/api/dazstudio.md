## Classes

<dl>
<dt><a href="#DzBridgeAutoWeight">DzBridgeAutoWeight</a></dt>
<dd></dd>
<dt><a href="#DzBridgeExporter">DzBridgeExporter</a></dt>
<dd></dd>
<dt><a href="#DzBridgeHelpers">DzBridgeHelpers</a></dt>
<dd></dd>
<dt><a href="#DzBridgeScene">DzBridgeScene</a></dt>
<dd></dd>
</dl>

<a name="DzBridgeAutoWeight"></a>

## DzBridgeAutoWeight
**Kind**: global class  

* [DzBridgeAutoWeight](#DzBridgeAutoWeight)
    * [new DzBridgeAutoWeight(sRootPath)](#new_DzBridgeAutoWeight_new)
    * [.getActiveMorphs(oNode)](#DzBridgeAutoWeight+getActiveMorphs) ⇒ <code>DzNode</code>
    * [.zeroOutMorphs(oActiveMorphs)](#DzBridgeAutoWeight+zeroOutMorphs)
    * [.returnMorphValues(oActiveMorphs)](#DzBridgeAutoWeight+returnMorphValues)
    * [.transferWeights(oSource, oTarget)](#DzBridgeAutoWeight+transferWeights) ⇒ <code>Boolean</code>
    * [.findingPropsToWeight(oSource, oParent)](#DzBridgeAutoWeight+findingPropsToWeight)
    * [.weightObjects(oBaseNode)](#DzBridgeAutoWeight+weightObjects)

<a name="new_DzBridgeAutoWeight_new"></a>

### new DzBridgeAutoWeight(sRootPath)
Used to weight non-skinned geometry on Nodes with a skeleton


| Param | Type |
| --- | --- |
| sRootPath | <code>String</code> | 

<a name="DzBridgeAutoWeight+getActiveMorphs"></a>

### dzBridgeAutoWeight.getActiveMorphs(oNode) ⇒ <code>DzNode</code>
Object : Helper function to deselect everything in the scene.

**Kind**: instance method of [<code>DzBridgeAutoWeight</code>](#DzBridgeAutoWeight)  
**Returns**: <code>DzNode</code> - Contains all the active morphs on the node given with its property and value  

| Param | Type | Description |
| --- | --- | --- |
| oNode | <code>DzNode</code> | a given figure that has morphs |

<a name="DzBridgeAutoWeight+zeroOutMorphs"></a>

### dzBridgeAutoWeight.zeroOutMorphs(oActiveMorphs)
Void: Applys the default values of the morphs that are active

**Kind**: instance method of [<code>DzBridgeAutoWeight</code>](#DzBridgeAutoWeight)  

| Param | Type | Description |
| --- | --- | --- |
| oActiveMorphs | <code>Object</code> | All the active morphs found on the specific figure. |

<a name="DzBridgeAutoWeight+returnMorphValues"></a>

### dzBridgeAutoWeight.returnMorphValues(oActiveMorphs)
Void: Applys the user input values of the morphs that are active

**Kind**: instance method of [<code>DzBridgeAutoWeight</code>](#DzBridgeAutoWeight)  

| Param | Type | Description |
| --- | --- | --- |
| oActiveMorphs | <code>Object</code> | All the active morphs found on the specific figure. |

<a name="DzBridgeAutoWeight+transferWeights"></a>

### dzBridgeAutoWeight.transferWeights(oSource, oTarget) ⇒ <code>Boolean</code>
Bool : Runs Transfer Utility and return if it was a success or not.

**Kind**: instance method of [<code>DzBridgeAutoWeight</code>](#DzBridgeAutoWeight)  
**Returns**: <code>Boolean</code> - Returns if the DzTransferUtility was a success or not  

| Param | Type | Description |
| --- | --- | --- |
| oSource | <code>DzNode</code> | Source Figure used to get the weights |
| oTarget | <code>DzNode</code> | Target prop which is unweighted and needs auto-weights |

<a name="DzBridgeAutoWeight+findingPropsToWeight"></a>

### dzBridgeAutoWeight.findingPropsToWeight(oSource, oParent)
Void: Cycles through the Children of the Parents and does loop for Auto-Weights

**Kind**: instance method of [<code>DzBridgeAutoWeight</code>](#DzBridgeAutoWeight)  

| Param | Type | Description |
| --- | --- | --- |
| oSource | <code>DzNode</code> | Source Figure used to get the weights |
| oParent | <code>DzNode</code> | Parent Figure used for find the Children |

<a name="DzBridgeAutoWeight+weightObjects"></a>

### dzBridgeAutoWeight.weightObjects(oBaseNode)
Void: Used to run the Auto-Weight logic, This is Destructive and break user's scene

**Kind**: instance method of [<code>DzBridgeAutoWeight</code>](#DzBridgeAutoWeight)  

| Param | Type | Description |
| --- | --- | --- |
| oBaseNode | <code>DzNode</code> | The Top Node of the hierachy |

<a name="DzBridgeExporter"></a>

## DzBridgeExporter
**Kind**: global class  

* [DzBridgeExporter](#DzBridgeExporter)
    * [new DzBridgeExporter(sDazBridgeName, sScriptPath, oBridgeScene)](#new_DzBridgeExporter_new)
    * [.sDazBridgeName](#DzBridgeExporter+sDazBridgeName) : <code>String</code>
    * [.sRootPath](#DzBridgeExporter+sRootPath) : <code>String</code>
    * [.sCustomPath](#DzBridgeExporter+sCustomPath) : <code>String</code>
    * [.sPresetPath](#DzBridgeExporter+sPresetPath) : <code>String</code>
    * [.sConfigPath](#DzBridgeExporter+sConfigPath) : <code>String</code>
    * [.sMorphPath](#DzBridgeExporter+sMorphPath) : <code>String</code>
    * [.sFbxPath](#DzBridgeExporter+sFbxPath) : <code>String</code>
    * [.init(sDazBridgeName, sScriptPath, oBridgeScene)](#DzBridgeExporter+init)
    * [.prepareForExport(oBridgeScene)](#DzBridgeExporter+prepareForExport)

<a name="new_DzBridgeExporter_new"></a>

### new DzBridgeExporter(sDazBridgeName, sScriptPath, oBridgeScene)
Used to weight non-skinned geometry on Nodes with a skeleton


| Param | Type |
| --- | --- |
| sDazBridgeName | <code>String</code> | 
| sScriptPath | <code>String</code> | 
| oBridgeScene | [<code>DzBridgeScene</code>](#DzBridgeScene) | 

<a name="DzBridgeExporter+sDazBridgeName"></a>

### dzBridgeExporter.sDazBridgeName : <code>String</code>
Name of Bridge

**Kind**: instance property of [<code>DzBridgeExporter</code>](#DzBridgeExporter)  
<a name="DzBridgeExporter+sRootPath"></a>

### dzBridgeExporter.sRootPath : <code>String</code>
Path to the the Export Directory

**Kind**: instance property of [<code>DzBridgeExporter</code>](#DzBridgeExporter)  
<a name="DzBridgeExporter+sCustomPath"></a>

### dzBridgeExporter.sCustomPath : <code>String</code>
Path to the Custom Export Directory

**Kind**: instance property of [<code>DzBridgeExporter</code>](#DzBridgeExporter)  
<a name="DzBridgeExporter+sPresetPath"></a>

### dzBridgeExporter.sPresetPath : <code>String</code>
Path to the Preset Folder

**Kind**: instance property of [<code>DzBridgeExporter</code>](#DzBridgeExporter)  
<a name="DzBridgeExporter+sConfigPath"></a>

### dzBridgeExporter.sConfigPath : <code>String</code>
Path to the Configs Folder

**Kind**: instance property of [<code>DzBridgeExporter</code>](#DzBridgeExporter)  
<a name="DzBridgeExporter+sMorphPath"></a>

### dzBridgeExporter.sMorphPath : <code>String</code>
LastUsed.csv from Morph Dialog

**Kind**: instance property of [<code>DzBridgeExporter</code>](#DzBridgeExporter)  
<a name="DzBridgeExporter+sFbxPath"></a>

### dzBridgeExporter.sFbxPath : <code>String</code>
Path to FBX File

**Kind**: instance property of [<code>DzBridgeExporter</code>](#DzBridgeExporter)  
<a name="DzBridgeExporter+init"></a>

### dzBridgeExporter.init(sDazBridgeName, sScriptPath, oBridgeScene)
Void : Initilizes Variables

**Kind**: instance method of [<code>DzBridgeExporter</code>](#DzBridgeExporter)  

| Param | Type |
| --- | --- |
| sDazBridgeName | <code>String</code> | 
| sScriptPath | <code>String</code> | 
| oBridgeScene | [<code>DzBridgeScene</code>](#DzBridgeScene) | 

<a name="DzBridgeExporter+prepareForExport"></a>

### dzBridgeExporter.prepareForExport(oBridgeScene)
Void : Delete previous export and recreate directories if neededISSUE : Currently the Both Enum is handled incorrectly new logic is neededTODO: Refactor logic

**Kind**: instance method of [<code>DzBridgeExporter</code>](#DzBridgeExporter)  

| Param | Type |
| --- | --- |
| oBridgeScene | [<code>DzBridgeScene</code>](#DzBridgeScene) | 

<a name="DzBridgeHelpers"></a>

## DzBridgeHelpers
**Kind**: global class  

* [DzBridgeHelpers](#DzBridgeHelpers)
    * [new DzBridgeHelpers(sDazBridgeName, sScriptPath, sRootPath, sFbxPath)](#new_DzBridgeHelpers_new)
    * [.sDazBridgeName](#DzBridgeHelpers+sDazBridgeName) : <code>String</code>
    * [.sRootPath](#DzBridgeHelpers+sRootPath) : <code>String</code>
    * [.sScriptPath](#DzBridgeHelpers+sScriptPath) : <code>String</code>
    * [.sFbxPath](#DzBridgeHelpers+sFbxPath) : <code>String</code>
    * [.sFig](#DzBridgeHelpers+sFig) : <code>String</code>
    * [.sEnv](#DzBridgeHelpers+sEnv) : <code>String</code>
    * [.sMorphRules](#DzBridgeHelpers+sMorphRules) : <code>String</code>
    * [.bIncludeAnim](#DzBridgeHelpers+bIncludeAnim) : <code>Boolean</code>
    * [.oMeshTypes](#DzBridgeHelpers+oMeshTypes)
    * [.oExportTypes](#DzBridgeHelpers+oExportTypes)
    * [.init(sDazBridgeName, sScriptPath, sRootPath, sFbxPath)](#DzBridgeHelpers+init)
    * [.executeSubScript(sScript, aArgs)](#DzBridgeHelpers+executeSubScript) ⇒ <code>Object</code>
    * [.getGroupProperties(oGroup, bTraverse, bRecurse)](#DzBridgeHelpers+getGroupProperties) ⇒ <code>Array.&lt;DzProperty&gt;</code>
    * [.getElementProperties(oGroup, bTraverse, bRecurse)](#DzBridgeHelpers+getElementProperties) ⇒ <code>Array.&lt;DzProperty&gt;</code>
    * [.exportFBX(oNode, sName, nIdx, sSuffix, bAscii)](#DzBridgeHelpers+exportFBX)
    * [.exportOBJ(oNode, sName, nIdx, bSelected)](#DzBridgeHelpers+exportOBJ)
    * [.importOBJ(sName, nIdx)](#DzBridgeHelpers+importOBJ)
    * [.getPropertyName(oProperty)](#DzBridgeHelpers+getPropertyName) ⇒ <code>String</code>
    * [.addTempDirectory()](#DzBridgeHelpers+addTempDirectory)
    * [.cleanUpTempFiles(sPath)](#DzBridgeHelpers+cleanUpTempFiles)
    * [.deSelectAll()](#DzBridgeHelpers+deSelectAll)
    * [.changeLock(oProperty, bLock)](#DzBridgeHelpers+changeLock)
    * [.setLock(oBaseNode, bLock, bIsFigure)](#DzBridgeHelpers+setLock)
    * [.getObjectType(oNode)](#DzBridgeHelpers+getObjectType) ⇒ <code>String</code>
    * [.getParentingData(oParentNode, oBaseNode)](#DzBridgeHelpers+getParentingData) ⇒ <code>Array.&lt;String&gt;</code>
    * [.getMeshType(oNode)](#DzBridgeHelpers+getMeshType) ⇒ <code>Number</code>

<a name="new_DzBridgeHelpers_new"></a>

### new DzBridgeHelpers(sDazBridgeName, sScriptPath, sRootPath, sFbxPath)

| Param | Type |
| --- | --- |
| sDazBridgeName | <code>String</code> | 
| sScriptPath | <code>String</code> | 
| sRootPath | <code>String</code> | 
| sFbxPath | <code>String</code> | 

<a name="DzBridgeHelpers+sDazBridgeName"></a>

### dzBridgeHelpers.sDazBridgeName : <code>String</code>
Name of Bridge

**Kind**: instance property of [<code>DzBridgeHelpers</code>](#DzBridgeHelpers)  
<a name="DzBridgeHelpers+sRootPath"></a>

### dzBridgeHelpers.sRootPath : <code>String</code>
Path to the Export Directory

**Kind**: instance property of [<code>DzBridgeHelpers</code>](#DzBridgeHelpers)  
<a name="DzBridgeHelpers+sScriptPath"></a>

### dzBridgeHelpers.sScriptPath : <code>String</code>
Path to where the executed script is located.

**Kind**: instance property of [<code>DzBridgeHelpers</code>](#DzBridgeHelpers)  
<a name="DzBridgeHelpers+sFbxPath"></a>

### dzBridgeHelpers.sFbxPath : <code>String</code>
Path to FBX File

**Kind**: instance property of [<code>DzBridgeHelpers</code>](#DzBridgeHelpers)  
<a name="DzBridgeHelpers+sFig"></a>

### dzBridgeHelpers.sFig : <code>String</code>
Keyword for Figure Exports

**Kind**: instance property of [<code>DzBridgeHelpers</code>](#DzBridgeHelpers)  
<a name="DzBridgeHelpers+sEnv"></a>

### dzBridgeHelpers.sEnv : <code>String</code>
Keyword for Env/Prop Exports

**Kind**: instance property of [<code>DzBridgeHelpers</code>](#DzBridgeHelpers)  
<a name="DzBridgeHelpers+sMorphRules"></a>

### dzBridgeHelpers.sMorphRules : <code>String</code>
Used for the FBX Exporter to export user's Morphs

**Kind**: instance property of [<code>DzBridgeHelpers</code>](#DzBridgeHelpers)  
<a name="DzBridgeHelpers+bIncludeAnim"></a>

### dzBridgeHelpers.bIncludeAnim : <code>Boolean</code>
Enable or Disable Animation Export

**Kind**: instance property of [<code>DzBridgeHelpers</code>](#DzBridgeHelpers)  
<a name="DzBridgeHelpers+oMeshTypes"></a>

### dzBridgeHelpers.oMeshTypes
Types of Meshes

**Kind**: instance property of [<code>DzBridgeHelpers</code>](#DzBridgeHelpers)  
**Properties**

| Name | Type |
| --- | --- |
| Figure | <code>Number</code> | 
| Mesh | <code>Number</code> | 
| Other | <code>Number</code> | 
| Bone | <code>Number</code> | 
| NoFacets | <code>Number</code> | 
| Empty | <code>Number</code> | 

<a name="DzBridgeHelpers+oExportTypes"></a>

### dzBridgeHelpers.oExportTypes
Types of Exports

**Kind**: instance property of [<code>DzBridgeHelpers</code>](#DzBridgeHelpers)  
**Properties**

| Name | Type |
| --- | --- |
| Both | <code>Number</code> | 
| Figure | <code>Number</code> | 
| EnvProp | <code>Number</code> | 
| None | <code>Number</code> | 

<a name="DzBridgeHelpers+init"></a>

### dzBridgeHelpers.init(sDazBridgeName, sScriptPath, sRootPath, sFbxPath)
Void : Initilizes Variables

**Kind**: instance method of [<code>DzBridgeHelpers</code>](#DzBridgeHelpers)  

| Param | Type |
| --- | --- |
| sDazBridgeName | <code>String</code> | 
| sScriptPath | <code>String</code> | 
| sRootPath | <code>String</code> | 
| sFbxPath | <code>String</code> | 

<a name="DzBridgeHelpers+executeSubScript"></a>

### dzBridgeHelpers.executeSubScript(sScript, aArgs) ⇒ <code>Object</code>
Object : Executes a Script with a given script name

**Kind**: instance method of [<code>DzBridgeHelpers</code>](#DzBridgeHelpers)  

| Param | Type |
| --- | --- |
| sScript | <code>String</code> | 
| aArgs | <code>Array</code> | 

<a name="DzBridgeHelpers+getGroupProperties"></a>

### dzBridgeHelpers.getGroupProperties(oGroup, bTraverse, bRecurse) ⇒ <code>Array.&lt;DzProperty&gt;</code>
Array<DzProperty> : A function for getting a list of the properties in a group

**Kind**: instance method of [<code>DzBridgeHelpers</code>](#DzBridgeHelpers)  

| Param | Type |
| --- | --- |
| oGroup | <code>DzNode</code> | 
| bTraverse | <code>Boolean</code> | 
| bRecurse | <code>Boolean</code> | 

<a name="DzBridgeHelpers+getElementProperties"></a>

### dzBridgeHelpers.getElementProperties(oGroup, bTraverse, bRecurse) ⇒ <code>Array.&lt;DzProperty&gt;</code>
Array<DzProperty> : A function for getting the list properties for an element

**Kind**: instance method of [<code>DzBridgeHelpers</code>](#DzBridgeHelpers)  

| Param | Type |
| --- | --- |
| oGroup | <code>DzNode</code> | 
| bTraverse | <code>Boolean</code> | 
| bRecurse | <code>Boolean</code> | 

<a name="DzBridgeHelpers+exportFBX"></a>

### dzBridgeHelpers.exportFBX(oNode, sName, nIdx, sSuffix, bAscii)
Void : Silently exports FBX

**Kind**: instance method of [<code>DzBridgeHelpers</code>](#DzBridgeHelpers)  

| Param | Type |
| --- | --- |
| oNode | <code>DzNode</code> | 
| sName | <code>String</code> | 
| nIdx | <code>Number</code> | 
| sSuffix | <code>String</code> | 
| bAscii | <code>Boolean</code> | 

<a name="DzBridgeHelpers+exportOBJ"></a>

### dzBridgeHelpers.exportOBJ(oNode, sName, nIdx, bSelected)
Void : Silently exports OBJ

**Kind**: instance method of [<code>DzBridgeHelpers</code>](#DzBridgeHelpers)  

| Param | Type |
| --- | --- |
| oNode | <code>DzNode</code> | 
| sName | <code>String</code> | 
| nIdx | <code>Number</code> | 
| bSelected | <code>Boolean</code> | 

<a name="DzBridgeHelpers+importOBJ"></a>

### dzBridgeHelpers.importOBJ(sName, nIdx)
Void : Silently imports OBJ

**Kind**: instance method of [<code>DzBridgeHelpers</code>](#DzBridgeHelpers)  

| Param | Type |
| --- | --- |
| sName | <code>String</code> | 
| nIdx | <code>Number</code> | 

<a name="DzBridgeHelpers+getPropertyName"></a>

### dzBridgeHelpers.getPropertyName(oProperty) ⇒ <code>String</code>
String : Get the name of the Property

**Kind**: instance method of [<code>DzBridgeHelpers</code>](#DzBridgeHelpers)  
**Returns**: <code>String</code> - - Returns the name of the property  

| Param | Type |
| --- | --- |
| oProperty | <code>DzProperty</code> | 

<a name="DzBridgeHelpers+addTempDirectory"></a>

### dzBridgeHelpers.addTempDirectory()
Void : Helper function to create the temp directory if it doesn't exist

**Kind**: instance method of [<code>DzBridgeHelpers</code>](#DzBridgeHelpers)  
<a name="DzBridgeHelpers+cleanUpTempFiles"></a>

### dzBridgeHelpers.cleanUpTempFiles(sPath)
Void : Helper function to remove temporary files form a path

**Kind**: instance method of [<code>DzBridgeHelpers</code>](#DzBridgeHelpers)  

| Param | Type | Description |
| --- | --- | --- |
| sPath | <code>string</code> | Path of the temp folder used to export/import the obj |

<a name="DzBridgeHelpers+deSelectAll"></a>

### dzBridgeHelpers.deSelectAll()
Void : Helper function to deselect everything in the scene.

**Kind**: instance method of [<code>DzBridgeHelpers</code>](#DzBridgeHelpers)  
<a name="DzBridgeHelpers+changeLock"></a>

### dzBridgeHelpers.changeLock(oProperty, bLock)
Void : Change lock based on given Boolean

**Kind**: instance method of [<code>DzBridgeHelpers</code>](#DzBridgeHelpers)  

| Param | Type |
| --- | --- |
| oProperty | <code>DzProperty</code> | 
| bLock | <code>Boolean</code> | 

<a name="DzBridgeHelpers+setLock"></a>

### dzBridgeHelpers.setLock(oBaseNode, bLock, bIsFigure)
Void : Set lock for a node and all it's childen

**Kind**: instance method of [<code>DzBridgeHelpers</code>](#DzBridgeHelpers)  

| Param | Type |
| --- | --- |
| oBaseNode | <code>DzNode</code> | 
| bLock | <code>Boolean</code> | 
| bIsFigure | <code>Boolean</code> | 

<a name="DzBridgeHelpers+getObjectType"></a>

### dzBridgeHelpers.getObjectType(oNode) ⇒ <code>String</code>
String : Find out what type of Object we have

**Kind**: instance method of [<code>DzBridgeHelpers</code>](#DzBridgeHelpers)  
**Returns**: <code>String</code> - Object Type  

| Param | Type |
| --- | --- |
| oNode | <code>DzNode</code> | 

<a name="DzBridgeHelpers+getParentingData"></a>

### dzBridgeHelpers.getParentingData(oParentNode, oBaseNode) ⇒ <code>Array.&lt;String&gt;</code>
Array<String> : ...

**Kind**: instance method of [<code>DzBridgeHelpers</code>](#DzBridgeHelpers)  
**Returns**: <code>Array.&lt;String&gt;</code> - Parented nodes names  

| Param | Type |
| --- | --- |
| oParentNode | <code>DzNode</code> | 
| oBaseNode | <code>DzNode</code> | 

<a name="DzBridgeHelpers+getMeshType"></a>

### dzBridgeHelpers.getMeshType(oNode) ⇒ <code>Number</code>
Number  : ...

**Kind**: instance method of [<code>DzBridgeHelpers</code>](#DzBridgeHelpers)  
**Returns**: <code>Number</code> - Mesh Type  

| Param | Type |
| --- | --- |
| oNode | <code>DzNode</code> | 

<a name="DzBridgeScene"></a>

## DzBridgeScene
**Kind**: global class  

* [DzBridgeScene](#DzBridgeScene)
    * [new DzBridgeScene()](#new_DzBridgeScene_new)
    * [.checkChildType(oChildNode)](#DzBridgeScene+checkChildType) ⇒ <code>String</code>
    * [.overrideExportType(nExportType)](#DzBridgeScene+overrideExportType)

<a name="new_DzBridgeScene_new"></a>

### new DzBridgeScene()
Used to Create the type of Exports that exist in the scene

<a name="DzBridgeScene+checkChildType"></a>

### dzBridgeScene.checkChildType(oChildNode) ⇒ <code>String</code>
Used to Create the type of Exports that exist in the scene

**Kind**: instance method of [<code>DzBridgeScene</code>](#DzBridgeScene)  
**Returns**: <code>String</code> - Daz Content Type of given Node.  

| Param | Type | Description |
| --- | --- | --- |
| oChildNode | <code>DzNode</code> | the Child node of the RootNodes Found |

<a name="DzBridgeScene+overrideExportType"></a>

### dzBridgeScene.overrideExportType(nExportType)
Based on user's input we will remove the type of export they do not want.

**Kind**: instance method of [<code>DzBridgeScene</code>](#DzBridgeScene)  

| Param | Type | Description |
| --- | --- | --- |
| nExportType | <code>Number</code> | The type recieve from DzBridgeDialog.promptExportType |

