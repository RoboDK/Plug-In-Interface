#include "pluginopcua.h"
#include "robodktools.h"
#include "irobodk.h"
#include "iitem.h"

#include "formopcsettings.h"

#include <QMainWindow>
#include <QToolBar>
#include <QDebug>
#include <QAction>
#include <QStatusBar>
#include <QMenuBar>
#include <QTextEdit>
#include <QDateTime>
#include <QIcon>
#include <QDesktopServices>
#include <QSettings>


// only for Sleep()
#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
void Sleep(unsigned int milliseconds) {
    sleep(milliseconds);
}
#endif

//------------------------------- RoboDK Plug-in commands ------------------------------


QString PluginOPCUA::PluginName(){
    return "OPC-UA";
}


QString PluginOPCUA::PluginLoad(QMainWindow *mw, QMenuBar *menubar, QStatusBar *statusbar, RoboDK *rdk, const QString &settings){
    RDK = rdk;
    MainWindow = mw;
    StatusBar = statusbar;

    // Create empty log saved ini settings
    Log.clear();
    Log.append(tr("OPC-UA log started on ") + QDateTime::currentDateTime().toString(Qt::DateFormat::ISODateWithMs));

    //--------------------
    LogWindow = nullptr;

    // Load the plugin
    qDebug() << "Loading plugin " << PluginName();
    qDebug() << "Using settings: " << settings; // reserved for future compatibility

    // it is highly recommended to use the statusbar for debugging purposes (pass /DEBUG as an argument to see debug result in RoboDK)
    qDebug() << "Setting up the status bar";
    StatusBar->showMessage(tr("RoboDK Plugin %1 is being loaded").arg(PluginName()));

    // initialize resources for the plugin (if required):
    Q_INIT_RESOURCE(resources1);

    // Set the icon for the checkable action (Active/Inactive server)
    QIcon iconOnOff;
    iconOnOff.addPixmap(QPixmap(":/resources/on.png"), QIcon::Normal, QIcon::On);
    iconOnOff.addPixmap(QPixmap(":/resources/off.png"), QIcon::Normal, QIcon::Off);

    // Here you can add all the "Actions": these actions are callbacks from buttons selected from the menu or the toolbar
    action_StartServer = new QAction(iconOnOff, tr("Start OPC-UA Server"));
    action_StartClient = new QAction(iconOnOff, tr("Start OPC-UA Client"));
    action_OpcSettings = new QAction(QIcon(":/resources/settings.png"), tr("OPC-UA Settings"));
    action_OpcLog = new QAction(QIcon(":/resources/settings.png"), tr("OPC-UA Log"));
    action_StartServer->setCheckable(true);
    //action_StartClient->setCheckable(true);


    // Make sure to connect the action to your callback (slot)
    connect(action_StartServer, SIGNAL(triggered(bool)), this, SLOT(callback_StartServer(bool)));
    connect(action_StartClient, SIGNAL(triggered()), this, SLOT(callback_StartClient()));
    connect(action_OpcSettings, SIGNAL(triggered()), this, SLOT(callback_OpcSettings()));
    connect(action_OpcLog, SIGNAL(triggered()), this, SLOT(LogShow()));

    // Here you can add one or more actions in the menu
    menuOpc = menubar->addMenu("OPC UA");
    qDebug() << "Setting up the OPC menu bar";
    menuOpc->addAction(action_StartServer);
    menuOpc->addAction(action_StartClient);
    menuOpc->addAction(action_OpcSettings);
    menuOpc->addAction(action_OpcLog);

    // Important: reset the robot pilot dock/form pointer so that it is created the first time
    dock_OpcSettings = nullptr;
    form_OpcSettings = nullptr;


    //-------------------------------------------------------
    // Create the OPC-UA server
    Server = new opcua_server(this);

    // Create the OPC-UA Client
    Client = new opcua_client(this);

    // Load INI settings
    QSettings params(QSettings::IniFormat, QSettings::UserScope, "RoboDK-PluginsS", PluginName());
    // Retrieve server related settings
    Server->Port =  params.value("ServerPort", Server->Port).toInt();
    Server->AutoStart = params.value("ServerAutoStart", Server->AutoStart).toBool();
    if (Server->AutoStart){
        // This will emit the server callback start signal
        action_StartServer->trigger();
    }

    // Retrieve client related settings
    Client->EndpointUrl =  params.value("ClientEndpoint", Client->EndpointUrl).toString();
    Client->AutoStart = params.value("ClientAutoStart", Client->AutoStart).toBool();
    if (Client->AutoStart){
        // This will emit the server callback start signal
        action_StartClient->trigger();
    }

    // return string is reserverd for future compatibility
    return "";
};


void PluginOPCUA::PluginUnload(){
    // Cleanup the plugin
    qDebug() << "Unloading plugin " << PluginName();

    // Save the settings
    QSettings params(QSettings::IniFormat, QSettings::UserScope, "RoboDK-Plugins", PluginName());
    params.setValue("ServerPort", Server->Port);
    params.setValue("ServerAutoStart", Server->AutoStart);
    params.setValue("ClientEndpoint", Client->EndpointUrl);
    params.setValue("ClientAutoStart", Client->AutoStart);

    // remove the menu
    menuOpc->deleteLater();
    menuOpc = nullptr;
    // remove the toolbar
    toolbarOpc->deleteLater();
    toolbarOpc = nullptr;

    if (dock_OpcSettings != nullptr){
        dock_OpcSettings->close();
        dock_OpcSettings = nullptr;
        dock_OpcSettings = nullptr;
    }

    // Stop the server and the client
    qDebug() << "Waiting for the OPC-UA server to stop...";
    Server->Stop();
    while (!Server->IsStopped()){
        Sleep(1);
    }
    qDebug() << "OPC-UA server stopped";
    delete Server;
    delete Client;

    // Delete the log window (if it is open)
    LogHide();

    // remove resources
    Q_CLEANUP_RESOURCE(resources1);
}

void PluginOPCUA::PluginLoadToolbar(QMainWindow *mw, int icon_size){
    // Create a new toolbar:
    toolbarOpc = mw->addToolBar("OPC-UA");
    toolbarOpc->setIconSize(QSize(icon_size, icon_size));

    // Important: It is highly recommended to set an object name on toolbars. This allows saving the preferred location of the toolbar by the user
    toolbarOpc->setObjectName(PluginName() + "-MainToolbar");

    // Add a new button to the toolbar
    toolbarOpc->addAction(action_StartServer);
    toolbarOpc->addAction(action_StartClient);
    toolbarOpc->addAction(action_OpcSettings);
}


bool PluginOPCUA::PluginItemClick(Item item, QMenu *menu, TypeClick click_type){
    qDebug() << "Selected item: " << item->Name() << " of type " << item->Type() << " click type: " << click_type;
/*
    if (item->Type() == IItem::ITEM_TYPE_OBJECT){
        //menu->actions().insert(0, action_btn1); // add action at the beginning
        menu->addAction(action); // add action at the end
        qDebug() << "Done";
        return true;
    } else if (item->Type() == IItem::ITEM_TYPE_ROBOT){
        //menu->actions().insert(0, action_robotpilot); // add action at the beginning
        menu->addAction(action); // add action at the end
        qDebug() << "Done";
        return true;
    }*/
    return false;
}

QString PluginOPCUA::PluginCommand(const QString &command, const QString &value){
    qDebug() << "Received command: " << command << "    With value: " << value;
    if (command.compare("ServerStart", Qt::CaseInsensitive) == 0){
        // Start the OPC-UA server, unless 0 is passed as the value
        callback_StartServer(!value.contains("0"));
        return "Done";
    } else if (command.compare("ClientBrowse", Qt::CaseInsensitive) == 0){
        // Use an OPC-UA Client to connect to the server. A value can be optionally provided to override the Endpoint URL
        // Trick: Create a macro such as the following one to update the variables automatically every 100 ms
        /*
        from robolink import *    # RoboDK API
        from robodk import *      # Robot toolbox
        RDK = Robolink()
        while True:
            RDK.PluginCommand("", "ClientBrowse")
            pause(0.1)

        */
        if (!value.isEmpty()){
            Client->EndpointUrl = value;
        }
        Client->QuickBrowse();
        return "Done";
    }
    return "";
}

// Render your own graphics here. This function is called every time the OpenGL window is displayed. The RoboDK OpenGL context is active at this moment.
// Make sure to make this code as fast as possible to not provoke render lags
void PluginOPCUA::PluginEvent(TypeEvent event_type){
    /*switch (event_type) {
    case EventChanged:
        qDebug() << "An item has been added or deleted. Current station: " << RDK->getActiveStation()->Name();
        break;
    case EventMoved:
        qDebug() << "Something has moved, such as a robot, reference frame, object or tool (usually, a render event follows)";
        break;
    case EventRender:
        //qDebug() << "Render event";
        break;
    default:
        qDebug() << "Unknown/future event: " << event_type;
    }*/
}

//----------------------------------------------------------------------------------
// Define your own button callbacks here

void PluginOPCUA::callback_StartServer(bool start){
    if (start){
        Server->Start();
    } else {
        Server->Stop();
    }
}

void PluginOPCUA::callback_StartClient(){
    Client->QuickBrowse();
}

void PluginOPCUA::callback_OpcSettings(){
    if (dock_OpcSettings != nullptr){
        // prevent opening more than 1 form
        StatusBar->showMessage(tr("The OPC UA window is already open"));
        return;
    }
    qDebug() << "Opening OPC UA settings";
    form_OpcSettings = new FormOpcSettings(RDK, MainWindow, this);
    dock_OpcSettings = AddDockWidget(MainWindow, form_OpcSettings, tr("OPC UA Settings"));
    connect(form_OpcSettings, SIGNAL(destroyed()), this, SLOT(callback_OpcSettingsClosed()));
}
void PluginOPCUA::callback_OpcSettingsClosed(){
    // it is important to reset pointers when the form is closed (deleted)
    dock_OpcSettings = nullptr;
    form_OpcSettings = nullptr;
    qDebug() << "OPC UA settings window closed";
}

//--------------------------------------------------------------
// Operating with the log
void PluginOPCUA::LogAdd(const QString &msgin){
    QString strtime(QDateTime::currentDateTime().toString(Qt::DateFormat::ISODateWithMs));
    QString msg(strtime + ":" + msgin);
    qDebug() << msg;

    // Make sure the log does not get too large
    const int max_log_size = 1e5;
    if (Log.length() >= max_log_size){
        while (Log.length() >= max_log_size){
            Log.removeFirst();
        }
    }
    // Append the message to the log
    Log.append(msg);

    // Add the message to the Log window if it is open
    if (LogWindow != nullptr){
        LogWindow->append(msg);
        LogWindow->repaint();
    }

    // Trigger a signal to update the form, if required
    emit LogUpdated();
}

void PluginOPCUA::LogShow(){
    if (LogWindow != nullptr){
        return;
    }
    // Create a new window to display the log
    LogWindow = new QTextEdit(MainWindow);
    LogWindow->setAttribute(Qt::WA_DeleteOnClose);
    LogWindow->setWindowFlags(LogWindow->windowFlags() | Qt::Window);
    LogWindow->setReadOnly(true);
    LogWindow->setWindowTitle(tr("OPC-UA log"));
    LogWindow->setHtml("");
    for (int i=0; i<Log.size(); i++){
        LogWindow->append(Log.at(i));
    }
    LogWindow->repaint();
    LogWindow->show();
    QRect geom(LogWindow->geometry());
    geom.setWidth(500);
    geom.setHeight(400);
    LogWindow->setGeometry(geom);
    connect(LogWindow,SIGNAL(destroyed()), this, SLOT(LogHide()));
}
void PluginOPCUA::LogHide(){
    if (QObject::sender() == LogWindow){
        // In this case, LogHide is called by the destroyed signal, so we do not need to delete it
        LogWindow = nullptr;
        return;
    }
    // Delete the log if this function was not called by the delete function
    if (LogWindow == nullptr){
        return;
    }
    LogWindow->deleteLater();
    LogWindow = nullptr;
}


