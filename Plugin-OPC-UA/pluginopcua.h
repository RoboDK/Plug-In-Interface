#ifndef PLUGINOPCUA_H
#define PLUGINOPCUA_H


#include <QObject>
#include <QtPlugin>
#include <QDockWidget>
#include <QTextEdit>

#include "iapprobodk.h"
#include "robodktypes.h"

#include "opcua_server.h"
#include "opcua_client.h"



class QToolBar;
class QMenu;
class QAction;
class IRoboDK;
class IItem;
class FormOpcSettings;

///
/// \brief The PluginExample class shows the structure of a RoboDK plugin.
/// A RoboDK plugin must implement the IAppRoboDK and the QObject class.
///
/// \image html robodk-plugin-example.png
///
class PluginOPCUA : public QObject, IAppRoboDK
{
    Q_OBJECT
    Q_PLUGIN_METADATA(IID "RoboDK.IAppRoboDK")// FILE "metadatalugin.json")
    Q_INTERFACES(IAppRoboDK)

public:
    //------------------------------- RoboDK Plug-in Interface commands ------------------------------

    QString PluginName(void) override;    
    virtual QString PluginLoad(QMainWindow *mw, QMenuBar *menubar, QStatusBar *statusbar, RoboDK *rdk, const QString &settings="") override;
    virtual void PluginUnload() override;
    virtual void PluginLoadToolbar(QMainWindow *mw, int icon_size) override;
    virtual bool PluginItemClick(Item item, QMenu *menu, TypeClick click_type) override;
    virtual QString PluginCommand(const QString &command, const QString &value) override;
    virtual void PluginEvent(TypeEvent event_type) override;

    //----------------------------------------------------------------------------------

// Recommended pointers to use in your plugin:
public:
    /// RoboDK's <strong>main window</strong> pointer.
    QMainWindow *MainWindow;

    /// RoboDK's main <strong>status bar</strong> pointer.
    QStatusBar *StatusBar;

    /// Pointer to the <strong>RoboDK API</strong> interface.
    RoboDK *RDK;

public:
    /// Pointer to the OPC-UA server
    opcua_server *Server;

    /// Pointer to the OPC-UA client
    opcua_client *Client;

    /// Pointer to the log window widget
    QTextEdit *LogWindow;


public slots:
    // define button callbacks (or slots) here. They are triggered automatically when the button is selected.

    /// Called when we select to start/stop the OPC UA server
    void callback_StartServer(bool checked=true);

    /// Called when we select to start the OPC UA client
    void callback_StartClient();

    /// Called when the user selects OPC UA settings
    void callback_OpcSettings();

    /// Called when the settings window is closed (event triggered by the dock window)
    void callback_OpcSettingsClosed();

// define your actions: usually, one action per button
private:
    /// Pointer to the customized toolbar
    QToolBar *toolbarOpc;

    /// Pointer to the customized menu
    QMenu *menuOpc;

    /// Information action. callback_information is triggered with this action. Actions are required to populate toolbars and menus and allows getting callbacks.
    QAction *action_StartServer;

    /// Open robot pilot form action. callback_robotpilot is triggered with this action. Actions are required to populate toolbars and menus and allows getting callbacks.
    QAction *action_StartClient;

    /// Open help action. callback_help is triggered with this action. Actions are required to populate toolbars and menus and allows getting callbacks.
    QAction *action_OpcSettings;

    /// Action to display the OPC-UA server/client logs
    QAction *action_OpcLog;

    /// Pointer to the docked window.
    QDockWidget *dock_OpcSettings;

    /// Pointer to the robot pilot form.
    FormOpcSettings *form_OpcSettings;

    /// OPC messages log
    QStringList Log;


public slots:
    /// Add a message to the log
    void LogAdd(const QString &msg);

    /// Display the log window
    void LogShow();

    /// Hide the log window
    void LogHide();

signals:
    /// Signal emitted when the log changes (a new message is added)
    void LogUpdated();
};
//! [0]


#endif // PLUGINOPCUA_H
