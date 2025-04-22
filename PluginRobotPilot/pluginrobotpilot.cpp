#include "pluginrobotpilot.h"
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
    return "RobotPilot";
}


QString PluginExample::PluginLoad(QMainWindow *mw, QMenuBar *menubar, QStatusBar *statusbar, RoboDK *rdk, const QString &settings){
    Q_UNUSED(settings)

    RDK = rdk;
    MainWindow = mw;
    StatusBar = statusbar;

    // Here you can add all the "Actions": these actions are callbacks from buttons selected from the menu or the toolbar
    action_robotpilot = new QAction(tr("Robot Pilot"));

    // Make sure to connect the action to your callback (slot)
    connect(action_robotpilot, SIGNAL(triggered()), this, SLOT(callback_robotpilot()), Qt::QueuedConnection);

    // Here you can add one or more actions in the menu
    //menu1 = new QMenu("Submenu");
    //menu1->setIcon(QIcon(":/resources/submenu-icon.svg"));
    // locate utilities menu and insert inside that menu on position 3
    QMenu *menuTools = mw->findChild<QMenu *>("menu-Tools");
    int id_action = 0; // index of the action or submenu within the Tools menu
    if (menuTools != nullptr){
        if (menuTools->actions().length() > id_action){
            qDebug() << "Inserting menu action at location " << id_action;
            menuTools->insertAction(menuTools->actions()[id_action], action_robotpilot);
        } else {
            qDebug() << "Inserting menu action at the end of the utilities menu";
            menuTools->addSeparator();
            //menuUtilities->addMenu(menu1);
            menuTools->addAction(action_robotpilot);
        }
    } else {
        // tools menu not found: adding action in the main menu
        qDebug() << "Adding menu in the main menu";
        menubar->addAction(action_robotpilot);
    }

    // Important: reset the robot pilot dock/form pointer so that it is created the first time
    dock_robotpilot = nullptr;
    form_robotpilot = nullptr;

    // return string is reserverd for future compatibility
    return "";
};


void PluginExample::PluginUnload(){
    // remove the menu action and close the form
    action_robotpilot->deleteLater();
    action_robotpilot = nullptr;

    if (dock_robotpilot != nullptr){
        dock_robotpilot->close();
        dock_robotpilot = nullptr;
        form_robotpilot = nullptr;
    }

}

void PluginExample::PluginLoadToolbar(QMainWindow *mw, int icon_size){
    Q_UNUSED(mw)
    Q_UNUSED(icon_size)

    // Create a new toolbar:
    /*
    toolbar1 = mw->addToolBar("Plugin Example Toolbar");
    toolbar1->setIconSize(QSize(icon_size, icon_size));

    // Important: It is highly recommended to set an object name on toolbars. This allows saving the preferred location of the toolbar by the user
    toolbar1->setObjectName(PluginName() + "-Toolbar1");

    // Add a new button to the toolbar
    toolbar1->addAction(action_information);
    toolbar1->addAction(action_robotpilot);
    toolbar1->addAction(action_help);
    */
}


bool PluginExample::PluginItemClick(Item item, QMenu *menu, TypeClick click_type){
    Q_UNUSED(click_type)

    if (item->Type() == IItem::ITEM_TYPE_ROBOT){
        menu->actions().insert(0, action_robotpilot); // add action at the beginning
        //menu->addAction(action_robotpilot); // add action at the end
        return false;
    }
    return false;
}

QString PluginExample::PluginCommand(const QString &command, const QString &value){
    Q_UNUSED(value)

    if (command.compare("RobotPilot", Qt::CaseInsensitive) == 0){
        callback_robotpilot();
        return "Done";
    }
    return "";
}

void PluginExample::PluginEvent(TypeEvent event_type){
    switch (event_type) {
    case EventRender:
        /// Display/Render the 3D scene.
        /// At this moment we can call RDK->DrawGeometry to customize the displayed scene
        //qDebug() << "(EventRender)";
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
        //qDebug() << "==== EventChanged ====";
        if (form_robotpilot != nullptr){
            form_robotpilot->SelectRobot();
        }
        break;
    case EventAbout2Save:
        //qDebug() << "==== EventAbout2Save ====";
        /// The user requested to save the project and the RDK file will be saved to disk. It is recommended to save all station-specific settings at this moment.
        /// For example, you can use RDK.setParam("ParameterName", "ParameterValue") or RDK.setData("ParameterName", bytearray)
        //SaveSettings();
        break;
    case EventAbout2ChangeStation:
        /// The user requested to open a new RoboDK station (RDK file) or the user is navigating among different stations. This event is triggered before the current station looses focus.
        //qDebug() << "==== EventAbout2ChangeStation ====";
        //SaveSettings();
        if (dock_robotpilot) {
            dock_robotpilot->close();
            dock_robotpilot = nullptr;
        }
        break;
    case EventAbout2CloseStation:
        /// The user requested to close the currently open RoboDK station (RDK file). The RDK file may be saved if the user and the corresponding event will be triggered.
        //qDebug() << "==== EventAbout2CloseStation ====";
        //SaveSettings();
        //ROBOT = nullptr;
        if (dock_robotpilot) {
            dock_robotpilot->close();
            dock_robotpilot = nullptr;
        }
        break;
    case EventChangedStation:
        if (dock_robotpilot) {
            dock_robotpilot->close();
            dock_robotpilot = nullptr;
        }
        break;
    //default:
        //qDebug() << "Unknown/future event: " << event_type;

    }
}

//----------------------------------------------------------------------------------
// Define your own button callbacks here
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

