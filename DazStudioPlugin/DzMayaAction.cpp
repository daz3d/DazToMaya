#include <QtGui/qcheckbox.h>
#include <QtGui/QMessageBox>
#include <QtNetwork/qudpsocket.h>
#include <QtNetwork/qabstractsocket.h>
#include <QCryptographicHash>
#include <QtCore/qdir.h>

#include <dzapp.h>
#include <dzscene.h>
#include <dzmainwindow.h>
#include <dzshape.h>
#include <dzproperty.h>
#include <dzobject.h>
#include <dzpresentation.h>
#include <dznumericproperty.h>
#include <dzimageproperty.h>
#include <dzcolorproperty.h>
#include <dpcimages.h>

#include "QtCore/qmetaobject.h"
#include "dzmodifier.h"
#include "dzgeometry.h"
#include "dzweightmap.h"
#include "dzfacetshape.h"
#include "dzfacetmesh.h"
#include "dzfacegroup.h"
#include "dzprogress.h"
#include "dzscript.h"
#include "dzexportmgr.h"

#include "DzMayaAction.h"
#include "DzMayaDialog.h"
#include "DzBridgeMorphSelectionDialog.h"
#include "DzBridgeSubdivisionDialog.h"

#ifdef WIN32
#include <shellapi.h>
#endif

#include "dzbridge.h"

QString DzMayaUtils::FindMayaPyExe(QString sMayaExecutablePath)
{
	if (sMayaExecutablePath.isEmpty()) return QString();

	if (QFileInfo(sMayaExecutablePath).exists() == false) return QString();

	if (sMayaExecutablePath.contains("mayapy", Qt::CaseInsensitive)) return sMayaExecutablePath;

#ifdef WIN32
	QString sMayaPyExe = QString(sMayaExecutablePath).replace("maya.exe", "mayapy.exe", Qt::CaseInsensitive);
#elif defined(__APPLE__)
	QString sMayaPyExe = QString(sMayaExecutablePath).replace("/Contents/MacOS/Maya", "/Contents/MacOS/mayapy", Qt::CaseInsensitive);
#endif

	if (QFileInfo(sMayaPyExe).exists() == false) return sMayaExecutablePath;

	return sMayaPyExe;
}

bool DzMayaUtils::GenerateExporterBatchFile(QString batchFilePath, QString sExecutablePath, QString sCommandArgs, QString sCWD)
{
	QString sBatchFileFolder = QFileInfo(batchFilePath).dir().path().replace("\\", "/");
	QDir().mkdir(sBatchFileFolder);

	// 4. Generate manual batch file to launch exporter scripts
	QString sBatchString = QString("\
chcp 65001\n\
cd /d \"%1\"\n\
\"%2\"\
").arg(sCWD).arg(sExecutablePath);
	foreach(QString arg, sCommandArgs.split(";"))
	{
		if (arg.contains(" "))
		{
			sBatchString += QString(" \"%1\"").arg(arg);
		}
		else
		{
			sBatchString += " " + arg;
		}
	}
	// write batch
	QFile batchFileOut(batchFilePath);
	bool bResult = batchFileOut.open(QIODevice::WriteOnly | QIODevice::OpenModeFlag::Truncate);
	if (bResult) {
		batchFileOut.write(sBatchString.toUtf8().constData());
		batchFileOut.close();
	}
	else {
		dzApp->log("ERROR: GenerateExporterBatchFile(): Unable to open batch file for writing: " + batchFilePath);
		return false;
	}

	return true;
}

DzError	DzMayaExporter::write(const QString& filename, const DzFileIOSettings* options)
{
	bool bDefaultToEnvironment = false;
	if (DZ_BRIDGE_NAMESPACE::DzBridgeAction::SelectBestRootNodeForTransfer(false) == DZ_BRIDGE_NAMESPACE::EAssetType::Scene) {
		bDefaultToEnvironment = true;
	}
	QString sMayaOutputPath = QFileInfo(filename).dir().path().replace("\\", "/");

	// process options
	QMap<QString, QString> optionsMap;
	int numKeys = options->getNumValues();
	for (int i = 0; i < numKeys; i++) {
		auto key = options->getKey(i);
		auto val = options->getValue(i);
		optionsMap.insert(key, val);
		dzApp->log(QString("DEBUG: DzMayaExporter: Options[%1]=[%2]").arg(key).arg(val));
	}

	DzProgress exportProgress(tr("Maya Exporter starting..."), 100, false, true);
	exportProgress.setInfo(QString("Exporting to:\n    \"%1\"\n").arg(filename));

	exportProgress.setInfo("Generating intermediate file");
	exportProgress.step(25);

	DzMayaAction* pMayaAction = new DzMayaAction();
	pMayaAction->m_pSelectedNode = dzScene->getPrimarySelection();
	pMayaAction->m_sOutputMayaFilepath = QString(filename).replace("\\", "/");
	pMayaAction->setNonInteractiveMode(DZ_BRIDGE_NAMESPACE::eNonInteractiveMode::DzExporterMode);
	pMayaAction->createUI();
	DzMayaDialog* pDialog = qobject_cast<DzMayaDialog*>( pMayaAction->getBridgeDialog() );
	if (pDialog == NULL) 
	{
		exportProgress.cancel();
		dzApp->log("Maya Exporter: CRITICAL ERROR: Unable to initialize DzMayaDialog. Aborting operation.");
		return DZ_OPERATION_FAILED_ERROR;
	}
	if (bDefaultToEnvironment) {
		int nEnvIndex = pDialog->getAssetTypeCombo()->findText("Environment");
		pDialog->getAssetTypeCombo()->setCurrentIndex(nEnvIndex);
	}
	pDialog->requireMayaExecutableWidget(true);
	pMayaAction->executeAction();
	pDialog->requireMayaExecutableWidget(false);

	if (pDialog->result() == QDialog::Rejected) {
		exportProgress.cancel();
		return DZ_USER_CANCELLED_OPERATION;
	}

	DzError nExecuteActionResult = pMayaAction->getExecutActionResult();
	if (nExecuteActionResult != DZ_NO_ERROR) {
		exportProgress.cancel();
		return nExecuteActionResult;
	}

	//////////////////////////////////////////////////////////////////////////////////////////
	QString sIntermediatePath = QFileInfo(pMayaAction->m_sDestinationFBX).dir().path().replace("\\", "/");
	QString sIntermediateScriptsPath = sIntermediatePath + "/Scripts";
	QDir().mkdir(sIntermediateScriptsPath);

	QStringList aScriptFilelist = (QStringList() <<
		"create_maya_file.py" 
		);
	// copy 
	foreach(auto sScriptFilename, aScriptFilelist)
	{
		bool replace = true;
		QString sEmbeddedFolderPath = ":/DazBridgeMaya";
		QString sEmbeddedFilepath = sEmbeddedFolderPath + "/" + sScriptFilename;
		QFile srcFile(sEmbeddedFilepath);
		QString tempFilepath = sIntermediateScriptsPath + "/" + sScriptFilename;
		DZ_BRIDGE_NAMESPACE::DzBridgeAction::copyFile(&srcFile, &tempFilepath, replace);
		srcFile.close();
	}

	exportProgress.setInfo("Generating Maya File");
	exportProgress.step(25);

	//////////////////////////////////////////////////////////////////////////////////////////

	//QString sMayaLogPath = sIntermediatePath + "/" + "create_maya_file.log";
	//QString sScriptPath = sIntermediateScriptsPath + "/" + "create_maya_file.py";
	//QString sCommandArgs = QString("%1;%2").arg(sScriptPath).arg(pMayaAction->m_sDestinationFBX);
	QString sMayaLogPath = QString(".") + "/" + "create_maya_file.log";
	QString sScriptPath = QString("./Scripts") + "/" + "create_maya_file.py";
	QString sCommandArgs = QString("%1;%2").arg(sScriptPath).arg(pMayaAction->m_sDestinationFBX);
#if WIN32
	QString batchFilePath = sIntermediatePath + "/" + "create_maya_file.bat";
#else
	QString batchFilePath = sIntermediatePath + "/" + "create_maya_file.sh";
#endif
	QString sMayaPyExecutable = DzMayaUtils::FindMayaPyExe(pMayaAction->m_sMayaExecutablePath);
	if (sMayaPyExecutable.isEmpty() || sMayaPyExecutable == "") 
	{
		QString sNoMayaPyExe = tr("Daz To Maya: CRITICAL ERROR: Unable to find a valid Maya Python executable. Aborting operation.");
		dzApp->log(sNoMayaPyExe);
		QMessageBox::critical(0, tr("No Maya Py Executable Found"),
			sNoMayaPyExe, QMessageBox::Abort);
		exportProgress.cancel();
		return DZ_OPERATION_FAILED_ERROR;
	}
	DzMayaUtils::GenerateExporterBatchFile(batchFilePath, sMayaPyExecutable, sCommandArgs, sIntermediatePath);

	bool result = pMayaAction->executeMayaScripts(sMayaPyExecutable, sCommandArgs, 120);

	exportProgress.step(25);
	//////////////////////////////////////////////////////////////////////////////////////////

	if (result) 
	{
		exportProgress.update(100);
		QMessageBox::information(0, tr("Maya Exporter"), 
			tr("Export from Daz Studio complete."), QMessageBox::Ok);

#ifdef WIN32
//	ShellExecuteA(NULL, "open", sMayaOutputPath.toLocal8Bit().data(), NULL, NULL, SW_SHOWDEFAULT);
	std::wstring wcsMayaOutputPath(reinterpret_cast<const wchar_t*>(sMayaOutputPath.utf16()));
	ShellExecuteW(NULL, L"open", wcsMayaOutputPath.c_str(), NULL, NULL, SW_SHOWDEFAULT);
#elif defined(__APPLE__)
	QStringList args;
	args << "-e";
	args << "tell application \"Finder\"";
	args << "-e";
	args << "activate";
	args << "-e";
	if (QFileInfo(filename).exists()) {
		args << "select POSIX file \"" + filename + "\"";
	}
	else {
		args << "select POSIX file \"" + sMayaOutputPath + "/." + "\"";
	}
	args << "-e";
	args << "end tell";
	QProcess::startDetached("osascript", args);
#endif
	} 
	else 
	{
		QString sErrorString;
		sErrorString += QString("An error occured during the export process (ExitCode=%1).\n").arg(pMayaAction->m_nMayaExitCode);
		sErrorString += QString("Please check log files at : %1\n").arg(pMayaAction->m_sDestinationPath);
		QMessageBox::critical(0, "Maya Exporter", tr(sErrorString.toLocal8Bit()), QMessageBox::Ok);
#ifdef WIN32
//		ShellExecuteA(NULL, "open", pMayaAction->m_sDestinationPath.toLocal8Bit().data(), NULL, NULL, SW_SHOWDEFAULT);
		std::wstring wcsDestinationPath(reinterpret_cast<const wchar_t*>(pMayaAction->m_sDestinationPath.utf16()));
		ShellExecuteW(NULL, L"open", wcsDestinationPath.c_str(), NULL, NULL, SW_SHOWDEFAULT);
#elif defined(__APPLE__)
		QStringList args;
		args << "-e";
		args << "tell application \"Finder\"";
		args << "-e";
		args << "activate";
		args << "-e";
		args << "select POSIX file \"" + batchFilePath + "\"";
		args << "-e";
		args << "end tell";
		QProcess::startDetached("osascript", args);
#endif

		exportProgress.cancel();
		return DZ_OPERATION_FAILED_ERROR;
	}

	exportProgress.finish();
	return DZ_NO_ERROR;
};


DzMayaAction::DzMayaAction() :
	DzBridgeAction(tr("Send to &Maya..."), tr("Send the selected node to Maya."))
{
	this->setObjectName("DzBridge_DazToMaya_Action");

	m_nNonInteractiveMode = 0;
	m_sAssetType = QString("SkeletalMesh");
	//Setup Icon
	QString iconName = "Daz to Maya";
	QPixmap basePixmap = QPixmap::fromImage(getEmbeddedImage(iconName.toLatin1()));
	QIcon icon;
	icon.addPixmap(basePixmap, QIcon::Normal, QIcon::Off);
	QAction::setIcon(icon);

}

bool DzMayaAction::createUI()
{
	// Check if the main window has been created yet.
	// If it hasn't, alert the user and exit early.
	DzMainWindow* mw = dzApp->getInterface();
	if (!mw)
	{
		if (m_nNonInteractiveMode == 0) QMessageBox::warning(0, tr("Error"),
			tr("The main window has not been created yet."), QMessageBox::Ok);

		return false;
	}

	 // Create the dialog
	if (!m_bridgeDialog)
	{
		m_bridgeDialog = new DzMayaDialog(mw);
	}
	else
	{
		DzMayaDialog* mayaDialog = qobject_cast<DzMayaDialog*>(m_bridgeDialog);
		if (mayaDialog)
		{
			mayaDialog->resetToDefaults();
			mayaDialog->loadSavedSettings();
		}
	}

	// m_subdivisionDialog creation REQUIRES valid Character or Prop selected
	if (dzScene->getNumSelectedNodes() != 1)
	{
		if (m_nNonInteractiveMode == 0) QMessageBox::warning(0, tr("Error"),
			tr("Please select one Character or Prop to send."), QMessageBox::Ok);

		return false;
	}

	if (!m_subdivisionDialog) m_subdivisionDialog = DZ_BRIDGE_NAMESPACE::DzBridgeSubdivisionDialog::Get(m_bridgeDialog);
	if (!m_morphSelectionDialog) m_morphSelectionDialog = DZ_BRIDGE_NAMESPACE::DzBridgeMorphSelectionDialog::Get(m_bridgeDialog);

	return true;
}

void DzMayaAction::executeAction()
{
	m_nExecuteActionResult = DZ_OPERATION_FAILED_ERROR;
	m_eSelectedNodeAssetType = DZ_BRIDGE_NAMESPACE::EAssetType::None;

	// CreateUI() disabled for debugging -- 2022-Feb-25
	/*
		 // Create and show the dialog. If the user cancels, exit early,
		 // otherwise continue on and do the thing that required modal
		 // input from the user.
		 if (createUI() == false)
			 return;
	*/

	// Check if the main window has been created yet.
	// If it hasn't, alert the user and exit early.
	DzMainWindow* mw = dzApp->getInterface();
	if (!mw)
	{
		if (m_nNonInteractiveMode == 0)
		{
			QMessageBox::warning(0, tr("Error"),
				tr("The main window has not been created yet."), QMessageBox::Ok);
		}
		return;
	}

	if (m_nNonInteractiveMode != DZ_BRIDGE_NAMESPACE::eNonInteractiveMode::DzExporterMode) {
		m_eSelectedNodeAssetType = SelectBestRootNodeForTransfer(true);
		m_pSelectedNode = dzScene->getPrimarySelection();
	}

	// Create the dialog
	if (m_bridgeDialog == nullptr)
	{
		m_bridgeDialog = new DzMayaDialog(mw);
	}
	else
	{
		if (m_nNonInteractiveMode == 0)
		{
			m_bridgeDialog->resetToDefaults();
			m_bridgeDialog->loadSavedSettings();
		}
	}

	// Prepare member variables when not using GUI
	if (isInteractiveMode() == false)
	{
//		if (m_sRootFolder != "") m_bridgeDialog->getIntermediateFolderEdit()->setText(m_sRootFolder);

		if (m_aMorphListOverride.isEmpty() == false)
		{
			m_bEnableMorphs = true;
			m_sMorphSelectionRule = m_aMorphListOverride.join("\n1\n");
			m_sMorphSelectionRule += "\n1\n.CTRLVS\n2\nAnything\n0";
			if (m_morphSelectionDialog == nullptr)
			{
				m_morphSelectionDialog = DZ_BRIDGE_NAMESPACE::DzBridgeMorphSelectionDialog::Get(m_bridgeDialog);
			}
			m_MorphNamesToExport.clear();
			foreach(QString morphName, m_aMorphListOverride)
			{
				QString label = m_morphSelectionDialog->GetMorphLabelFromName(morphName);
				m_MorphNamesToExport.append(morphName);
			}
		}
		else
		{
			m_bEnableMorphs = false;
			m_sMorphSelectionRule = "";
			m_MorphNamesToExport.clear();
		}

	}

	m_bridgeDialog->setEAssetType(m_eSelectedNodeAssetType);

	// If the Accept button was pressed, start the export
	int dlgResult = -1;
	if ( isInteractiveMode() )
	{
		dlgResult = m_bridgeDialog->exec();
	}
	if (isInteractiveMode() == false || dlgResult == QDialog::Accepted)
	{
		// Read GUI values
		if (readGui(m_bridgeDialog) == false)
		{
			m_nExecuteActionResult = DZ_OPERATION_FAILED_ERROR;
			return;
		}

		// DB 2021-10-11: Progress Bar
		DzProgress* exportProgress = new DzProgress("Sending to Maya...", 10, false, true);

		DzError result = doPromptableObjectBaking();
		if (result != DZ_NO_ERROR) {
			exportProgress->finish();
			exportProgress->cancel();
			m_nExecuteActionResult = result;
			return;
		}
		exportProgress->step();

		//Create Daz3D folder if it doesn't exist
		QDir dir;
		dir.mkpath(m_sRootFolder);
		exportProgress->step();

		if (m_sAssetType == "Environment") {

			QDir().mkdir(m_sDestinationPath);
			m_pSelectedNode = dzScene->getPrimarySelection();

			auto objectList = dzScene->getNodeList();
			foreach(auto el, objectList) {
				DzNode* pNode = qobject_cast<DzNode*>(el);
				preProcessScene(pNode);
			}
			DzExportMgr* ExportManager = dzApp->getExportMgr();
			DzExporter* Exporter = ExportManager->findExporterByClassName("DzFbxExporter");
			DzFileIOSettings ExportOptions;
			ExportOptions.setBoolValue("IncludeSelectedOnly", false);
			ExportOptions.setBoolValue("IncludeVisibleOnly", true);
			ExportOptions.setBoolValue("IncludeFigures", true);
			ExportOptions.setBoolValue("IncludeProps", true);
			ExportOptions.setBoolValue("IncludeLights", false);
			ExportOptions.setBoolValue("IncludeCameras", false);
			ExportOptions.setBoolValue("IncludeAnimations", true);
			ExportOptions.setIntValue("RunSilent", !m_bShowFbxOptions);
			setExportOptions(ExportOptions);
			// NOTE: be careful to use m_sExportFbx and NOT m_sExportFilename since FBX and DTU base name may differ
			QString sEnvironmentFbx = m_sDestinationPath + m_sExportFbx + ".fbx";
			DzError result = Exporter->writeFile(sEnvironmentFbx, &ExportOptions);
			if (result != DZ_NO_ERROR) {
				undoPreProcessScene();
				m_nExecuteActionResult = result;
				exportProgress->finish();
				exportProgress->cancel();
				return;
			}
			exportProgress->step();

			writeConfiguration();
			exportProgress->step();

			undoPreProcessScene();
			exportProgress->step();

		} 
		else 
		{
			DzNode* pParentNode = NULL;
			if (m_pSelectedNode->isRootNode() == false) {
				dzApp->log("INFO: Selected Node for Export is not a Root Node, unparenting now....");
				pParentNode = m_pSelectedNode->getNodeParent();
				pParentNode->removeNodeChild(m_pSelectedNode, true);
				dzApp->log("INFO: Parent stored: " + pParentNode->getLabel() + ", New Root Node: " + m_pSelectedNode->getLabel());
			}
			exportProgress->step();
			exportHD(exportProgress);
			exportProgress->step();
			if (pParentNode) {
				dzApp->log("INFO: Restoring Parent relationship: " + pParentNode->getLabel() + ", child node: " + m_pSelectedNode->getLabel());
				pParentNode->addNodeChild(m_pSelectedNode, true);
			}
		}

		exportProgress->update(10);
		// DB 2021-09-02: messagebox "Export Complete"
		if (m_nNonInteractiveMode == 0)
		{
			QMessageBox::information(0, "Daz To Maya Bridge",
				tr("Export phase from Daz Studio complete. Please switch to Maya to begin Import phase."), QMessageBox::Ok);
		}

		// DB 2021-10-11: Progress Bar
		exportProgress->finish();

	}

	m_nExecuteActionResult = DZ_NO_ERROR;
}


void DzMayaAction::writeConfiguration()
{
	DzProgress* pDtuProgress = new DzProgress("Writing DTU file", 10, false, true);

	QString DTUfilename = m_sDestinationPath + m_sAssetName + ".dtu";
	QFile DTUfile(DTUfilename);
	DTUfile.open(QIODevice::WriteOnly);
	DzJsonWriter writer(&DTUfile);
	writer.startObject(true);

	writeDTUHeader(writer);
	pDtuProgress->step();

	// Plugin-specific items
//	writer.addMember("Use Blender Tools", m_bUseBlenderTools);
	writer.addMember("Output Maya Filepath", m_sOutputMayaFilepath);
//	writer.addMember("Texture Atlas Mode", m_sTextureAtlasMode);
//	writer.addMember("Texture Atlas Size", m_nTextureAtlasSize);
//	writer.addMember("Export Rig Mode", m_sExportRigMode);
//	writer.addMember("Enable GPU Baking", m_bEnableGpuBaking);
//	writer.addMember("Embed Textures", m_bEmbedTexturesInOutputFile);
	writer.addMember("Generate Final Fbx", m_bGenerateFinalFbx);
	writer.addMember("Shader Target", m_sShaderTarget);
	pDtuProgress->step();

//	if (m_sAssetType.toLower().contains("mesh") || m_sAssetType == "Animation")
	if (true)
	{
		QTextStream *pCVSStream = nullptr;
		if (m_bExportMaterialPropertiesCSV)
		{
			QString filename = m_sDestinationPath + m_sAssetName + "_Maps.csv";
			QFile file(filename);
			file.open(QIODevice::WriteOnly);
			pCVSStream = new QTextStream(&file);
			*pCVSStream << "Version, Object, Material, Type, Color, Opacity, File" << endl;
		}
		pDtuProgress->update(6);
		if (m_sAssetType == "Environment") {
			writeSceneMaterials(writer, pCVSStream);
			pDtuProgress->step();
		}
		else {
			writeAllMaterials(m_pSelectedNode, writer, pCVSStream);
			pDtuProgress->step();
		}

		writeAllMorphs(writer);

		writeMorphLinks(writer);
		writeMorphNames(writer);
		pDtuProgress->step();

		DzBoneList aBoneList = getAllBones(m_pSelectedNode);

		writeSkeletonData(m_pSelectedNode, writer);
		writeHeadTailData(m_pSelectedNode, writer);
		writeJointOrientation(aBoneList, writer);
		writeLimitData(aBoneList, writer);
		writePoseData(m_pSelectedNode, writer, true);
		pDtuProgress->step();

		writeAllSubdivisions(writer);
		pDtuProgress->step();

		writeAllDforceInfo(m_pSelectedNode, writer);
		pDtuProgress->step();
	}

	//if (m_sAssetType == "Pose")
	//{
	//   writeAllPoses(writer);
	//}

	//if (m_sAssetType == "Environment")
	//{
	//	writeEnvironment(writer);
	//}

	writer.finishObject();
	DTUfile.close();

	pDtuProgress->finish();

}

// Setup custom FBX export options
void DzMayaAction::setExportOptions(DzFileIOSettings& ExportOptions)
{
//	ExportOptions.setBoolValue("IncludeFaceGroupsAsPolygonSets", false);
//	ExportOptions.setBoolValue("IncludeFaceGroupsAsPolygonGroups", false);

	ExportOptions.setBoolValue("doFps", true);
	ExportOptions.setBoolValue("doLocks", false);
	ExportOptions.setBoolValue("doLimits", false);
	ExportOptions.setBoolValue("doBaseFigurePoseOnly", false);
	ExportOptions.setBoolValue("doHelperScriptScripts", false);
	ExportOptions.setBoolValue("doMentalRayMaterials", false);

	//ExportOptions.setBoolValue("doEmbed", false);
	//ExportOptions.setBoolValue("doDiffuseOpacity", false);
	//ExportOptions.setBoolValue("doCopyTextures", false);

	// Unable to use this option, since generated files are referenced only in FBX and unknown to DTU
	ExportOptions.setBoolValue("MergeDiffuseOpacity", false);
	// disable these options since we use Blender to generate a new FBX with embedded files
	ExportOptions.setBoolValue("EmbedTextures", false);
	ExportOptions.setBoolValue("CollectTextures", false);

	// Custom Properties
	ExportOptions.setBoolValue("IncludeNodeNamesLabels", true);
	ExportOptions.setBoolValue("IncludeNodePresentation", true);
	ExportOptions.setBoolValue("IncludeNodeSelectionMap", true);
	ExportOptions.setBoolValue("IncludeSceneIDs", true);
	ExportOptions.setBoolValue("IncludeFollowTargets", true);

}

QString DzMayaAction::readGuiRootFolder()
{
	QString rootFolder = QDesktopServices::storageLocation(QDesktopServices::DocumentsLocation) + QDir::separator() + "DazToMaya";
#if __LEGACY_PATHS__
		rootFolder = QDesktopServices::storageLocation(QDesktopServices::DocumentsLocation) + "/DAZ 3D/Bridges/Daz To Maya/Exports/FIG/FIG0";
		rootFolder = rootFolder.replace("\\","/");
#else
	if (m_bridgeDialog)
	{
		QLineEdit* intermediateFolderEdit = nullptr;
		DzMayaDialog* mayaDialog = qobject_cast<DzMayaDialog*>(m_bridgeDialog);

		if (mayaDialog)
			intermediateFolderEdit = mayaDialog->getAssetsFolderEdit();

		if (intermediateFolderEdit)
			rootFolder = intermediateFolderEdit->text().replace("\\", "/") + "/Daz3D";
	}
#endif

	return rootFolder;
}

bool DzMayaAction::executeMayaScripts(QString sFilePath, QString sCommandlineArguments, float fTimeoutInSeconds)
{
	// fork or spawn child process
	QString sWorkingPath = m_sDestinationPath;
	QStringList args = sCommandlineArguments.split(";");

//	float fTimeoutInSeconds = 2 * 60;
	float fMilliSecondsPerTick = 200;
	int numTotalTicks = fTimeoutInSeconds * 1000 / fMilliSecondsPerTick;
	DzProgress* progress = new DzProgress("Running Maya Script", numTotalTicks, false, true);
	progress->enable(true);
	QProcess* pToolProcess = new QProcess(this);
	pToolProcess->setWorkingDirectory(sWorkingPath);
	pToolProcess->start(sFilePath, args);
	int currentTick = 0;
	int timeoutTicks = numTotalTicks;
	bool bUserInitiatedTermination = false;
	while (pToolProcess->waitForFinished(fMilliSecondsPerTick) == false) {
		// if timeout reached, then terminate process
		if (currentTick++ > timeoutTicks) {
			if (!bUserInitiatedTermination)
			{
				QString sTimeoutText = tr("\
The current Maya operation is taking a long time.\n\
Do you want to Ignore this time-out and wait a little longer, or \n\
Do you want to Abort the operation now?");
				int result = QMessageBox::critical(0,
					tr("Daz To Maya: Maya Timout Error"),
					sTimeoutText,
					QMessageBox::Ignore,
					QMessageBox::Abort);
				if (result == QMessageBox::Ignore) {
					int snoozeTime = 60 * 1000 / fMilliSecondsPerTick;
					timeoutTicks += snoozeTime;
				}
				else {
					bUserInitiatedTermination = true;
				}
			}
			else
			{
				if (currentTick - timeoutTicks < 5) {
					pToolProcess->terminate();
				}
				else {
					pToolProcess->kill();
				}
			}
		}
		if (pToolProcess->state() == QProcess::Running) {
			progress->step();
		}
		else {
			break;
		}
	}
	progress->setCurrentInfo("Maya Script Completed.");
	progress->finish();
	delete progress;
	m_nMayaExitCode = pToolProcess->exitCode();
//#ifdef __APPLE__
//	if (m_nMayaExitCode != 0 && m_nMayaExitCode != 120)
#//else
	if (m_nMayaExitCode != 0)
//#endif
	{
		//if (m_nMayaExitCode == m_nPythonExceptionExitCode) {
		//	dzApp->log(QString("Daz To Maya: ERROR: Python error:.... %1").arg(m_nMayaExitCode));
		//}
		//else {
		//	dzApp->log(QString("Daz To Maya: ERROR: exit code = %1").arg(m_nMayaExitCode));
		//}
		dzApp->log(QString("Daz To Maya: ERROR: exit code = %1").arg(m_nMayaExitCode));
		return false;
	}

	return true;
}

bool DzMayaAction::readGui(DZ_BRIDGE_NAMESPACE::DzBridgeDialog* BridgeDialog)
{
	bool bResult = DzBridgeAction::readGui(BridgeDialog);
	if (!bResult)
	{
		return false;
	}

#if __LEGACY_PATHS__
	m_sRootFolder = QDesktopServices::storageLocation(QDesktopServices::DocumentsLocation) + "/DAZ 3D/Bridges/Daz To Maya/Exports/FIG";
	m_sRootFolder = m_sRootFolder.replace("\\", "/");
	m_sExportSubfolder = "FIG0";
	m_sExportFbx = "B_FIG";
	m_sAssetName = "FIG";
	m_sDestinationPath = m_sRootFolder + "/" + m_sExportSubfolder + "/";
	m_sDestinationFBX = m_sDestinationPath + m_sExportFbx + ".fbx";
#endif

	// Read Custom GUI values
	DzMayaDialog* pMayaDialog = qobject_cast<DzMayaDialog*>(m_bridgeDialog);
	if (pMayaDialog) {

		if (m_sMayaExecutablePath == "" || isInteractiveMode() ) m_sMayaExecutablePath = pMayaDialog->getMayaExecutablePath().replace("\\", "/");
		m_bGenerateFinalFbx = pMayaDialog->getGenerateFbxFile();
		m_sShaderTarget = pMayaDialog->getShaderConversion();
	}
	else {
		// Issue error, fail gracefully
		dzApp->log("Daz To Maya: ERROR: Maya Dialog was not initialized.  Cancelling operation...");
	}

	return true;
}


#include "moc_DzMayaAction.cpp"
