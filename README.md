# Daz To Maya
---
* Owner: [Daz 3D][OwnerURL] � [@Daz3d][TwitterURL]
* License: [Apache License, Version 2.0][LicenseURL] - see ``LICENSE`` and ``NOTICE`` for more information.
* Offical Release: [Daz to Maya Bridge][ProductURL]
* Official Project: [github.com/daz3d/DazToMaya][RepositoryURL]

## Prerequisites
---
* A compatible version of the [Daz Studio][DazStudioURL] application
  * Minimum: 4.10
* A compatible version of the [Maya][MayaURL] application
  * Minimum: 2016
* Operating System:
  * Windows 7 or newer
  * macOS 10.13 (High Sierra) or newer

## Directory Structure
---
Files in this repository are organized into two distinct top-level directories - named after the applications that the files within them relate to. Within these directories are hierarchies of subdirectories that correspond to locations on the target machine. Portions of the hierarchy are consistent between the supported platforms and should be replicated exactly while others serve as placeholders for locations that vary depending on the platform of the target machine.

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
  - `MAYA_SCRIPT_PATH`:  See table above
    - `...`:            Remaining sub-hierarchy
- `Daz Studio`:               Files that pertain to the _Daz Studio_ side of the bridge
  - `appdir_common`:          See table above
    - `...`:                  Remaining sub-hierarchy

[OwnerURL]: https://www.daz3d.com
[TwitterURL]: https://twitter.com/Daz3d
[LicenseURL]: http://www.apache.org/licenses/LICENSE-2.0
[ProductURL]: https://www.daz3d.com/daz-to-maya-bridge
[RepositoryURL]: https://github.com/daz3d/DazToMaya/
[DazStudioURL]: https://www.daz3d.com/get_studio
[MayaURL]: https://www.autodesk.com/products/maya
[MayaDocsURL]: https://knowledge.autodesk.com/support/maya/getting-started/caas/CloudHelp/cloudhelp/2019/ENU/Maya-EnvVar/files/GUID-228CCA33-4AFE-4380-8C3D-18D23F7EAC72-htm.html#
