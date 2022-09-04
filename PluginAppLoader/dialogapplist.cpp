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

    connect( ui->tableWidget, SIGNAL( cellDoubleClicked (int, int) ),  this, SLOT( onCellDoubleClicked( int, int ) ) );

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
        if (appmenu->Active){
            itemStatus = new QTableWidgetItem(iconEnabled, tr("Enabled"));
        } else {
            itemStatus = new QTableWidgetItem(iconDisabled, tr("Disabled"));
        }

        QTableWidgetItem* itemStorage = new QTableWidgetItem(
            appmenu->Global ? tr("Global") : tr("User"));

        ui->tableWidget->setItem(i, 0, itemName);
        ui->tableWidget->setItem(i, 1, itemStatus);
        ui->tableWidget->setItem(i, 3, itemStorage);
        ui->tableWidget->setItem(i, 4, itemPath);
    }

    ui->tableWidget->resizeRowsToContents();
    ui->tableWidget->resizeColumnsToContents();
    ui->tableWidget->resizeRowsToContents();// needs doubled! otherwise it does not work
    ui->tableWidget->resizeColumnsToContents();
}

void DialogAppList::onCellDoubleClicked( int a, int b){
    if (a < 0 || a >= pAppLoader->ListMenus.length()){
        // this should never happen
        return;
    }
    tAppMenu *appmenu = pAppLoader->ListMenus[a];
    bool set_enabled = !appmenu->Active;
    appmenu->Active = set_enabled;
    if (appmenu->Toolbar != nullptr){
        appmenu->Toolbar->Active = set_enabled;
    }

    //--------- set enabled or disabled in the INI file
    // warning: this may not work depending on where we installed RoboDK
    QSettings settings(appmenu->IniPath, QSettings::IniFormat);
    settings.setValue("Enabled", set_enabled);
    //------------------------------------------

    // clean up apps from the User Interface and load them again
    // pAppLoader->AppsSearch(); // this is not needed (it may not work if we don't have rights to change the INI files)
    pAppLoader->AppsReload();

    // update the list of apps
    UpdateForm();
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
