#include "dialogapplist.h"
#include "ui_dialogapplist.h"
#include "apploader.h"

#include <QSettings>


DialogAppList::DialogAppList(AppLoader *apploader, QWidget *parent) :
    QDialog(parent),
    pAppLoader(apploader),
    ui(new Ui::DialogAppList)
{
    ui->setupUi(this);
    setModal(true);
    setAttribute(Qt::WA_DeleteOnClose);
    setWindowFlags((windowFlags() | Qt::CustomizeWindowHint | Qt::Window));// & ~(Qt::WindowContextHelpButtonHint | Qt::WindowMaximizeButtonHint | Qt::WindowMinimizeButtonHint));//Qt::WindowCloseButtonHint | // | Qt::WindowStaysOnTopHint

    UpdateForm();
}

DialogAppList::~DialogAppList() {
    delete ui;
}


void DialogAppList::UpdateForm(){
    static QIcon iconEnabled(":img/dot_green.png"); // this is a RoboDK resource
    static QIcon iconDisabled(":img/dot_red.png"); // this is a RoboDK resource

    QStringList header;
    header << tr("Application");
    header << tr("Status");
    header << tr("Action");
    header << tr("Storage");
    header << tr("Folder");
    header << QString();

    ui->tableWidget->clear();
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

        QTableWidgetItem *itemPath = new QTableWidgetItem(appmenu->NamePath);
        // item->setToolTip(appmenu->Name);

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

        ui->tableWidget->setItem(i, 0, itemName);
        ui->tableWidget->setItem(i, 1, itemStatus);
        ui->tableWidget->setCellWidget(i, 2, buttonAction);
        ui->tableWidget->setItem(i, 3, itemStorage);
        ui->tableWidget->setItem(i, 4, itemPath);
    }

    ui->tableWidget->resizeRowsToContents();
    ui->tableWidget->resizeColumnsToContents();
    ui->tableWidget->resizeRowsToContents();// needs doubled! otherwise it does not work
    ui->tableWidget->resizeColumnsToContents();
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

    QSettings settings(pathIni, QSettings::IniFormat);
    settings.setValue("Enabled", enable);

    pAppLoader->AppsReload();
    UpdateForm();
}
