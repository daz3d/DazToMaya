#pragma once
#include <dzaction.h>
#include <dznode.h>
#include <dzjsonwriter.h>
#include <QtCore/qfile.h>
#include <QtCore/qtextstream.h>
#include <dzexporter.h>

#include <DzBridgeAction.h>
#include "DzMayaDialog.h"

class UnitTest_DzMayaAction;

#include "dzbridge.h"

class DzMayaAsciiExporter : public DzExporter {
	Q_OBJECT
public:
	DzMayaAsciiExporter() : DzExporter(QString("ma")) {};

public slots:
	virtual void getDefaultOptions(DzFileIOSettings* options) const {};
	virtual QString getDescription() const override { return QString("Maya Ascii File"); };
	virtual bool isFileExporter() const override { return true; };

protected:
	virtual DzError	write(const QString& filename, const DzFileIOSettings* options) override;
};

class DzMayaBinaryExporter : public DzExporter {
	Q_OBJECT
public:
	DzMayaBinaryExporter() : DzExporter(QString("mb")) {};

public slots:
	virtual void getDefaultOptions(DzFileIOSettings* options) const {};
	virtual QString getDescription() const override { return QString("Maya Binary File"); };
	virtual bool isFileExporter() const override { return true; };

protected:
	virtual DzError	write(const QString& filename, const DzFileIOSettings* options) override;
};

class DzMayaAction : public DZ_BRIDGE_NAMESPACE::DzBridgeAction {
	 Q_OBJECT
public:
	DzMayaAction();

protected:

	 void executeAction();
	 Q_INVOKABLE bool createUI();
	 Q_INVOKABLE void writeConfiguration();
	 Q_INVOKABLE void setExportOptions(DzFileIOSettings& ExportOptions);
	 QString readGuiRootFolder();

#ifdef UNITTEST_DZBRIDGE
	friend class UnitTest_DzMayaAction;
#endif

};
