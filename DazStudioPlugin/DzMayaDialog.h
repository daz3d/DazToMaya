#pragma once
#include "dzbasicdialog.h"
#include <QtGui/qcombobox.h>
#include <QtCore/qsettings.h>
#include <DzBridgeDialog.h>

class QPushButton;
class QLineEdit;
class QCheckBox;
class QComboBox;
class QGroupBox;
class QLabel;
class QWidget;
class DzMayaAction;

class UnitTest_DzMayaDialog;

#include "dzbridge.h"

class DzMayaDialog : public DZ_BRIDGE_NAMESPACE::DzBridgeDialog{
	friend DzMayaAction;
	Q_OBJECT
	Q_PROPERTY(QWidget* intermediateFolderEdit READ getIntermediateFolderEdit)
public:
	Q_INVOKABLE QLineEdit* getIntermediateFolderEdit() { return intermediateFolderEdit; }

	/** Constructor **/
	 DzMayaDialog(QWidget *parent=nullptr);

	/** Destructor **/
	virtual ~DzMayaDialog() {}

	Q_INVOKABLE void resetToDefaults() override;
	Q_INVOKABLE bool loadSavedSettings() override;

protected slots:
	void HandleSelectIntermediateFolderButton();
	void HandleAssetTypeComboChange(int state);
	void HandleTargetPluginInstallerButton();

protected:
	QLineEdit* intermediateFolderEdit;
	QPushButton* intermediateFolderButton;

#ifdef UNITTEST_DZBRIDGE
	friend class UnitTest_DzMayaDialog;
#endif
};
