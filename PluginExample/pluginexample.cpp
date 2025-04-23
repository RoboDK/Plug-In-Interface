#include "pluginexample.h"
#include "robodktools.h"
#include "irobodk.h"
#include "iitem.h"

#include "formrobotpilot.h"

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

//------------------------------- RoboDK Plug-in commands ------------------------------


QString PluginExample::PluginName(){
    return "Example Plugin";
}


QString PluginExample::PluginLoad(QMainWindow *mw, QMenuBar *menubar, QStatusBar *statusbar, RoboDK *rdk, const QString &settings){
    RDK = rdk;
    MainWindow = mw;
    StatusBar = statusbar;
    qDebug() << "Loading plugin " << PluginName();
    qDebug() << "Using settings: " << settings; // reserved for future compatibility

    // it is highly recommended to use the statusbar for debugging purposes (pass /DEBUG as an argument to see debug result in RoboDK)
    qDebug() << "Setting up the status bar";
    StatusBar->showMessage(tr("RoboDK Plugin %1 is being loaded").arg(PluginName()));

    // initialize resources for the plugin (if required):
    Q_INIT_RESOURCE(resources1);

    // Here you can add all the "Actions": these actions are callbacks from buttons selected from the menu or the toolbar
    action_information = new QAction(QIcon(":/resources/information.png"), tr("Plugin Speed Information"));
    action_robotpilot = new QAction(QIcon(":/resources/code.png"), tr("Robot Pilot Form"));
    action_help = new QAction(QIcon(":/resources/help.png"), tr("RoboDK Plugins - Help"));
    // Make sure to connect the action to your callback (slot)
    connect(action_information, SIGNAL(triggered()), this, SLOT(callback_information()), Qt::QueuedConnection);
    connect(action_robotpilot, SIGNAL(triggered()), this, SLOT(callback_robotpilot()), Qt::QueuedConnection);
    connect(action_help, SIGNAL(triggered()), this, SLOT(callback_help()), Qt::QueuedConnection);

    // Here you can add one or more actions in the menu
    menu1 = menubar->addMenu("Plugin Example Menu");
    qDebug() << "Setting up the menu bar";
    menu1->addAction(action_information);
    menu1->addAction(action_robotpilot);
    menu1->addAction(action_help);

    // Important: reset the robot pilot dock/form pointer so that it is created the first time
    dock_robotpilot = nullptr;
    form_robotpilot = nullptr;

    // return string is reserverd for future compatibility
    return "";
};


void PluginExample::PluginUnload(){
    // Cleanup the plugin
    qDebug() << "Unloading plugin " << PluginName();

    // remove the menu
    menu1->deleteLater();
    menu1 = nullptr;
    // remove the toolbar
    toolbar1->deleteLater();
    toolbar1 = nullptr;

    if (dock_robotpilot != nullptr){
        dock_robotpilot->close();
        dock_robotpilot = nullptr;
        form_robotpilot = nullptr;
    }

    // remove resources
    Q_CLEANUP_RESOURCE(resources1);
}

void PluginExample::PluginLoadToolbar(QMainWindow *mw, int icon_size){
    // Create a new toolbar:
    toolbar1 = mw->addToolBar("Plugin Example Toolbar");
    toolbar1->setIconSize(QSize(icon_size, icon_size));

    // Important: It is highly recommended to set an object name on toolbars. This allows saving the preferred location of the toolbar by the user
    toolbar1->setObjectName(PluginName() + "-Toolbar1");

    // Add a new button to the toolbar
    toolbar1->addAction(action_information);
    toolbar1->addAction(action_robotpilot);
    toolbar1->addAction(action_help);
}


bool PluginExample::PluginItemClick(Item item, QMenu *menu, TypeClick click_type){
    qDebug() << "Selected item: " << item->Name() << " of type " << item->Type() << " click type: " << click_type;

    if (item->Type() == IItem::ITEM_TYPE_OBJECT){
        //menu->actions().insert(0, action_btn1); // add action at the beginning
        menu->addAction(action_information); // add action at the end
        qDebug() << "Done";
        return false;
    } else if (item->Type() == IItem::ITEM_TYPE_ROBOT){
        //menu->actions().insert(0, action_robotpilot); // add action at the beginning
        menu->addAction(action_robotpilot); // add action at the end
        qDebug() << "Done";
        return false;
    }
    return false;
}

QString PluginExample::PluginCommand(const QString &command, const QString &value){
    qDebug() << "Sent command: " << command << "    With value: " << value;
    if (command.compare("Information", Qt::CaseInsensitive) == 0){
        callback_information();
        return "Done";
    } else if (command.compare("RobotPilot", Qt::CaseInsensitive) == 0){
        callback_robotpilot();
        return "Done";
    }

    return "";
}

void PluginExample::PluginEvent(TypeEvent event_type) {
    switch (event_type)
    {
    case EventRender:
        /// Display/Render the 3D scene.
        /// At this moment we can call RDK->DrawGeometry to customize the displayed scene
        /// qDebug() << "==== EventRender ====";
        break;

    case EventMoved:
        /// qDebug() << "Something has moved, such as a robot, reference frame, object or tool.
        /// It is very likely that an EventRender will be triggered immediately after this event
        /// qDebug() << "==== EventMoved ====";
        break;

    case EventChanged:
        /// qDebug() << "An item has been added or deleted. Current station: " << RDK->getActiveStation()->Name();
        /// If we added a new item (for example, a reference frame) it is very likely that an EventMoved will follow with the updated position of the newly added item(s)
        /// This event is also triggered when we change the active station and a new station gains focus.

        /// Example to check if the station changed and to load settings
        //if (RDK->getActiveStation() != STATION){
        //    SetDefaultSettings();
        //    STATION = RDK->getActiveStation();
        //    LoadSettings(); // will select the robot if there are settings.
        //}
        qDebug() << "==== EventChanged ====";
        if (form_robotpilot != nullptr) {
            form_robotpilot->SelectRobot();
        }
        break;

    case EventChangedStation:
        qDebug() << "==== EventChangedStation ====";

        if (dock_robotpilot) {
            dock_robotpilot->close();
            dock_robotpilot = nullptr;
        }
        break;

    case EventAbout2Save:
        qDebug() << "==== EventAbout2Save ====";
        /// The user requested to save the project and the RDK file will be saved to disk. It is recommended to save all station-specific settings at this moment.
        /// For example, you can use RDK.setParam("ParameterName", "ParameterValue") or RDK.setData("ParameterName", bytearray)
        //SaveSettings();
        break;

    case EventAbout2ChangeStation:
        /// The user requested to open a new RoboDK station (RDK file) or the user is navigating among different stations. This event is triggered before the current station looses focus.
        qDebug() << "==== EventAbout2ChangeStation ====";
        //SaveSettings();
        if (dock_robotpilot) {
            dock_robotpilot->close();
            dock_robotpilot = nullptr;
        }
        break;

    case EventAbout2CloseStation:
        /// The user requested to close the currently open RoboDK station (RDK file). The RDK file may be saved if the user and the corresponding event will be triggered.
        qDebug() << "==== EventAbout2CloseStation ====";
        //SaveSettings();
        //ROBOT = nullptr;
        if (dock_robotpilot) {
            dock_robotpilot->close();
            dock_robotpilot = nullptr;
        }
        break;

    case EventTrajectoryStep:
        qDebug() << "==== EventTrajectoryStep ====";
        break;

    default:
        if (event_type < EventApiMask) {
            qDebug() << "Unknown/future event: " << event_type;
            return;
        }
        break;
    }

    if (event_type < EventApiMask) {
        return;
    }

    int apiEvent = event_type & (EventApiMask - 1);

    // API Events
    switch (apiEvent)
    {
    case EVENT_SELECTIONTREE_CHANGED:
        qDebug() << "EVENT_SELECTIONTREE_CHANGED";
        break;

    case EVENT_ITEM_MOVED:
        qDebug() << "EVENT_ITEM_MOVED";
        break;

    case EVENT_REFERENCE_PICKED:
        qDebug() << "EVENT_REFERENCE_PICKED";
        break;

    case EVENT_REFERENCE_RELEASED:
        qDebug() << "EVENT_REFERENCE_RELEASED";
        break;

    case EVENT_TOOL_MODIFIED:
        qDebug() << "EVENT_TOOL_MODIFIED";
        break;

    case EVENT_CREATED_ISOCUBE:
        qDebug() << "EVENT_CREATED_ISOCUBE";
        break;

    case EVENT_SELECTION3D_CHANGED:
        qDebug() << "EVENT_SELECTION3D_CHANGED";
        break;

    case EVENT_VIEWPOSE_CHANGED:
        qDebug() << "EVENT_VIEWPOSE_CHANGED";
        break;

    case EVENT_ROBOT_MOVED:
        qDebug() << "EVENT_ROBOT_MOVED";
        break;

    case EVENT_KEY:
        qDebug() << "EVENT_KEY";
        break;

    case EVENT_ITEM_MOVED_POSE:
        qDebug() << "EVENT_ITEM_MOVED_POSE";
        break;

    case EVENT_COLLISIONMAP_RESET:
        qDebug() << "EVENT_COLLISIONMAP_RESET";
        break;

    case EVENT_COLLISIONMAP_TOO_LARGE:
        qDebug() << "EVENT_COLLISIONMAP_TOO_LARGE";
        break;

    case EVENT_CALIB_MEASUREMENT:
        qDebug() << "EVENT_CALIB_MEASUREMENT";
        break;

    case EVENT_SELECTION3D_CLICK:
        qDebug() << "EVENT_SELECTION3D_CLICK";
        break;

    case EVENT_CHANGED:
        qDebug() << "EVENT_CHANGED";
        break;

    case EVENT_RENAME:
        qDebug() << "EVENT_RENAME";
        break;

    case EVENT_SETVISIBLE:
        qDebug() << "EVENT_SETVISIBLE";
        break;

    case EVENT_STATIONCHANGED:
        qDebug() << "EVENT_STATIONCHANGED";
        break;

    case EVENT_PROGSLIDER_CHANGED:
        qDebug() << "EVENT_PROGSLIDER_CHANGED";
        break;

    case EVENT_PROGSLIDER_SET:
        qDebug() << "EVENT_PROGSLIDER_SET";
        break;

    default:
        qDebug() << "Unknown/future API event: " << apiEvent;
        break;
    }
}

//----------------------------------------------------------------------------------
// Define your own button callbacks here

void PluginExample::callback_information(){

    // Perform some timing tests using the RoboDK API
    RDK->ShowMessage("Starting timing tests", false);
    QString text_message_html("<strong>Plugin Timing Tests Summary on " + QDateTime::currentDateTime().toString(Qt::SystemLocaleLongDate) + ":</strong><br>");

    int ntests=10000;
    //Item robot = RDK->getItem("", IItem::ITEM_TYPE_ROBOT);
    Item robot = RDK->ItemUserPick("Pick a robot", IItem::ITEM_TYPE_ROBOT);
    if (ItemValid(robot)){
        Mat pose_fk;
        tJoints joints_ik;
        QList<tJoints> joints_ik_all;
        qint64 tstart;
        qint64 tend;

        text_message_html += + "<br>" + QString("Using robot %1").arg(robot->Name());

        // Test Forward Kinematics
        tstart = QDateTime::currentMSecsSinceEpoch();
        for (int i=0; i<ntests; i++){
            pose_fk = robot->SolveFK(robot->Joints());
        }
        tend = QDateTime::currentMSecsSinceEpoch();
        text_message_html += + "<br>" + QString("Forward Kinematics: %1 micro seconds").arg(((double)(tend-tstart)*1000)/ntests, 0, 'f', 2);

        // Test Inverse Kinematics
        tstart = QDateTime::currentMSecsSinceEpoch();
        for (int i=0; i<ntests; i++){
            joints_ik = robot->SolveIK(pose_fk);
        }
        tend = QDateTime::currentMSecsSinceEpoch();
        text_message_html += "<br>" + QString("Inverse Kinematics: %1 micro seconds").arg(((double)(tend-tstart)*1000)/ntests, 0, 'f', 2);

        // Test Forward Kinematics
        tstart = QDateTime::currentMSecsSinceEpoch();
        for (int i=0; i<ntests; i++){
            joints_ik_all = robot->SolveIK_All(pose_fk);
        }
        tend = QDateTime::currentMSecsSinceEpoch();
        text_message_html += "<br>" + QString("Inverse Kinematics: %1 micro seconds (all solutions)").arg(((double)(tend-tstart)*1000)/ntests, 0, 'f', 2);
    } else {
        text_message_html += + "<br>No robot available to run Kinematic tests";
    }


    // output through debug console
    qDebug() << text_message_html;


    RDK->ShowMessage("Retrieving all station items", false);
    QStringList item_list_names = RDK->getItemListNames();
    qDebug() << "Available items in the current station: " << item_list_names;

    QList<Item> item_list = RDK->getItemList();

    RDK->ShowMessage("Displaying list of station items", false);
    text_message_html += QString("<br>Open station <strong>%1</strong> items:").arg(RDK->getActiveStation()->Name());
    foreach (Item itm, item_list){
        Item item_parent = itm->Parent();
        if (!ItemValid(item_parent)){
            // station items do not have a parent
            text_message_html += QString("<br>%1 (station)").arg(itm->Name());
        } else {
            text_message_html += QString("<br>%1 -> <i>parent: %2</i>").arg(itm->Name()).arg(item_parent->Name());
        }

    }


    QTextEdit *text_editor = new QTextEdit("Plugin timing summary");
    text_editor->setHtml(text_message_html);

    AddDockWidget(MainWindow, text_editor, "Dock Plugin timing summary");
}

void PluginExample::callback_robotpilot(){
    if (dock_robotpilot != nullptr){
        // prevent opening more than 1 form
        RDK->ShowMessage("Robot pilot form is already open", false);
        return;
    }
    RDK->ShowMessage("Opening robot pilot form...", false);
    form_robotpilot = new FormRobotPilot(RDK, MainWindow);
    dock_robotpilot = AddDockWidget(MainWindow, form_robotpilot, "Robot Pilot");
    connect(form_robotpilot, SIGNAL(destroyed()), this, SLOT(callback_robotpilot_closed()));
}
void PluginExample::callback_robotpilot_closed(){
    // it is important to reset pointers when the form is closed (deleted)
    dock_robotpilot = nullptr;
    form_robotpilot = nullptr;
    RDK->ShowMessage("Closed robot pilot", false);
}
void PluginExample::callback_help(){
    QDesktopServices::openUrl(QUrl("https://robodk.com/CreatePlugin"));
}


