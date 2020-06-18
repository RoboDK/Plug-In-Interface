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
    ui->tableWidget->clear();

    ui->tableWidget->setRowCount(pAppLoader->ListMenus.length());
    ui->tableWidget->setColumnCount(3);

    ui->tableWidget->setHorizontalHeaderLabels(QStringList() << tr("App") << tr("Enabled") << tr("Folder") );

    //////////////////////////////////////
    static QIcon icnY(":img/dot_green.png"); // this is a RoboDK resource
    static QIcon icnN(":img/dot_red.png"); // this is a RoboDK resource
    QTableWidgetItem *todelete;
    for (int i=0; i<pAppLoader->ListMenus.length(); i++){
        tAppMenu *appmenu = pAppLoader->ListMenus[i];
        QTableWidgetItem *item = new QTableWidgetItem(appmenu->Name);
        // item->setToolTip(appmenu->Name);
        item->setFlags(item->flags() & (~Qt::ItemIsEditable));
        QTableWidgetItem *item_path = new QTableWidgetItem(appmenu->NamePath);
        // item->setToolTip(appmenu->Name);
        item_path->setFlags(item_path->flags() & (~Qt::ItemIsEditable));

        QTableWidgetItem *item_loaded = nullptr;
        if (appmenu->Active){
            item_loaded = new QTableWidgetItem(QIcon(icnY), tr("Yes"));
            item_loaded->setToolTip(tr("Double click to load %1 App").arg(appmenu->Name));
        } else {
            item_loaded = new QTableWidgetItem(QIcon(icnN), tr("No"));
            item_loaded->setToolTip(tr("Double click to unload %1 App").arg(appmenu->Name));
        }
        item_loaded->setFlags(item->flags() & (~Qt::ItemIsEditable));
        todelete = ui->tableWidget->takeItem(i,0);
        if (todelete != NULL){ delete todelete; }
        todelete = ui->tableWidget->takeItem(i,1);
        if (todelete != NULL){ delete todelete; }
        todelete = ui->tableWidget->takeItem(i,2);
        if (todelete != NULL){ delete todelete; }

        ui->tableWidget->setItem(i, 0, item);
        ui->tableWidget->setItem(i, 1, item_loaded);
        ui->tableWidget->setItem(i, 2, item_path);
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
