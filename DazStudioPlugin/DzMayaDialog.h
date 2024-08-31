#pragma once
#include "dzbasicdialog.h"
#include <QtGui/qcombobox.h>
#include <QtCore/qsettings.h>
#include <DzBridgeDialog.h>

#include "qlineedit.h"

class QPushButton;
class QLineEdit;
class QCheckBox;
class QComboBox;
class QGroupBox;
class QLabel;
class QWidget;
class QHBoxLayout;

class DzMayaAction;

class UnitTest_DzMayaDialog;

#include "dzbridge.h"

class DzFileValidator : public QValidator {
public:
	State validate(QString& input, int& pos) const;
};

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
	Q_INVOKABLE void saveSettings() override;

	// Maya Exectuable
	DzFileValidator m_dzValidatorFileExists;
	bool isMayaTextBoxValid(const QString& text = "");
	bool disableAcceptUntilAllRequirementsValid();
	Q_INVOKABLE void requireMayaExecutableWidget(bool bRequired);

	Q_INVOKABLE QString getMayaExecutablePath() { return m_wMayaExecutablePathEdit->text(); }

protected slots:
	void HandleSelectIntermediateFolderButton();
	void HandleAssetTypeComboChange(int state);
	void HandleTargetPluginInstallerButton();
	virtual void HandleOpenIntermediateFolderButton(QString sFolderPath = "");

	void HandleSelectMayaExecutablePathButton();
	void HandleTextChanged(const QString& text);
	void updateMayaExecutablePathEdit(bool isValid);

protected:
	QLineEdit* intermediateFolderEdit;
	QPushButton* intermediateFolderButton;

	QLineEdit* m_wMayaExecutablePathEdit;
	DzBridgeBrowseButton* m_wMayaExecutablePathButton;
	QHBoxLayout* m_wMayaExecutablePathLayout;
	QLabel* m_wMayaExecutableRowLabel;

	bool m_bMayaRequired = false;

#ifdef UNITTEST_DZBRIDGE
	friend class UnitTest_DzMayaDialog;
#endif
};
