#include <QtGui/QLayout>
#include <QtGui/QLabel>
#include <QtGui/QGroupBox>
#include <QtGui/QPushButton>
#include <QtGui/QMessageBox>
#include <QtGui/QToolTip>
#include <QtGui/QWhatsThis>
#include <QtGui/qlineedit.h>
#include <QtGui/qboxlayout.h>
#include <QtGui/qfiledialog.h>
#include <QtCore/qsettings.h>
#include <QtGui/qformlayout.h>
#include <QtGui/qcombobox.h>
#include <QtGui/qdesktopservices.h>
#include <QtGui/qcheckbox.h>
#include <QtGui/qlistwidget.h>
#include <QtGui/qgroupbox.h>

#include "dzapp.h"
#include "dzscene.h"
#include "dzstyle.h"
#include "dzmainwindow.h"
#include "dzactionmgr.h"
#include "dzaction.h"
#include "dzskeleton.h"
#include "qstandarditemmodel.h"

#include "DzMayaDialog.h"
#include "DzBridgeMorphSelectionDialog.h"
#include "DzBridgeSubdivisionDialog.h"

#include "version.h"

/*****************************
Local definitions
*****************************/
#define DAZ_BRIDGE_PLUGIN_NAME "Daz To Maya"

#include "dzbridge.h"

QValidator::State DzFileValidator::validate(QString& input, int& pos) const {
	QFileInfo fi(input);
	if (fi.exists() == false) {
		dzApp->log("DzBridge: DzFileValidator: DEBUG: file does not exist: " + input);
		return QValidator::Intermediate;
	}

	return QValidator::Acceptable;
};


DzMayaDialog::DzMayaDialog(QWidget* parent) :
	 DzBridgeDialog(parent, DAZ_BRIDGE_PLUGIN_NAME)
{
	 intermediateFolderEdit = nullptr;
	 intermediateFolderButton = nullptr;

	 settings = new QSettings("Daz 3D", "DazToMaya");

	 // Declarations
	 int margin = style()->pixelMetric(DZ_PM_GeneralMargin);
	 int wgtHeight = style()->pixelMetric(DZ_PM_ButtonHeight);
	 int btnMinWidth = style()->pixelMetric(DZ_PM_ButtonMinWidth);

	 // Set the dialog title
	 int revision = PLUGIN_REV % 1000;
#ifdef _DEBUG
	 setWindowTitle(tr("Daz To Maya Bridge %1 v%2.%3.%4").arg(PLUGIN_MAJOR).arg(PLUGIN_MINOR).arg(revision).arg(PLUGIN_BUILD));
#else
	 setWindowTitle(tr("Daz To Maya Bridge %1 v%2.%3").arg(PLUGIN_MAJOR).arg(PLUGIN_MINOR).arg(revision));
#endif

	 // Welcome String for Setup/Welcome Mode
	 QString sDazAppDir = dzApp->getHomePath().replace("\\","/");
	 QString sPdfPath = sDazAppDir + "/docs/Plugins" + "/Daz to Maya/Daz to Maya.pdf";
	 QString sSetupModeString = tr("\
<div style=\"background-color:#282f41;\" align=center>\
<img src=\":/DazBridgeMaya/banner.jpg\" width=\"370\" height=\"95\" align=\"center\" hspace=\"0\" vspace=\"0\">\
<table width=100% cellpadding=8 cellspacing=2 style=\"vertical-align:middle; font-size:x-large; font-weight:bold; background-color:#FFAA00;foreground-color:#FFFFFF\" align=center>\
  <tr>\
    <td width=33% style=\"text-align:center; background-color:#282f41;\"><div align=center><a href=\"https://www.daz3d.com/maya-bridge#faq\">FAQ</a></div></td>\
    <td width=33% style=\"text-align:center; background-color:#282f41;\"><div align=center><a href=\"https://youtu.be/gck7raZ2N84\">Installation Video</a></td>\
    <td width=33% style=\"text-align:center; background-color:#282f41;\"><div align=center><a href=\"https://youtu.be/QMFFliYu_kw\">Tutorial Video</a></td>\
  </tr>\
  <tr>\
    <td width=33% style=\"text-align:center; background-color:#282f41;\"><div align=center><a href=\"file:///") + sPdfPath + tr("\">PDF</a></td>\
    <td width=33% style=\"text-align:center; background-color:#282f41;\"><div align=center><a href=\"https://www.daz3d.com/forums/categories/maya-discussion\">Forums</a></td>\
    <td width=33% style=\"text-align:center; background-color:#282f41;\"><div align=center><a href=\"https://github.com/daz3d/DazToMaya/issues\">Report Bug</a></td>\
  </tr>\
</table>\
</div>\
");
	 m_WelcomeLabel->setText(sSetupModeString);

	 // Disable Unsupported AssetType ComboBox Options
	 QStandardItemModel* model = qobject_cast<QStandardItemModel*>(assetTypeCombo->model());
	 QStandardItem* item = nullptr;
	 item = model->findItems("Environment").first();
	 if (item) item->setFlags(item->flags() & ~Qt::ItemIsEnabled);
	 item = model->findItems("Pose").first();
	 if (item) item->setFlags(item->flags() & ~Qt::ItemIsEnabled);

	 // Connect new asset type handler
	 connect(assetTypeCombo, SIGNAL(activated(int)), this, SLOT(HandleAssetTypeComboChange(int)));

	 m_wMayaExecutablePathEdit = new QLineEdit(this);
	 m_wMayaExecutablePathEdit->setValidator(&m_dzValidatorFileExists);
	 m_wMayaExecutablePathButton = new DzBridgeBrowseButton(this);
	 m_wMayaExecutablePathLayout = new QHBoxLayout();
	 m_wMayaExecutablePathLayout->setSpacing(0);
	 m_wMayaExecutablePathLayout->addWidget(m_wMayaExecutablePathEdit);
	 m_wMayaExecutablePathLayout->addWidget(m_wMayaExecutablePathButton);
	 connect(m_wMayaExecutablePathButton, SIGNAL(released()), this, SLOT(HandleSelectMayaExecutablePathButton()));
	 connect(m_wMayaExecutablePathEdit, SIGNAL(textChanged(const QString&)), this, SLOT(HandleTextChanged(const QString&)));

	 m_wMayaExecutableRowLabel = new QLabel(tr("Maya Executable"));
	 advancedLayout->insertRow(0, m_wMayaExecutableRowLabel, m_wMayaExecutablePathLayout);
	 m_aRowLabels.append(m_wMayaExecutableRowLabel);

	 QString sMayaExeHelp = tr("Select a Maya executable to run scripts");
	 QString sMayaExeHelp2 = tr("Select a Maya executable to run scripts. \
Maya scripts are used for generating maya files when File->Export is used. \
Recommend using the lowest version of Maya that is compatible with your projects.");
	 m_wMayaExecutablePathEdit->setToolTip(sMayaExeHelp);
	 m_wMayaExecutablePathButton->setToolTip(sMayaExeHelp);
	 m_wMayaExecutableRowLabel->setToolTip(sMayaExeHelp);
	 m_wMayaExecutablePathEdit->setWhatsThis(sMayaExeHelp2);
	 m_wMayaExecutablePathButton->setWhatsThis(sMayaExeHelp2);
	 m_wMayaExecutableRowLabel->setWhatsThis(sMayaExeHelp2);

	 // Intermediate Folder
	 QHBoxLayout* intermediateFolderLayout = new QHBoxLayout();
	 intermediateFolderEdit = new QLineEdit(this);
	 intermediateFolderButton = new QPushButton("...", this);
	 intermediateFolderLayout->addWidget(intermediateFolderEdit);
	 intermediateFolderLayout->addWidget(intermediateFolderButton);
	 connect(intermediateFolderButton, SIGNAL(released()), this, SLOT(HandleSelectIntermediateFolderButton()));

	 // Advanced Options
#if __LEGACY_PATHS__
	 intermediateFolderEdit->setVisible(false);
	 intermediateFolderButton->setVisible(false);
#endif
	 if (advancedLayout)
	 {
#if __LEGACY_PATHS__
		 // reposition the Open Intermediate Folder button so it aligns with the center section
		 advancedLayout->removeWidget(m_OpenIntermediateFolderButton);
		 advancedLayout->addRow("", m_OpenIntermediateFolderButton);
#else
		 advancedLayout->addRow("Intermediate Folder", intermediateFolderLayout);
#endif
	 }
	 QString sMayaVersionString = tr("DazToMaya Bridge %1 v%2.%3.%4").arg(PLUGIN_MAJOR).arg(PLUGIN_MINOR).arg(revision).arg(PLUGIN_BUILD);
	 setBridgeVersionStringAndLabel(sMayaVersionString);

	 // Configure Target Plugin Installer
	 renameTargetPluginInstaller("Maya Plugin Installer");
	 m_TargetSoftwareVersionCombo->clear();
	 m_TargetSoftwareVersionCombo->setVisible(false);
	 //m_TargetSoftwareVersionCombo->addItem("Select Maya Version");
	 //m_TargetSoftwareVersionCombo->addItem("Maya 2020");
	 //m_TargetSoftwareVersionCombo->addItem("Maya 2022");
	 //m_TargetSoftwareVersionCombo->addItem("Maya 2023");
	 showTargetPluginInstaller(true);

	 // Make the dialog fit its contents, with a minimum width, and lock it down
	 resize(QSize(500, 0).expandedTo(minimumSizeHint()));
	 setFixedWidth(width());
	 setFixedHeight(height());

	 update();

	 // Help
	 QString sAssetNameHelp = tr("This is the name the asset will use in Maya.");
	 QString sAssetTypeHelp = tr("\
<b>Skeletal Mesh</b> for something with moving parts, like a character.<br>\
<b>Static Mesh</b> for things like props.<br>\
<b>Animation</b> for a character animation.");
	 QString sIntermediateFolderHelp = tr("Daz To Maya will collect the assets in a subfolder under this folder.  Maya will import them from here.");
	 QString sTargetPluginInstallerHelp = tr("You can install the Maya Plugin by clicking Install.");

	 assetNameEdit->setToolTip(sAssetNameHelp);
	 m_wAssetNameRowLabelWidget->setToolTip(sAssetNameHelp);
	 assetTypeCombo->setToolTip(sAssetTypeHelp);
	 m_wAssetTypeRowLabelWidget->setToolTip(sAssetTypeHelp);
	 intermediateFolderEdit->setToolTip(sIntermediateFolderHelp);
	 intermediateFolderButton->setToolTip(sIntermediateFolderHelp);
	 m_OpenIntermediateFolderButton->setToolTip(sIntermediateFolderHelp);
	 m_wTargetPluginInstaller->setToolTip(sTargetPluginInstallerHelp);

	 assetNameEdit->setWhatsThis(sAssetNameHelp);
	 m_wAssetNameRowLabelWidget->setWhatsThis(sAssetNameHelp);
	 assetTypeCombo->setWhatsThis(sAssetTypeHelp);
	 m_wAssetTypeRowLabelWidget->setWhatsThis(sAssetTypeHelp);
	 intermediateFolderEdit->setWhatsThis(sIntermediateFolderHelp);
	 intermediateFolderButton->setWhatsThis(sIntermediateFolderHelp);
	 m_OpenIntermediateFolderButton->setWhatsThis(sIntermediateFolderHelp);
	 m_wTargetPluginInstaller->setWhatsThis(sTargetPluginInstallerHelp);

	 // Set Defaults
	 resetToDefaults();

	 // Load Settings
	 loadSavedSettings();

	 // GUI Refresh
	 m_WelcomeLabel->hide();
	 setWindowTitle(tr("Maya Export Options"));
	 wHelpMenuButton->show();

	 disableAcceptUntilAllRequirementsValid();

	 fixRowLabelStyle();
	 fixRowLabelWidths();

}

bool DzMayaDialog::loadSavedSettings()
{
	DzBridgeDialog::loadSavedSettings();

	if (!settings->value("IntermediatePath").isNull())
	{
		QString directoryName = settings->value("IntermediatePath").toString();
		intermediateFolderEdit->setText(directoryName);
	}
	else
	{
		QString DefaultPath = QDesktopServices::storageLocation(QDesktopServices::DocumentsLocation) + QDir::separator() + "DazToMaya";
		intermediateFolderEdit->setText(DefaultPath);
	}
	if (!settings->value("MayaExecutablePath").isNull())
	{
		m_wMayaExecutablePathEdit->setText(settings->value("MayaExecutablePath").toString());
	}

	return true;
}

void DzMayaDialog::saveSettings()
{
	if (settings == nullptr || m_bDontSaveSettings) return;

	DzBridgeDialog::saveSettings();

	// Intermediate Path
	QString sIntermdiateFolderpath = intermediateFolderEdit->text();
	if (sIntermdiateFolderpath == "") {
		// reset to default
		QString DefaultPath = QDesktopServices::storageLocation(QDesktopServices::DocumentsLocation) + QDir::separator() + "DazToMaya";
		sIntermdiateFolderpath = DefaultPath;
	}
	settings->setValue("IntermediatePath", sIntermdiateFolderpath);

	// Maya Executable Path
	settings->setValue("MayaExecutablePath", m_wMayaExecutablePathEdit->text());
}

void DzMayaDialog::resetToDefaults()
{
	m_bDontSaveSettings = true;
	DzBridgeDialog::resetToDefaults();

	QString DefaultPath = QDesktopServices::storageLocation(QDesktopServices::DocumentsLocation) + QDir::separator() + "DazToMaya";
	intermediateFolderEdit->setText(DefaultPath);

	DzNode* Selection = dzScene->getPrimarySelection();
	if (dzScene->getFilename().length() > 0)
	{
		QFileInfo fileInfo = QFileInfo(dzScene->getFilename());
		assetNameEdit->setText(fileInfo.baseName().remove(QRegExp("[^A-Za-z0-9_]")));
	}
	else if (dzScene->getPrimarySelection())
	{
		assetNameEdit->setText(Selection->getLabel().remove(QRegExp("[^A-Za-z0-9_]")));
	}

	if (qobject_cast<DzSkeleton*>(Selection))
	{
		assetTypeCombo->setCurrentIndex(0);
	}
	else
	{
		assetTypeCombo->setCurrentIndex(1);
	}
	m_bDontSaveSettings = false;
}

void DzMayaDialog::HandleSelectIntermediateFolderButton()
{
	 // DB (2021-05-15): prepopulate with existing folder string
	 QString directoryName = "/home";
	 if (settings != nullptr && settings->value("IntermediatePath").isNull() != true)
	 {
		 directoryName = settings->value("IntermediatePath").toString();
	 }
	 directoryName = QFileDialog::getExistingDirectory(this, tr("Choose Directory"),
		  directoryName,
		  QFileDialog::ShowDirsOnly
		  | QFileDialog::DontResolveSymlinks);

	 if (directoryName != NULL)
	 {
		 intermediateFolderEdit->setText(directoryName);
		 if (settings != nullptr)
		 {
			 settings->setValue("IntermediatePath", directoryName);
		 }
	 }
}

void DzMayaDialog::HandleAssetTypeComboChange(int state)
{
	QString assetNameString = assetNameEdit->text();

	// enable/disable Morphs and Subdivision only if Skeletal selected
	if (assetTypeCombo->currentText() != "Skeletal Mesh")
	{
		morphsEnabledCheckBox->setChecked(false);
		subdivisionEnabledCheckBox->setChecked(false);
	}

	// if "Animation", change assetname
	if (assetTypeCombo->currentText() == "Animation")
	{
		// check assetname is in @anim[0000] format
		if (!assetNameString.contains("@") || assetNameString.contains(QRegExp("@anim[0-9]*")))
		{
			// extract true assetName and recompose animString
			assetNameString = assetNameString.left(assetNameString.indexOf("@"));
			// get importfolder using corrected assetNameString
			QString importFolderPath = settings->value("AssetsPath").toString() + QDir::separator() + "Daz3D" + QDir::separator() + assetNameString + QDir::separator();

			// create anim filepath
			uint animCounter = 0;
			QString animString = assetNameString + QString("@anim%1").arg(animCounter, 4, 10, QChar('0'));
			QString filePath = importFolderPath + animString + ".fbx";

			// if anim file exists, then increment anim filename counter
			while (QFileInfo(filePath).exists())
			{
				if (++animCounter > 9999)
				{
					break;
				}
				animString = assetNameString + QString("@anim%1").arg(animCounter, 4, 10, QChar('0'));
				filePath = importFolderPath + animString + ".fbx";
			}
			assetNameEdit->setText(animString);
		}

	}
	else
	{
		// remove @anim if present
		if (assetNameString.contains("@")) {
			assetNameString = assetNameString.left(assetNameString.indexOf("@"));
		}
		assetNameEdit->setText(assetNameString);
	}

}

#include <QProcessEnvironment>

void DzMayaDialog::HandleTargetPluginInstallerButton()
{
	// Get Software Versio
	DzBridgeDialog::m_sEmbeddedFilesPath = ":/DazBridgeMaya";
	QString sBinariesFile = "/mayamodule.zip";
	QProcessEnvironment env(QProcessEnvironment::systemEnvironment());
	QString sMayaAppDir = env.value("MAYA_APP_DIR");
#ifdef __APPLE__
	if (sMayaAppDir == "") {
		sMayaAppDir = QDir().homePath() + "/Library/Preferences/Autodesk/maya";
	}
#else
	if (sMayaAppDir == "") {
		sMayaAppDir = QDesktopServices::storageLocation(QDesktopServices::DocumentsLocation) + QDir::separator() + "maya";
	}
#endif
	QString sDestinationPath = sMayaAppDir;
	if (QDir(sDestinationPath).exists() == false)
	{
		// Warning, not a valid MayaAppDir
		QMessageBox msgBox;
		msgBox.setTextFormat(Qt::RichText);
		msgBox.setWindowTitle("MAYA_APP_DIR not found");
		msgBox.setText(
		tr("The bridge could not find the path to your personal Maya application directory (MAYA_APP_DIR).<br><br> \
On Windows, this is usually at <b>\"/Users/&lt;username&gt;/Documents/maya/\"</b> and on Mac, it is at \
<b>\"~&lt;username&gt;/Library/Preferences/Autodesk/maya/\"</b>.  Please navigate to where \
this folder is located for your installation.<br><br> \
For more information on the MAYA_APP_DIR setting, please refer to:<br> \
<a href=\"https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2015/ENU/Maya/files/Environment-Variables-File-path-variables-htm.html\">\
File path variables (Maya Support and learning)</a>"));
		msgBox.setStandardButtons(QMessageBox::Ok);
		msgBox.exec();
		sDestinationPath = QDesktopServices::storageLocation(QDesktopServices::DocumentsLocation);
	}
	QString softwareVersion = m_TargetSoftwareVersionCombo->currentText();

	//if (softwareVersion.contains("..."))
	//{
	//	sDestinationPath += "...";
	//}
	//else
	//{
	//	// Warning, not a valid plugins folder path
	//	QMessageBox::information(0, "DazToMaya Bridge",
	//		tr("Please select a Maya version."));
	//	return;
	//}

	// Get Destination Folder
	sDestinationPath = QFileDialog::getExistingDirectory(this,
		tr("Choose a Maya Modules Folder"),
		sDestinationPath,
		QFileDialog::ShowDirsOnly
		| QFileDialog::DontResolveSymlinks);

	if (sDestinationPath == NULL)
	{
		// User hit cancel: return without addition popups
		return;
	}

	// fix path separators
	sDestinationPath = sDestinationPath.replace("\\", "/");

	// verify plugin path
	bool bIsPluginPath = false;
	QString sPluginsPath = sDestinationPath;
	if (sPluginsPath.endsWith("/modules") == false)
	{
		sPluginsPath += "/modules";
	}
	if (QDir(sPluginsPath).exists())
	{
		bIsPluginPath = true;
	}


	if (bIsPluginPath == false)
	{
		// Warning, not a valid plugins folder path
		auto userChoice = QMessageBox::warning(0, "Daz To Maya",
			tr("The selected folder may not be a valid Maya Modules folder.  Please select a \
Modules folder to install the module.\n\nYou can choose to Abort and select a new folder, \
or Ignore this warning and install the module anyway."),
QMessageBox::Ignore | QMessageBox::Abort,
QMessageBox::Abort);
		if (userChoice == QMessageBox::StandardButton::Abort)
			return;

	}

	// create plugins folder if does not exist
	if (QDir(sPluginsPath).exists() == false)
	{
		if (QDir().mkpath(sPluginsPath) == false)
		{
			QMessageBox::warning(0, "Daz To Maya",
				tr("Sorry, an error occured while trying to create the Modules \
path:\n\n") + sPluginsPath + tr("\n\nPlease make sure you have write permissions to \
modify the parent folder."));
			return;
		}
	}

	bool bInstallSuccessful = false;
	bInstallSuccessful = installEmbeddedArchive(sBinariesFile, sPluginsPath);

	if (bInstallSuccessful)
	{
		QMessageBox::information(0, "Daz To Maya",
			tr("Maya module successfully installed to: ") + sPluginsPath +
			tr("\n\nIf Maya is running, please quit and restart Maya to continue \
Bridge Export process."));
	}
	else
	{
		QMessageBox::warning(0, "Daz To Maya",
			tr("Sorry, an unknown error occured. Unable to install Maya \
module to: ") + sPluginsPath + tr("\n\nPlease make sure you have write permissions to \
modify the selected folder."));
		return;
	}

	return;
}

void DzMayaDialog::HandleOpenIntermediateFolderButton(QString sFolderPath)
{
	QString sIntermediateFolder = QDesktopServices::storageLocation(QDesktopServices::DocumentsLocation) + QDir::separator() + "DazToMaya";
#if __LEGACY_PATHS__
	sIntermediateFolder = QDesktopServices::storageLocation(QDesktopServices::DocumentsLocation) + "/DAZ 3D/Bridges/Daz To Maya/Exports";
	if (QFile(sIntermediateFolder).exists() == false)
	{
		QDir().mkpath(sIntermediateFolder);
	}
#else
	if (intermediateFolderEdit != nullptr)
	{
		sIntermediateFolder = intermediateFolderEdit->text();
	}
#endif
	sIntermediateFolder = sIntermediateFolder.replace("\\", "/");
	DzBridgeDialog::HandleOpenIntermediateFolderButton(sIntermediateFolder);
}

void DzMayaDialog::HandleSelectMayaExecutablePathButton()
{
	QString directoryName = "";
	QString sMayaExePath = m_wMayaExecutablePathEdit->text();
	directoryName = QFileInfo(sMayaExePath).dir().path();
	if (directoryName == "." || directoryName == "") {
		if (settings != nullptr && settings->value("MayaExecutablePath").isNull() != true) {
			sMayaExePath = settings->value("MayaExecutablePath").toString();
			directoryName = QFileInfo(sMayaExePath).dir().path();
		}
		if (directoryName == "." || directoryName == "") {
			// DEFAULT APPLICATION PATH
#ifdef WIN32
			directoryName = "C:/Program Files/";
#elif defined (__APPLE__)
			directoryName = "/Applications/";
#endif
		}
	}
#ifdef WIN32
	QString sExeFilter = tr("Executable Files (*.exe)");
#elif defined(__APPLE__)
	QString sExeFilter = tr("Application Bundle (*.app)");
#endif
	QString fileName = QFileDialog::getOpenFileName(this,
		tr("Select Maya Executable"),
		directoryName,
		sExeFilter,
		&sExeFilter,
		QFileDialog::ReadOnly |
		QFileDialog::DontResolveSymlinks);

#if defined(__APPLE__)
	if (fileName != "")
	{
		fileName = fileName + "/Contents/MacOS/Maya";
	}
#endif

	if (fileName != "")
	{
		m_wMayaExecutablePathEdit->setText(fileName);
		if (settings != nullptr)
		{
			settings->setValue("MayaExecutablePath", fileName);
		}
	}

}

void DzMayaDialog::HandleTextChanged(const QString& text)
{
	QObject* senderWidget = sender();
	if (senderWidget == m_wMayaExecutablePathEdit) {
		updateMayaExecutablePathEdit(isMayaTextBoxValid());
	}
	disableAcceptUntilAllRequirementsValid();
}

bool DzMayaDialog::isMayaTextBoxValid(const QString& arg_text)
{
	QString temp_text(arg_text);

	if (temp_text == "") {
		// check widget text
		temp_text = m_wMayaExecutablePathEdit->text();
	}

	// validate blender executable
	QFileInfo fi(temp_text);
	if (fi.exists() == false) {
		dzApp->log("DzBridge: disableAcceptUntilBlenderValid: DEBUG: file does not exist: " + temp_text);
		return false;
	}

	return true;
}

void DzMayaDialog::updateMayaExecutablePathEdit(bool isValid)
{
	if (!isValid && m_bMayaRequired) {
		m_wMayaExecutablePathButton->setHighlightStyle(true);
	}
	else {
		m_wMayaExecutablePathButton->setHighlightStyle(false);
	}

}

bool DzMayaDialog::disableAcceptUntilAllRequirementsValid()
{
	if (!isMayaTextBoxValid() && m_bMayaRequired)
	{
		this->setAcceptButtonText("Unable to Proceed");
		return false;
	}
	this->setAcceptButtonText("Accept");
	return true;

}

void DzMayaDialog::requireMayaExecutableWidget(bool bRequired)
{
	m_bMayaRequired = bRequired;

	if (bRequired) {
		// move GUI
		advancedLayout->removeItem(m_wMayaExecutablePathLayout);
		mainLayout->insertRow(0, m_wMayaExecutableRowLabel, m_wMayaExecutablePathLayout);
	} else {
		mainLayout->removeItem(m_wMayaExecutablePathLayout);
		advancedLayout->insertRow(0, m_wMayaExecutableRowLabel, m_wMayaExecutablePathLayout);
	}
	updateMayaExecutablePathEdit(isMayaTextBoxValid());

}

void DzMayaDialog::accept()
{
	if (m_bSetupMode) {
		saveSettings();
		return DzBasicDialog::reject();
	}

	bool bResult = HandleAcceptButtonValidationFeedback();
	if (bResult == true)
	{
		saveSettings();
		return DzBasicDialog::accept();
	}

}

bool DzMayaDialog::HandleAcceptButtonValidationFeedback()
{
	// Check if Intermedia Folder and Blender Executable are valid, if not issue Error and fail gracefully
	if (
		(m_bMayaRequired) &&
		(m_wMayaExecutablePathEdit->text() == "" || isMayaTextBoxValid() == false)
		)
	{
		QMessageBox::warning(0, tr("Maya Executable Path"), tr("Maya Executable Path must be set."), QMessageBox::Ok);
		return false;
	}
	else if (assetTypeCombo->itemData(assetTypeCombo->currentIndex()).toString() == "__")
	{
		QMessageBox::warning(0, tr("Select Asset Type"), tr("Please select an asset type from the dropdown menu."), QMessageBox::Ok);
		return false;
	}

	return true;
}

#include <QUrl>
void DzMayaDialog::HandlePdfButton()
{
	QString sDazAppDir = dzApp->getHomePath().replace("\\", "/");
	QString sPdfPath = sDazAppDir + "/docs/Plugins" + "/Daz to Maya/Daz to Maya.pdf";
	QDesktopServices::openUrl(QUrl(sPdfPath));
}

void DzMayaDialog::HandleYoutubeButton()
{
	QString url = "https://youtu.be/QMFFliYu_kw";
	QDesktopServices::openUrl(QUrl(url));
}

void DzMayaDialog::HandleSupportButton()
{
	QString url = "https://bugs.daz3d.com/hc/en-us/requests/new";
	QDesktopServices::openUrl(QUrl(url));
}


#include "moc_DzMayaDialog.cpp"
