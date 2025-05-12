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
#include <QDateTime>


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

PluginOPCUA::PluginOPCUA()
{
    /// workaround to trigger messages from non QObject class like the server thread.
    connect(this, SIGNAL(EmitShowMessage(QString)), this, SLOT(ShowMessage(QString)), Qt::QueuedConnection);
}

QString PluginOPCUA::PluginName(){
    return "OPC-UA";
}


QString PluginOPCUA::PluginLoad(QMainWindow *mw, QMenuBar *menubar, QStatusBar *statusbar, RoboDK *rdk, const QString &settings){
    RDK = rdk;
    MainWindow = mw;
    StatusBar = statusbar;

    // Create empty log saved ini settings
    Log.clear();
    //Log.append(tr("OPC-UA log started on ") + QDateTime::currentDateTime().toString(Qt::DateFormat::ISODateWithMs));
    Log.append(tr("OPC-UA log started on ") + QDateTime::currentDateTime().toString(Qt::DateFormat::ISODate));

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
    QIcon serverIconOnOff;
    serverIconOnOff.addPixmap(QPixmap(":/resources/ServerOn.svg"), QIcon::Normal, QIcon::On);
    serverIconOnOff.addPixmap(QPixmap(":/resources/ServerOff.svg"), QIcon::Normal, QIcon::Off);

    QIcon clientIconOnOff;
    clientIconOnOff.addPixmap(QPixmap(":/resources/ClientOn.svg"), QIcon::Normal, QIcon::On);
    clientIconOnOff.addPixmap(QPixmap(":/resources/ClientOff.svg"), QIcon::Normal, QIcon::Off);

    // Here you can add all the "Actions": these actions are callbacks from buttons selected from the menu or the toolbar
    action_StartServer = new QAction(serverIconOnOff, tr("Start OPC-UA Server"));
    //action_StartClient = new QAction(iconOnOff, tr("Start OPC-UA Client"));
    action_StartClient = new QAction(clientIconOnOff, tr("Start OPC-UA Client"));
    action_OpcSettings = new QAction(QIcon(":/resources/settings.png"), tr("OPC-UA Settings"));
    action_OpcLog = new QAction(tr("OPC-UA Log"));
    action_StartServer->setCheckable(true);
    action_StartClient->setCheckable(true);


    // Make sure to connect the action to your callback (slot)
    connect(action_StartServer, SIGNAL(triggered(bool)), this, SLOT(callback_StartServer(bool)));
    connect(action_StartClient, SIGNAL(triggered(bool)), this, SLOT(callback_StartClient(bool)));
    connect(action_OpcSettings, SIGNAL(triggered()), this, SLOT(callback_OpcSettings()));
    connect(action_OpcLog, SIGNAL(triggered()), this, SLOT(LogShow()));

    // Here you can add one or more actions in the menu
    menuOpc = menubar->addMenu("OPC UA");
    qDebug() << "Setting up the OPC menu bar";
    menuOpc->addAction(action_StartServer);
    menuOpc->addAction(action_StartClient);
    menuOpc->addSeparator();
    menuOpc->addAction(action_OpcSettings);
    menuOpc->addSeparator();
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
    /*
    QSettings params(QSettings::IniFormat, QSettings::UserScope, "RoboDK-Plugins", PluginName());
    // Retrieve server related settings    
    Server->Port = params.value("ServerPort", Server->Port).toInt();
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
    }*/

    // return string is reserverd for future compatibility
    return "";
};


void PluginOPCUA::PluginUnload(){
    // Cleanup the plugin
    qDebug() << "Unloading plugin " << PluginName();

    // Save the settings
    /*QSettings params(QSettings::IniFormat, QSettings::UserScope, "RoboDK-Plugins", PluginName());
    params.setValue("ServerPort", Server->Port);
    params.setValue("ServerAutoStart", Server->AutoStart);
    params.setValue("ClientEndpoint", Client->EndpointUrl);
    params.setValue("ClientAutoStart", Client->AutoStart);
    */

    // remove the menu
    menuOpc->deleteLater();
    menuOpc = nullptr;


    // remove the toolbars
    toolbarOpcServer->deleteLater();
    toolbarOpcServer = nullptr;

    toolbarOpcClient->deleteLater();
    toolbarOpcClient = nullptr;



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
    // Create a new toolbar for server connection:
    toolbarOpcServer = mw->addToolBar("OPC-UA Server");
    toolbarOpcServer->setIconSize(QSize(icon_size, icon_size));

    // Important: It is highly recommended to set an object name on toolbars. This allows saving the preferred location of the toolbar by the user
    toolbarOpcServer->setObjectName(PluginName() + "-Server");

    // Add a new button to the toolbar
    toolbarOpcServer->addAction(action_StartServer);


    //-------------------
    // Create a new toolbar for client
    toolbarOpcClient = mw->addToolBar("OPC-UA Client");
    toolbarOpcClient->setIconSize(QSize(icon_size, icon_size));

    // Important: It is highly recommended to set an object name on toolbars. This allows saving the preferred location of the toolbar by the user
    toolbarOpcClient->setObjectName(PluginName() + "-Client");

    // Add a new button to the toolbar
    toolbarOpcClient->addAction(action_StartClient);

    //toolbarOpc->addAction(action_OpcSettings);
}


bool PluginOPCUA::PluginItemClick(Item item, QMenu *menu, TypeClick click_type){
    Q_UNUSED(menu)

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
        from robodk.robolink import *    # RoboDK API
        from robodk.robomath import *    # Robot toolbox
        RDK = Robolink()
        while True:
            RDK.PluginCommand("", "ClientBrowse")
            pause(0.1)

        */

        if (!value.isEmpty()){
            // connect/disconnect if we provide the endpoint
            Client->Stop(); // close connection
            Client->EndpointUrl = value;
            Client->Browse(true);
            emit UpdateForm();
        } else {
            // use the connection URL provided by the user or the RDK file and keep connected
            Client->Browse(false);
        }
        return "Done";
    }
    return "";
}

// Render your own graphics here. This function is called every time the OpenGL window is displayed. The RoboDK OpenGL context is active at this moment.
// Make sure to make this code as fast as possible to not provoke render lags
void PluginOPCUA::PluginEvent(TypeEvent event_type){
    switch (event_type) {
        case EventRender:
            /// Display/Render the 3D scene.
            /// At this moment we can call RDK->DrawGeometry to customize the displayed scene
            break;
        case EventMoved:
            /// qDebug() << "Something has moved, such as a robot, reference frame, object or tool.
            /// It is very likely that an EventRender will be triggered immediately after this event
            break;
        case EventChanged:
            /// qDebug() << "An item has been added or deleted. Current station: " << RDK->getActiveStation()->Name();
            /// If we added a new item (for example, a reference frame) it is very likely that an EventMoved will follow with the updated position of the newly added item(s)
            /// This event is also triggered when we change the active station and a new station gains focus.
            // qDebug() << "==== EventChanged ====" << RDK->getActiveStation()->Name();
            break;
        case EventChangedStation:
            // we changed the station so load the new settings
            //qDebug() << "==== EventChangedStation ====" << RDK->getActiveStation()->Name();
            LoadSettings();
            break;
        case EventAbout2Save:
            // qDebug() << "==== EventAbout2Save ====" << RDK->getActiveStation()->Name();
            /// The user requested to save the project and the RDK file will be saved to disk. It is recommended to save all station-specific settings at this moment.
            /// For example, you can use RDK.setParam("ParameterName", "ParameterValue") or RDK.setData("ParameterName", bytearray)
            SaveSettings();
            break;
        case EventAbout2ChangeStation:
            /// The user requested to open a new RoboDK station (RDK file) or the user is navigating among different stations. This event is triggered before the current station looses focus.
            // qDebug() << "==== EventAbout2ChangeStation ====" << RDK->getActiveStation()->Name();
            SaveSettings();
            break;
        case EventAbout2CloseStation:
            /// The user requested to close the currently open RoboDK station (RDK file). The RDK file may be saved if the user and the corresponding event will be triggered.
            // qDebug() << "==== EventAbout2CloseStation ====" << RDK->getActiveStation()->Name();
            //SaveSettings();
            //ROBOT = nullptr;
            break;
        //default:
            // qDebug() << "Unknown/future event: " << event_type;

    }
}




bool PluginOPCUA::LoadSettings(){
    //SaveRequired = false;

    QByteArray data;
    data = RDK->getData(PluginName());

    if (data.length() == 0){ return false; }


    qint64 version = -1;

    QDataStream ds(data);
    qDebug() << "Loading OPC-UA plugin settings...";
    ds >> version;
    //qDebug() << N_Samples;
    if (version < 0){
        qDebug() << "Invalid version!";
        return false;
    }
    ds >> Server->Port;
    ds >> Server->AutoStart;
    ds >> Client->EndpointUrl;
    ds >> Client->AutoStart;
    ds >> Client->KeepConnected;
    emit UpdateForm();
    qDebug() << "Done";
    return true;
}
void PluginOPCUA::SaveSettings(){
    //if (!SaveRequired) { return; }

    qDebug() << "Saving OPC-UA plugin settings...";
    QByteArray data;
    QDataStream ds(&data, QDataStream::WriteOnly);
    qint64 version = 2;
    ds << version;
    ds << Server->Port;
    ds << Server->AutoStart;
    ds << Client->EndpointUrl;
    ds << Client->AutoStart;
    ds << Client->KeepConnected;

    RDK->setData(PluginName(), data);

    //SaveRequired = false;
    qDebug() << "Done";
}
//----------------------


//----------------------------------------------------------------------------------
// Define your own button callbacks here

void PluginOPCUA::callback_StartServer(bool start){
    if (start){
        Server->Start();
    } else {
        Server->Stop();
    }
}

void PluginOPCUA::callback_StartClient(bool start){
    if (start){
        Client->Start();
        if (!Client->KeepConnected){
            action_StartClient->setChecked(false);
        }
    } else {
        Client->Stop();
    }



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
void PluginOPCUA::ShowMessage(const QString &msg){
    // show message in the status bar + add message to log
    StatusBar->showMessage(msg);
    LogAdd(msg);
}

void PluginOPCUA::LogAdd(const QString &msgin){
    //QString strtime(QDateTime::currentDateTime().toString(Qt::DateFormat::ISODateWithMs));
    QString strtime(QDateTime::currentDateTime().toString(Qt::DateFormat::ISODate));
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
    LogWindow->setWindowTitle(tr("OPC-UA Server log"));
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


