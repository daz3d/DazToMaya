#pragma once
#ifdef UNITTEST_DZBRIDGE

#include <QObject>
#include "UnitTest.h"

class UnitTest_DzMayaDialog : public UnitTest {
	Q_OBJECT
public:
	UnitTest_DzMayaDialog();
	bool runUnitTests();

private:
	bool _DzBridgeMayaDialog(UnitTest::TestResult* testResult);
	bool getIntermediateFolderEdit(UnitTest::TestResult* testResult);
	bool resetToDefaults(UnitTest::TestResult* testResult);
	bool loadSavedSettings(UnitTest::TestResult* testResult);
	bool HandleSelectIntermediateFolderButton(UnitTest::TestResult* testResult);
	bool HandleAssetTypeComboChange(UnitTest::TestResult* testResult);

};


#endif
