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
#include <QElapsedTimer>

//------------------------------- RoboDK Plug-in commands ------------------------------


QString PluginExample::PluginName(){
    return "Realtime Plugin";
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
    action_realtime = new QAction(QIcon(":/resources/red-button.png"), tr("Activate/deactivate Real Time loop"));
    action_realtime->setCheckable(true);
    timer_realtime.setInterval(0);
    //Robot = nullptr;
    connect(&timer_realtime, SIGNAL(timeout()), this, SLOT(callback_realtime_process()));

    // Make sure to connect the action to your callback (slot)
    connect(action_information, SIGNAL(triggered()), this, SLOT(callback_information()), Qt::QueuedConnection);
    connect(action_robotpilot, SIGNAL(triggered()), this, SLOT(callback_robotpilot()), Qt::QueuedConnection);
    connect(action_help, SIGNAL(triggered()), this, SLOT(callback_help()), Qt::QueuedConnection);
    connect(action_realtime, SIGNAL(triggered(bool)), this, SLOT(callback_realtime(bool)), Qt::QueuedConnection);

    // Here you can add one or more actions in the menu
    menu1 = menubar->addMenu("Real Time Plugin Example Menu");
    qDebug() << "Setting up the menu bar";
    menu1->addAction(action_information);
    menu1->addAction(action_robotpilot);
    menu1->addAction(action_help);
    menu1->addAction(action_realtime);

    // Important: reset the robot pilot dock/form pointer so that it is created the first time
    dock_robotpilot = nullptr;
    form_robotpilot = nullptr;

    // If desired, trigger the real time operation here:
    action_realtime->setChecked(false);
    callback_realtime(false);

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
    toolbar2->deleteLater();
    toolbar2 = nullptr;

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
    toolbar1 = mw->addToolBar("Real time Plugin Example Toolbar");
    toolbar1->setIconSize(QSize(icon_size, icon_size));

    // Important: It is highly recommended to set an object name on toolbars. This allows saving the preferred location of the toolbar by the user
    toolbar1->setObjectName(PluginName() + "-Toolbar1");

    // Add a new button to the toolbar
    toolbar1->addAction(action_information);
    toolbar1->addAction(action_robotpilot);
    toolbar1->addAction(action_help);

    toolbar2 = new QToolBar(("RealTime Toolbar"));
    mw->addToolBar(Qt::ToolBarArea::RightToolBarArea, toolbar2);
    toolbar2->setIconSize(QSize(icon_size*2, icon_size*2));

    // Important: It is highly recommended to set an object name on toolbars. This allows saving the preferred location of the toolbar by the user
    toolbar2->setObjectName(PluginName() + "-Toolbar2");

    // Add a new button to the toolbar
    toolbar2->addAction(action_realtime);
}


bool PluginExample::PluginItemClick(Item item, QMenu *menu, TypeClick click_type){
    qDebug() << "Selected item: " << item->Name() << " of type " << item->Type() << " click type: " << click_type;

    if (item->Type() == IItem::ITEM_TYPE_OBJECT){
        //menu->actions().insert(0, action_btn1); // add action at the beginning
        menu->addAction(action_information); // add action at the end
        qDebug() << "Done";
        return true;
    } else if (item->Type() == IItem::ITEM_TYPE_ROBOT){
        //menu->actions().insert(0, action_robotpilot); // add action at the beginning
        menu->addAction(action_robotpilot); // add action at the end
        qDebug() << "Done";
        return true;
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
    } else if (command.compare("ActivateRealtime", Qt::CaseInsensitive) == 0){
        callback_realtime(value.contains("true"));
        return "Done";
    } else if (command.startsWith("SetParam", Qt::CaseInsensitive)){
        QStringList command_param = command.split("-");
        if (command_param.length() >= 2){
            QString name(command_param.at(1));
            RDK->setParam(name, value);
        }
        return "Done";
    }

    return "";
}

// Render your own graphics here. This function is called every time the OpenGL window is displayed. The RoboDK OpenGL context is active at this moment.
// Make sure to make this code as fast as possible to not provoke render lags
void PluginExample::PluginEvent(TypeEvent event_type){
    switch (event_type) {
    case EventChanged:        
        //qDebug() << "An item has been added or deleted. Current station: " << RDK->getActiveStation()->Name();
        // Use: RDK->getActiveStation() to get the open station. This call always returns a valid pointer
        // Use: RDK->Valid(item ) to check if an item exists (it could have been deleted! Therefore, provoke a crash when using a method)
        /*if (!RDK->Valid(Robot)){
            Robot = nullptr;
        }*/

        /*if (!RDK->Valid(Robot)) {
            Robot = nullptr;
        }*/
        RobotList = RDK->getItemList(IItem::ITEM_TYPE_ROBOT);

        if (form_robotpilot != nullptr){
            form_robotpilot->SelectRobot();
        }
        break;
    case EventMoved:
        RDK->setSimulationSpeed(1.0);
        //qDebug() << "Something has moved, such as a robot, reference frame, object or tool (usually, a render event follows)";
        break;
    case EventRender:
        //qDebug() << "Render event";
        break;
    default:
        qDebug() << "Unknown/future event: " << event_type;

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
    QDockWidget *dockwidget = AddDockWidget(MainWindow, text_editor, "Dock Plugin timing summary");
    text_editor->setHtml(text_message_html);
    //text_editor->show();

    // close the dock:
    //dockwidget->close();

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
    // it is important
    dock_robotpilot = nullptr;
    form_robotpilot = nullptr;
    RDK->ShowMessage("Closed robot pilot", false);
}
void PluginExample::callback_help(){
    // it is important
    QDesktopServices::openUrl(QUrl("https://robodk.com/doc/CreatePlugin"));
}

void PluginExample::callback_realtime(bool realtime){
    qDebug() << "Running Real Time: " << realtime;
    if (realtime) {
        timer_realtime.start();
    } else {
        timer_realtime.stop();
    }
}

void PluginExample::callback_realtime_process(){
    static int time_last = QDateTime::currentMSecsSinceEpoch();
    int time_now = QDateTime::currentMSecsSinceEpoch();
    if (time_now - time_last < 1){
        return;
    }
    time_last = time_now;

    if (RobotList.length() == 0){
        qDebug() << "No robots selected or loaded";
        return;
    }

    foreach (Item robot, RobotList){
        tJoints joints(robot->Joints());
        qDebug() << "Robot: " << robot->Name();
        qDebug() << "    Current robot joints are: " << joints;
        qDebug() << "    Calculated forward kinematcs: " << robot->SolveFK(joints);

    }



    // If you have one robot you can do:
    /*if (!ItemValid(Robot)) {
        //RDK->AddFile("filename")
        Robot = RDK->ItemUserPick("Select one robot", IItem::ITEM_TYPE_ROBOT);
        if (!ItemValid(Robot)){
            qDebug() << "Robot pointer not valid!";
            return;
        }
    }
    tJoints joints(Robot->Joints());
    qDebug() << "Current robot joints are: " << joints.ToString();
    qDebug() << "Caluclated forward kinematcs: " << Robot->SolveFK(joints).ToString();
*/



}






