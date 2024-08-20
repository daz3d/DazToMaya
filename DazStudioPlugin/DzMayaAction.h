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

class DzMayaExporter : public DzExporter {
	Q_OBJECT
public:
	DzMayaExporter(QString sExt) : DzExporter(sExt) {};

public slots:
	virtual void getDefaultOptions(DzFileIOSettings* options) const {};
	virtual bool isFileExporter() const override { return true; };

protected:
	virtual DzError	write(const QString& filename, const DzFileIOSettings* options) override;

	friend class DzMayaAsciiExporter;
	friend class DzMayaBinaryExporter;
};

class DzMayaAsciiExporter : public DzMayaExporter {
	Q_OBJECT
public:
	DzMayaAsciiExporter() : DzMayaExporter(QString("ma")) {};

public slots:
	virtual QString getDescription() const override { return QString("Maya Ascii File"); };
};

class DzMayaBinaryExporter : public DzMayaExporter {
	Q_OBJECT
public:
	DzMayaBinaryExporter() : DzMayaExporter(QString("mb")) {};

public slots:
	virtual QString getDescription() const override { return QString("Maya Binary File"); };
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

	 friend class DzMayaExporter;
#ifdef UNITTEST_DZBRIDGE
	friend class UnitTest_DzMayaAction;
#endif

};
