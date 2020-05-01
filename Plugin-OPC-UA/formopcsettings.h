#ifndef FORMOPCSETTINGS_H
#define FORMOPCSETTINGS_H

#include <QDialog>

#include "robodktypes.h"

class PluginOPCUA;


namespace Ui {
class FormOpcSettings;
}

/// This form represents the saved settings for the server and client plugin
class FormOpcSettings : public QWidget
{
    Q_OBJECT

public:
    explicit FormOpcSettings(RoboDK *rdk, QWidget *parent, PluginOPCUA *pluginopc);
    ~FormOpcSettings();

public slots:
    /// Update the form
    void FormUpdate();

private slots:

    /// Callback for the OPC-UA server port
    void on_spnServerPort_valueChanged(int arg1);

    /// Callback for the checkbox to start the OPC-UA server on plugin load
    void on_chkServerAutoStart_stateChanged(int arg1);

    /// Button callback to start the OPC-UA server
    void on_btnServerStart_clicked();

    /// Button callback to stop the OPC-UA server
    void on_btnServerStop_clicked();

    /// Callback to update the client endpoint
    void on_txtClientEndpointURL_editingFinished();

    /// Callback to list endpoints
    void on_btnClientListEndpoints_clicked();

    /// Display an OPC-UA log window
    void on_btnLog_clicked();

    void on_btnClientConnect_clicked();

    void on_chkClientRealTime_clicked(bool checked);

    void on_btnClientStop_clicked();

private:
    /// Pointer to the user interface form
    Ui::FormOpcSettings *ui;

    /// Pointer to the RoboDK API
    RoboDK *RDK;

    /// Pointer to this plugin
    PluginOPCUA *pPlugin;
};

#endif // FORMOPCSETTINGS_H
