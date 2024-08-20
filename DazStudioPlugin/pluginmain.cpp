#include "dzplugin.h"
#include "dzapp.h"

#include "version.h"
#include "DzMayaAction.h"
#include "DzMayaDialog.h"

#include "dzbridge.h"

CPP_PLUGIN_DEFINITION("Daz To Maya Bridge");

DZ_PLUGIN_AUTHOR("Daz 3D, Inc");

DZ_PLUGIN_VERSION(PLUGIN_MAJOR, PLUGIN_MINOR, PLUGIN_REV, PLUGIN_BUILD);

#ifdef _DEBUG
DZ_PLUGIN_DESCRIPTION(QString(
	"<b>Pre-Release Maya Bridge %1.%2.%3.%4 </b><br>\
<a href = \"https://github.com/daz3d/DazToMaya\">Github</a><br><br>"
).arg(PLUGIN_MAJOR).arg(PLUGIN_MINOR).arg(PLUGIN_REV).arg(PLUGIN_BUILD));
#else
DZ_PLUGIN_DESCRIPTION(QString(
"This plugin provides the ability to send assets to Maya. \
Documentation and source code are available on <a href = \"https://github.com/daz3d/DazToMaya\">Github</a>.<br>"
));
#endif

DZ_PLUGIN_CLASS_GUID(DzMayaAction, 93744e8a-989b-4a27-a168-416f09ac74a3);
NEW_PLUGIN_CUSTOM_CLASS_GUID(DzMayaDialog, af9f004a-0f1b-4f0f-a6f8-927a2b4d3a4b);

#ifdef UNITTEST_DZBRIDGE

#include "UnitTest_DzMayaAction.h"
#include "UnitTest_DzMayaDialog.h"

DZ_PLUGIN_CLASS_GUID(UnitTest_DzMayaAction, 536d9096-a3b2-41c9-bfa8-8ddeec674ec9);
DZ_PLUGIN_CLASS_GUID(UnitTest_DzMayaDialog, 39242fe6-17e3-4018-9ced-4879385fb423);

#endif

DZ_PLUGIN_CLASS_GUID(DzMayaAsciiExporter, f823002f-db9d-408f-9a28-694a536a726f);
DZ_PLUGIN_CLASS_GUID(DzMayaBinaryExporter, f823002f-db9d-408f-9a28-694a536a7270);
