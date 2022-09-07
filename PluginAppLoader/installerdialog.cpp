#include "installerdialog.h"
#include "ui_installerdialog.h"
#include "apploader.h"
#include "unzipper.h"

#include <QMessageBox>
#include <QFileInfo>
#include <QStringList>
#include <QDir>
#include <QTemporaryFile>
#include <QSettings>
#include <QComboBox>


InstallerDialog::InstallerDialog(AppLoader* apploader, QWidget* parent) :
    QDialog(parent),
    ui(new Ui::InstallerDialog),
    pAppLoader(apploader)
{
    ui->setupUi(this);
    setModal(true);
    setAttribute(Qt::WA_DeleteOnClose);

    Qt::WindowFlags flags = windowFlags();
    flags &= ~Qt::WindowContextHelpButtonHint;
    flags |= Qt::CustomizeWindowHint;
    flags |= Qt::Window;
    setWindowFlags(flags);

    QStringList header;
    header << tr("Application");
    header << tr("Installed Version");
    header << tr("Storage");
    header << tr("Proposed Version");
    header << tr("Action");

    ui->tableWidget->setColumnCount(header.size());
    ui->tableWidget->setHorizontalHeaderLabels(header);
}

InstallerDialog::~InstallerDialog(){
    delete ui;
}

bool InstallerDialog::processPackage(const QString& package){
    Unzipper unzipper(package);
    if (!unzipper.open()){
        QMessageBox::critical(parentWidget(), tr("Error"),
            tr("Unable to open package file:<br><b>%1</b>").arg(package),
            QMessageBox::Close);
        return false;
    }

    QFileInfo fileInfo(package);
    ui->labelPackage->setText(tr("Package Name: <b>%1</b>").arg(fileInfo.fileName()));

    QDir globalFolder(pAppLoader->PathApps);
    QDir userFolder(pAppLoader->PathUserApps);

    QTemporaryFile temporaryFile;
    QString temporaryFileName;
    if (!temporaryFile.open()) {
        QMessageBox::critical(parentWidget(), tr("Error"),
            tr("Unable to create temporary file"),
            QMessageBox::Close);
        return false;
    }
    temporaryFileName = temporaryFile.fileName();
    temporaryFile.close();

    ApplicationRecord record;
    int installedCount = 0;
    int newCount = 0;

    for (quint32 i = 0; i < unzipper.entriesCount(); ++i) {
        if (!unzipper.selectEntry(i))
            break;

        QString name = unzipper.entryName();
        int slash = name.indexOf('/');
        if (slash < 0 || name.midRef(slash).compare(QString("/AppConfig.ini")) != 0)
            continue;

        name.truncate(slash);

        if (!unzipper.entryExtract(temporaryFileName))
            continue;

        QSettings manifest(temporaryFileName, QSettings::IniFormat);

        record.clear();
        record.name = name;
        record.proposedVersion = QVersionNumber::fromString(manifest.value("Version").toString());

        bool exist = false;

        if (globalFolder.exists(name)) {
            record.global = true;
            record.path = globalFolder.filePath(name + "/AppConfig.ini");
            if (!QFile::exists(record.path)) {
                record.path = globalFolder.filePath(name + "/Settings.ini");
                if (!QFile::exists(record.path))
                    record.path.clear();
            }
            if (!record.path.isEmpty()) {
                installedCount++;
                QSettings currentManifest(record.path, QSettings::IniFormat);
                record.installedVersion = QVersionNumber::fromString(
                                             currentManifest.value("Version").toString());
                records.append(record);
                exist = true;
            }
        }

        if (userFolder.exists(name)) {
            record.global = false;
            record.path = userFolder.filePath(name + "/AppConfig.ini");
            if (!QFile::exists(record.path)) {
                record.path = userFolder.filePath(name + "/Settings.ini");
                if (!QFile::exists(record.path))
                    record.path.clear();
            }
            if (!record.path.isEmpty()) {
                installedCount++;
                QSettings currentManifest(record.path, QSettings::IniFormat);
                record.installedVersion = QVersionNumber::fromString(
                                             currentManifest.value("Version").toString());
                records.append(record);
                exist = true;
            }
        }

        if (!exist) {
            record.path.clear();
            newCount++;
            records.append(record);
        }
    }

    if (installedCount > 0) {
        int row = ui->tableWidget->rowCount();
        ui->tableWidget->setRowCount(row + installedCount + 1);
        QTableWidgetItem* item = new QTableWidgetItem();
        item->setText(tr("Already installed (%1)").arg(installedCount));
        item->setTextAlignment(Qt::AlignCenter);
        QFont font = item->font();
        font.setBold(true);
        item->setFont(font);
        ui->tableWidget->setItem(row, 0, item);
        ui->tableWidget->setSpan(row, 0, 1, ui->tableWidget->columnCount());
        row++;
        for (int i = 0; i < records.count(); ++i) {
            const ApplicationRecord& entity = records.at(i);
            if (entity.path.isEmpty())
                continue;

            item = new QTableWidgetItem(entity.name);
            ui->tableWidget->setItem(row, 0, item);
            item = new QTableWidgetItem(entity.installedVersion.toString());
            item->setTextAlignment(Qt::AlignCenter);
            if (entity.installedVersion.isNull()) {
                item->setText(tr("unknown"));
                QFont font = item->font();
                font.setItalic(true);
                item->setFont(font);
            }
            ui->tableWidget->setItem(row, 1, item);
            item = new QTableWidgetItem(entity.global ? tr("Global") : tr("User"));
            item->setTextAlignment(Qt::AlignCenter);
            ui->tableWidget->setItem(row, 2, item);
            item = new QTableWidgetItem(entity.proposedVersion.toString());
            item->setTextAlignment(Qt::AlignCenter);
            if (entity.proposedVersion.isNull()) {
                item->setText(tr("unknown"));
                QFont font = item->font();
                font.setItalic(true);
                item->setFont(font);
            }
            ui->tableWidget->setItem(row, 3, item);
            QComboBox* comboBox = new QComboBox();
            comboBox->addItem(tr("Do nothing"));
            comboBox->addItem(tr("Update"));
            comboBox->addItem(tr("Install for user"));
            ui->tableWidget->setCellWidget(row, 4, comboBox);
            row++;
        }
    }

    if (newCount > 0) {
        int row = ui->tableWidget->rowCount();
        ui->tableWidget->setRowCount(row + newCount + 1);
        QTableWidgetItem* item = new QTableWidgetItem();
        item->setText(tr("Newly installed (%1)").arg(newCount));
        item->setTextAlignment(Qt::AlignCenter);
        QFont font = item->font();
        font.setBold(true);
        item->setFont(font);
        ui->tableWidget->setItem(row, 0, item);
        ui->tableWidget->setSpan(row, 0, 1, ui->tableWidget->columnCount());
        row++;
        for (int i = 0; i < records.count(); ++i) {
            const ApplicationRecord& entity = records.at(i);
            if (!entity.path.isEmpty())
                continue;

            item = new QTableWidgetItem(entity.name);
            ui->tableWidget->setItem(row, 0, item);
            item = new QTableWidgetItem(tr("not installed"));
            item->setTextAlignment(Qt::AlignCenter);
            QFont font = item->font();
            font.setItalic(true);
            item->setFont(font);
            ui->tableWidget->setItem(row, 1, item);
            ui->tableWidget->setSpan(row, 1, 1, 2);
            item = new QTableWidgetItem(entity.global ? tr("Global") : tr("User"));
            ui->tableWidget->setItem(row, 2, item);
            item = new QTableWidgetItem(entity.proposedVersion.toString());
            item->setTextAlignment(Qt::AlignCenter);
            if (entity.proposedVersion.isNull()) {
                item->setText(tr("unknown"));
                QFont font = item->font();
                font.setItalic(true);
                item->setFont(font);
            }
            ui->tableWidget->setItem(row, 3, item);
            QComboBox* comboBox = new QComboBox();
            comboBox->addItem(tr("Do nothing"));
            comboBox->addItem(tr("Install for everyone"));
            comboBox->addItem(tr("Install for user"));
            ui->tableWidget->setCellWidget(row, 4, comboBox);
            row++;
        }
    }

    return true;
}
