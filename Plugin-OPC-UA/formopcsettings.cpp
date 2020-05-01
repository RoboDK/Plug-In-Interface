#include "formopcsettings.h"
#include "ui_formopcsettings.h"
#include "pluginopcua.h"

#include <QMessageBox>


FormOpcSettings::FormOpcSettings(RoboDK *rdk, QWidget *parent, PluginOPCUA *pluginopc) :
    QWidget(parent),
    ui(new Ui::FormOpcSettings)
{
    RDK = rdk;
    pPlugin = pluginopc;

    // It is important to delete the form when we close it (free memory)
    setAttribute(Qt::WA_DeleteOnClose);

    ui->setupUi(this);

    // Update the form
    FormUpdate();

    // Update the form (Status) when the log receives new messages
    connect(pPlugin, SIGNAL(LogUpdated()), this, SLOT(FormUpdate()));
    connect(pPlugin, SIGNAL(UpdateForm()), this, SLOT(FormUpdate()), Qt::QueuedConnection);
}

FormOpcSettings::~FormOpcSettings(){
    delete ui;
}

void FormOpcSettings::FormUpdate(){

    // Server parameters:
    ui->lblStatusServer->blockSignals(true);
    ui->lblStatusServer->setText(pPlugin->Server->Status());
    ui->lblStatusServer->blockSignals(false);
    ui->spnServerPort->blockSignals(true);
    ui->spnServerPort->setValue(pPlugin->Server->Port);
    ui->spnServerPort->blockSignals(false);
    ui->chkServerAutoStart->blockSignals(true);
    ui->chkServerAutoStart->setChecked(pPlugin->Server->AutoStart);
    ui->chkServerAutoStart->blockSignals(false);

    // Client parameters:
    ui->chkClientRealTime->blockSignals(true);
    ui->chkClientRealTime->setChecked(pPlugin->Client->KeepConnected);
    ui->chkClientRealTime->blockSignals(false);

    ui->txtClientEndpointURL->blockSignals(true);
    ui->txtClientEndpointURL->setText(pPlugin->Client->EndpointUrl);
    ui->txtClientEndpointURL->blockSignals(false);
}

void FormOpcSettings::on_spnServerPort_valueChanged(int arg1){
    pPlugin->Server->Port = arg1;
}
void FormOpcSettings::on_chkServerAutoStart_stateChanged(int arg1){
    pPlugin->Server->AutoStart = arg1;
}

void FormOpcSettings::on_btnServerStart_clicked(){
    pPlugin->callback_StartServer(true);
    ui->lblStatusServer->setText(pPlugin->Server->Status());
}

void FormOpcSettings::on_btnServerStop_clicked(){
    pPlugin->callback_StartServer(false);
    ui->lblStatusServer->setText(pPlugin->Server->Status());
}

void FormOpcSettings::on_txtClientEndpointURL_editingFinished(){
    pPlugin->Client->EndpointUrl = ui->txtClientEndpointURL->text();
}

void FormOpcSettings::on_btnClientListEndpoints_clicked(){
    // Display a messagebox with all available endpoints
    QStringList endpoints = pPlugin->Client->ListEndpoints();
    QString msg_txt("<strong>" + tr("Found %1 Endpoints:").arg(endpoints.length()) + "</strong>");
    foreach (QString endpt, endpoints){
        msg_txt.append(QString("<br><a href='%1'>%2</a>").arg(endpt).arg(endpt));
    }
    QMessageBox msg;
    msg.setWindowTitle(tr("Endpoints found"));
    msg.setText(msg_txt);
    msg.exec();
}

void FormOpcSettings::on_btnLog_clicked(){
    pPlugin->LogShow();
}

void FormOpcSettings::on_btnClientConnect_clicked(){
    pPlugin->Client->Start();
}

void FormOpcSettings::on_chkClientRealTime_clicked(bool checked){
    pPlugin->Client->KeepConnected = checked;
    if (checked){
        pPlugin->Client->Start();
    }
}

void FormOpcSettings::on_btnClientStop_clicked(){
    pPlugin->Client->Stop();
}
