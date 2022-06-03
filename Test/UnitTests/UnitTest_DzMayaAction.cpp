#ifdef UNITTEST_DZBRIDGE

#include "UnitTest_DzMayaAction.h"
#include "DzMayaAction.h"


UnitTest_DzMayaAction::UnitTest_DzMayaAction()
{
	m_testObject = (QObject*) new DzMayaAction();
}

bool UnitTest_DzMayaAction::runUnitTests()
{
	RUNTEST(_DzBridgeMayaAction);
	RUNTEST(executeAction);
	RUNTEST(createUI);
	RUNTEST(writeConfiguration);
	RUNTEST(setExportOptions);
	RUNTEST(readGuiRootFolder);

	return true;
}

bool UnitTest_DzMayaAction::_DzBridgeMayaAction(UnitTest::TestResult* testResult)
{
	bool bResult = true;
	TRY_METHODCALL(new DzMayaAction());
	return bResult;
}

bool UnitTest_DzMayaAction::executeAction(UnitTest::TestResult* testResult)
{
	bool bResult = true;
	TRY_METHODCALL(qobject_cast<DzMayaAction*>(m_testObject)->executeAction());
	return bResult;
}

bool UnitTest_DzMayaAction::createUI(UnitTest::TestResult* testResult)
{
	bool bResult = true;
	TRY_METHODCALL(qobject_cast<DzMayaAction*>(m_testObject)->createUI());
	return bResult;
}

bool UnitTest_DzMayaAction::writeConfiguration(UnitTest::TestResult* testResult)
{
	bool bResult = true;
	TRY_METHODCALL(qobject_cast<DzMayaAction*>(m_testObject)->writeConfiguration());
	return bResult;
}

bool UnitTest_DzMayaAction::setExportOptions(UnitTest::TestResult* testResult)
{
	bool bResult = true;
	DzFileIOSettings arg;
	TRY_METHODCALL(qobject_cast<DzMayaAction*>(m_testObject)->setExportOptions(arg));
	return bResult;
}

bool UnitTest_DzMayaAction::readGuiRootFolder(UnitTest::TestResult* testResult)
{
	bool bResult = true;
	TRY_METHODCALL(qobject_cast<DzMayaAction*>(m_testObject)->readGuiRootFolder());
	return bResult;
}


#include "moc_UnitTest_DzMayaAction.cpp"

#endif
