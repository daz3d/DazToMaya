#ifdef UNITTEST_DZBRIDGE

#include "UnitTest_DzMayaDialog.h"
#include "DzMayaDialog.h"


UnitTest_DzMayaDialog::UnitTest_DzMayaDialog()
{
	m_testObject = (QObject*) new DzMayaDialog();
}

bool UnitTest_DzMayaDialog::runUnitTests()
{
	RUNTEST(_DzBridgeMayaDialog);
	RUNTEST(getIntermediateFolderEdit);
	RUNTEST(resetToDefaults);
	RUNTEST(loadSavedSettings);
	RUNTEST(HandleSelectIntermediateFolderButton);
	RUNTEST(HandleAssetTypeComboChange);

	return true;
}

bool UnitTest_DzMayaDialog::_DzBridgeMayaDialog(UnitTest::TestResult* testResult)
{
	bool bResult = true;
	TRY_METHODCALL(new DzMayaDialog());
	return bResult;
}

bool UnitTest_DzMayaDialog::getIntermediateFolderEdit(UnitTest::TestResult* testResult)
{
	bool bResult = true;
	TRY_METHODCALL(qobject_cast<DzMayaDialog*>(m_testObject)->getIntermediateFolderEdit());
	return bResult;
}

bool UnitTest_DzMayaDialog::resetToDefaults(UnitTest::TestResult* testResult)
{
	bool bResult = true;
	TRY_METHODCALL(qobject_cast<DzMayaDialog*>(m_testObject)->resetToDefaults());
	return bResult;
}

bool UnitTest_DzMayaDialog::loadSavedSettings(UnitTest::TestResult* testResult)
{
	bool bResult = true;
	TRY_METHODCALL(qobject_cast<DzMayaDialog*>(m_testObject)->loadSavedSettings());
	return bResult;
}

bool UnitTest_DzMayaDialog::HandleSelectIntermediateFolderButton(UnitTest::TestResult* testResult)
{
	bool bResult = true;
	TRY_METHODCALL(qobject_cast<DzMayaDialog*>(m_testObject)->HandleSelectIntermediateFolderButton());
	return bResult;
}

bool UnitTest_DzMayaDialog::HandleAssetTypeComboChange(UnitTest::TestResult* testResult)
{
	bool bResult = true;
	TRY_METHODCALL(qobject_cast<DzMayaDialog*>(m_testObject)->HandleAssetTypeComboChange(0));
	return bResult;
}


#include "moc_UnitTest_DzMayaDialog.cpp"
#endif
