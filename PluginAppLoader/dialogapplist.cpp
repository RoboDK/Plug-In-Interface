#include "dialogapplist.h"
#include "ui_dialogapplist.h"
#include "apploader.h"
#include "tableheader.h"

#include <QSettings>
#include <QFileInfo>
#include <QDesktopServices>


DialogAppList::DialogAppList(AppLoader *apploader, QWidget *parent) :
    QDialog(parent),
    pAppLoader(apploader),
    ui(new Ui::DialogAppList)
{
    ui->setupUi(this);
    setModal(true);
    setAttribute(Qt::WA_DeleteOnClose);

    Qt::WindowFlags flags = windowFlags();
    flags &= ~Qt::WindowContextHelpButtonHint;
    flags |= Qt::CustomizeWindowHint;
    flags |= Qt::Window;
    setWindowFlags(flags);

    ui->tableWidget->setHorizontalHeader(new TableHeader(Qt::Horizontal));

    UpdateForm();
}

DialogAppList::~DialogAppList(){
    delete ui;
}


void DialogAppList::UpdateForm(){
    static QIcon iconEnabled(":/img/dot_green.png"); // this is a RoboDK resource
    static QIcon iconDisabled(":/img/dot_red.png"); // this is a RoboDK resource
    static QIcon iconFolder(":/img/newfile.png"); // this is a RoboDK resource

    QStringList header;
    header << tr("Application");
    header << tr("Version");
    header << tr("Status");
    header << tr("Action");
    header << tr("Storage");
    header << tr("Folder");
    header << QString();

    ui->tableWidget->clear();
    ui->tableWidget->setSortingEnabled(false);
    ui->tableWidget->setRowCount(pAppLoader->ListMenus.length());
    ui->tableWidget->setColumnCount(header.size());
    ui->tableWidget->setHorizontalHeaderLabels(header);

    for (int i = 0; i < pAppLoader->ListMenus.length(); i++){
        for (int column = 0; column < ui->tableWidget->columnCount(); ++column){
            QTableWidgetItem* item = ui->tableWidget->takeItem(i, column);
            if (item)
                delete item;
        }

        tAppMenu *appmenu = pAppLoader->ListMenus[i];
        QTableWidgetItem *itemName = new QTableWidgetItem(appmenu->Name);

        QTableWidgetItem *itemVersion = new QTableWidgetItem(appmenu->Version);
        itemVersion->setTextAlignment(Qt::AlignCenter);

        QTableWidgetItem *itemStatus = nullptr;
        QPushButton* buttonAction = nullptr;

        if (appmenu->Active){
            itemStatus = new QTableWidgetItem(iconEnabled, tr("Enabled"));
            buttonAction = new QPushButton(tr("DISABLE"));
            buttonAction->setProperty("action-enable", false);
        } else {
            itemStatus = new QTableWidgetItem(iconDisabled, tr("Disabled"));
            buttonAction = new QPushButton(tr("ENABLE"));
            buttonAction->setProperty("action-enable", true);
        }
        buttonAction->setProperty("action-ini", appmenu->IniPath);
        connect(buttonAction, &QPushButton::clicked,
                this, &DialogAppList::onButtonActionClicked);

        QTableWidgetItem* itemStorage = new QTableWidgetItem(
            appmenu->Global ? tr("Global") : tr("User"));
        itemStorage->setTextAlignment(Qt::AlignCenter);

        QFileInfo pathInfo(appmenu->IniPath);

        QTableWidgetItem *itemPath = new QTableWidgetItem(appmenu->NamePath);
        itemPath->setToolTip(pathInfo.absolutePath());

        QPushButton* buttonFolder = new QPushButton(iconFolder, QString());
        buttonFolder->setToolTip(tr("Open application location"));
        buttonFolder->setProperty("action-path", pathInfo.absolutePath());
        buttonFolder->setMaximumWidth(25);
        connect(buttonFolder, &QPushButton::clicked,
                this, &DialogAppList::onButtonFolderClicked);

        ui->tableWidget->setItem(i, 0, itemName);
        ui->tableWidget->setItem(i, 1, itemVersion);
        ui->tableWidget->setItem(i, 2, itemStatus);
        ui->tableWidget->setCellWidget(i, 3, buttonAction);
        ui->tableWidget->setItem(i, 4, itemStorage);
        ui->tableWidget->setItem(i, 5, itemPath);
        ui->tableWidget->setCellWidget(i, 6, buttonFolder);
    }

    ui->tableWidget->setSortingEnabled(true);
    ui->tableWidget->horizontalHeader()->setMinimumSectionSize(20);
    ui->tableWidget->resizeRowsToContents();
    ui->tableWidget->resizeColumnsToContents();
    ui->tableWidget->horizontalHeader()->setSectionResizeMode(0, QHeaderView::Stretch);
    ui->tableWidget->horizontalHeader()->setSectionResizeMode(6, QHeaderView::ResizeToContents);
}

void DialogAppList::on_btnOk_clicked(){
    deleteLater();
}

void DialogAppList::on_btnStopAppActions_clicked(){
    emit pAppLoader->stop_process();
}

void DialogAppList::on_btnReload_clicked(){
    pAppLoader->AppsReload();

    // update the list of apps
    UpdateForm();
}

void DialogAppList::onButtonActionClicked()
{
    QObject* sender = QObject::sender();
    if (!sender)
        return;

    bool enable = sender->property("action-enable").toBool();
    QString pathIni = sender->property("action-ini").toString();
    if (pathIni.isEmpty())
        return;

    pAppLoader->EnableApp(pathIni, enable);
    pAppLoader->AppsReload();
    UpdateForm();
}

void DialogAppList::onButtonFolderClicked()
{
    QObject* sender = QObject::sender();
    if (!sender)
        return;

    QString path = sender->property("action-path").toString();
    if (path.isEmpty())
        return;

    QDesktopServices::openUrl(QUrl("file:///" + path));
}
