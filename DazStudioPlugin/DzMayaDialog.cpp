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
#else
	 QFormLayout* advancedLayout = qobject_cast<QFormLayout*>(advancedWidget->layout());
	 if (advancedLayout)
	 {
		 advancedLayout->addRow("Intermediate Folder", intermediateFolderLayout);
	 }
#endif
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
	 assetNameEdit->setWhatsThis("This is the name the asset will use in Maya.");
	 assetTypeCombo->setWhatsThis("Skeletal Mesh for something with moving parts, like a character\nStatic Mesh for things like props\nAnimation for a character animation.");
	 intermediateFolderEdit->setWhatsThis("Daz To Maya will collect the assets in a subfolder under this folder.  Maya will import them from here.");
	 intermediateFolderButton->setWhatsThis("Daz To Maya will collect the assets in a subfolder under this folder.  Maya will import them from here.");
	 m_wTargetPluginInstaller->setWhatsThis("You can install the Maya Plugin by selecting the desired Maya version and then clicking Install.");

	 // Set Defaults
	 resetToDefaults();

	 // Load Settings
	 loadSavedSettings();

	 // Daz Ultra
	 m_WelcomeLabel->hide();
	 setWindowTitle(tr("Maya Export Options"));

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

	return true;
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


#include "moc_DzMayaDialog.cpp"
