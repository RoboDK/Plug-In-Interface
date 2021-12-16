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
#include <QInputDialog>

#include "pluginpartattached.h"

#include "robodk_interface.h"
#include "iitem.h"


//------------------------------- RoboDK Plug-in commands ------------------------------

PluginPartAttached::PluginPartAttached() {

}

QString PluginPartAttached::PluginName() {
    return "Plugin Part Attached";
}

QString PluginPartAttached::PluginLoad(QMainWindow *mw, QMenuBar *menubar, QStatusBar *statusbar, RoboDK *rdk, const QString &settings) {
    RDK = rdk;
    MainWindow = mw;
    StatusBar = statusbar;

    qDebug() << "Loading plugin " << PluginName();
    qDebug() << "Using settings: " << settings; // reserved for future compatibility

    // it is highly recommended to use the statusbar for debugging purposes (pass /DEBUG as an argument to see debug result in RoboDK)
    qDebug() << "Setting up the status bar";
    StatusBar->showMessage(tr("RoboDK Plugin %1 is being loaded").arg(PluginName()));

    // Here you can add all the "Actions": these actions are callbacks from buttons selected from the menu or the toolbar
    action_robot_select_attach = new QAction(tr("Attach object(s) to this robot"));
    action_robot_select_detach = new QAction(tr("Detach object(s) from this robot"));
    action_robot_detach_all = new QAction(tr("Detach all objects from this robot"));

    action_object_select_attach = new QAction(tr("Attach this object to a robot"));
    action_objet_detach_all = new QAction(tr("Detach this object from any robot"));

    // Make sure to connect the action to your callback (slot)
    connect(action_robot_select_attach, SIGNAL(triggered(bool)), this, SLOT(callback_robot_select_attach()));
    connect(action_robot_select_detach, SIGNAL(triggered(bool)), this, SLOT(callback_robot_select_detach()));
    connect(action_robot_detach_all, SIGNAL(triggered(bool)), this, SLOT(callback_robot_detach_all()));

    connect(action_object_select_attach, SIGNAL(triggered(bool)), this, SLOT(callback_object_select_attach()));
    connect(action_objet_detach_all, SIGNAL(triggered(bool)), this, SLOT(callback_objet_detach_all()));

    // return string is reserverd for future compatibility
    return "";
};

void PluginPartAttached::PluginUnload() {
    // Cleanup the plugin
    qDebug() << "Unloading plugin " << PluginName();

    last_clicked_item = nullptr;
    attached_objects.clear();

    if (nullptr != action_robot_select_attach) {
        disconnect(action_robot_select_attach, SIGNAL(triggered(bool)), this, SLOT(callback_robot_select_attach()));
        delete action_robot_select_attach;
        action_robot_select_attach = nullptr;
    }

    if (nullptr != action_robot_select_detach) {
        disconnect(action_robot_select_detach, SIGNAL(triggered(bool)), this, SLOT(callback_robot_select_detach()));
        delete action_robot_select_detach;
        action_robot_select_detach = nullptr;
    }

    if (nullptr != action_robot_detach_all) {
        disconnect(action_robot_detach_all, SIGNAL(triggered(bool)), this, SLOT(callback_robot_detach_all()));
        delete action_robot_detach_all;
        action_robot_detach_all = nullptr;
    }

    if (nullptr != action_object_select_attach) {
        disconnect(action_object_select_attach, SIGNAL(triggered(bool)), this, SLOT(callback_object_select_attach()));
        delete action_object_select_attach;
        action_object_select_attach = nullptr;
    }

    if (nullptr != action_objet_detach_all) {
        disconnect(action_objet_detach_all, SIGNAL(triggered(bool)), this, SLOT(callback_objet_detach_all()));
        delete action_objet_detach_all;
        action_objet_detach_all = nullptr;
    }
}

bool PluginPartAttached::PluginItemClick(Item item, QMenu *menu, TypeClick click_type) {
    if (click_type != ClickRight) {
        return false;
    }

    if (!validItem(item)) {
        return false;
    }

    if (item->Type() == IItem::ITEM_TYPE_OBJECT) {

        // An object can only be attached once
        bool already_attached = isAttached(item);
        qDebug() << "Object " << item->Name() << " status: " << (already_attached ? "Attached" : "Free");

        // Create the menu option, or update if it already exist
        if (nullptr != menu) {
            menu->addSeparator();
            menu->addAction(action_object_select_attach);
            if (already_attached) {
                menu->addAction(action_objet_detach_all);
            }
        }
        return true;
    } else {
        // A parent can have multiple objects
        bool childs = hasObjects(last_clicked_item);
        qDebug() << "Parent " << item->Name() << " status: " << (childs ? "Attached" : "Free");

        // Create the menu option, or update if it already exist
        if (nullptr != menu) {
            menu->addSeparator();
            menu->addAction(action_robot_select_attach);
            if (childs) {
                menu->addAction(action_robot_select_detach);
                menu->addAction(action_robot_detach_all);
            }
        }
        return true;
    }
    return false;
}

QString PluginPartAttached::PluginCommand(const QString &command, const QString &value) {
    qDebug() << "Received command: " << command << "    with value: " << value;

    // Expected format: "Attach", "Joint|Robot|Object|". Attaches Object to Robot at Joint
    //                  "Detach", "Object". Detach Object from any Robot
    //                  "Detach", "Robot". Detach all Objects from Robot
    //
    // For now, prompting the user for selection is not supported through the PluginCommand.

    if (command.compare("Attach", Qt::CaseInsensitive) == 0) {
        QStringList values = value.split("|");
        if (values.length() != 3) {
            return "Invalid values";
        }

        int joint_id = values.at(0).toInt();

        Item object = RDK->getItem(values.at(2), IItem::ITEM_TYPE_OBJECT);
        if (!RDK->Valid(object) || !validItem(object)) {
            return "Invalid object item";
        }

        // Needs to be processed last so that last_clicked_item is the parent (robot can be the TCP, last_clicked_item will be the robot)
        Item robot = RDK->getItem(values.at(1));
        if (!RDK->Valid(robot) || !validItem(robot)) {
            return "Invalid robot item";
        }

        // Add the attachment
        attached_object_t new_item;
        new_item.joint_id = joint_id;
        new_item.parent = last_clicked_item;
        new_item.object = object;
        new_item.pose = getCustomPose(last_clicked_item, joint_id).inv() * object->PoseAbs();
        attached_objects.append(new_item);

        return "OK";
    } else if (command.compare("Detach", Qt::CaseInsensitive) == 0) {
        Item item = RDK->getItem(value);
        if (!RDK->Valid(item) || !validItem(item)) {
            return "Invalid item";
        }

        if (item->Type() == IItem::ITEM_TYPE_OBJECT) {
            callback_objet_detach_all();
        } else {
            callback_robot_detach_all();
        }
        return "OK";
    } else if (command.compare("Loaded", Qt::CaseInsensitive) == 0) {
        return "OK";
    }
    return "";
}

void PluginPartAttached::PluginEvent(TypeEvent event_type) {
    switch (event_type) {
    case EventChanged:
    {
        qDebug() << "An item has been added or deleted. Current station: " << RDK->getActiveStation()->Name();

        // Check if any attached objects or parent were removed
        for (auto it = attached_objects.begin(); it != attached_objects.end(); it++) {
            attached_object_t attached_object = *it;
            if (!RDK->Valid(attached_object.parent)) {
                qDebug() << "Removing attached object(s) from deleted robot.";
                attached_objects.erase(it--);
                continue;
            }
            if (!RDK->Valid(attached_object.object)) {
                qDebug() << "Removing deleted object from attached robot(s).";
                attached_objects.erase(it--);
                continue;
            }
        }
        break;
    }
    case EventMoved:
        //qDebug() << "Something has moved, such as a robot, reference frame, object or tool (usually, a render event follows)";
        updatePoses();
        break;
    case EventRender:
        //qDebug() << "Render event";
        break;
    default:
        qDebug() << "Unknown/future event: " << event_type;

    }
}

//----------------------------------------------------------------------------------
// Define your own button callbacks here (and other slots)

void PluginPartAttached::callback_robot_select_attach() {
    if (last_clicked_item == nullptr) {
        return;
    }

    if (last_clicked_item->Type() == IItem::ITEM_TYPE_OBJECT) {
        return;
    }

    // Get a list of free objects to show the user
    QList<Item> list_objects = RDK->getItemList(IItem::ITEM_TYPE_OBJECT);
    if (!attached_objects.empty()) {
        for (auto it = list_objects.begin(); it != list_objects.end(); it++) {
            if (isAttached(*it)) {
                list_objects.erase(it--);
            }
        }
    }

    if (list_objects.empty()) {
        return;
    }

    // Prompt user for free objects to add. Stop adding when they cancel
    QList<Item> selected_objects;
    Item object = RDK->ItemUserPick("Select an object to attach to " + last_clicked_item->Name(), list_objects);
    while (object != nullptr) {
        selected_objects.append(object);
        list_objects.removeOne(object);
        object = RDK->ItemUserPick("Select another object to attach to " + last_clicked_item->Name() + ", or Cancel to continue.", list_objects);
    }

    if (selected_objects.empty()) {
        return;
    }

    // Prompt user for the target joint
    bool success = false;
    int dof = last_clicked_item->Joints().Length();
    int joint_id = QInputDialog::getInt(this->MainWindow, "Enter the joint ID", "Enter the joint ID you would like to attach object(s) to (id 3 means joint 3)", dof, 1, dof, 1, &success);
    if (!success) {
        return;
    }

    // Add objects to the selected item
    for (const auto &selected_object : selected_objects) {
        attached_object_t new_item;
        new_item.joint_id = joint_id;
        new_item.parent = last_clicked_item;
        new_item.object = selected_object;
        new_item.pose = getCustomPose(last_clicked_item, joint_id).inv() * selected_object->PoseAbs();
        attached_objects.append(new_item);
    }
}

void PluginPartAttached::callback_robot_select_detach() {
    if (last_clicked_item == nullptr) {
        return;
    }

    if (last_clicked_item->Type() == IItem::ITEM_TYPE_OBJECT) {
        return;
    }

    // Get a list of attached objects to show the user
    QList<Item> list_objects = attachedObjects(last_clicked_item);
    if (list_objects.empty()) {
        return;
    }

    // Prompt user for attached objects to remove. Stop when they cancel
    QList<Item> selected_objects;
    Item object = RDK->ItemUserPick("Select an object to detach from " + last_clicked_item->Name(), list_objects);
    while (object != nullptr) {
        selected_objects.append(object);
        list_objects.removeOne(object);
        object = RDK->ItemUserPick("Select another object to remove from " + last_clicked_item->Name() + ", or Cancel to continue.", list_objects);
    }

    if (selected_objects.empty()) {
        return;
    }

    // Remove objects from the selected item
    for (const auto &selected_object : selected_objects) {
        for (auto it = attached_objects.begin(); it != attached_objects.end(); it++) {
            attached_object_t attached_object = *it;
            if (attached_object.parent == last_clicked_item && attached_object.object == selected_object) {
                attached_objects.erase(it--);
                break;
            }
        }
    }
}

void PluginPartAttached::callback_robot_detach_all() {
    if (last_clicked_item == nullptr) {
        return;
    }

    if (last_clicked_item->Type() == IItem::ITEM_TYPE_OBJECT) {
        return;
    }

    for (auto it = attached_objects.begin(); it != attached_objects.end(); it++) {
        attached_object_t attached_object = *it;
        if (attached_object.parent == last_clicked_item) {
            attached_objects.erase(it--);
        }
    }
}

void PluginPartAttached::callback_object_select_attach() {
    if (last_clicked_item == nullptr) {
        return;
    }

    if (last_clicked_item->Type() != IItem::ITEM_TYPE_OBJECT) {
        return;
    }


    // Get a list of robots to show the user
    QList<Item> list_robots = RDK->getItemList(IItem::ITEM_TYPE_ROBOT);
    if (list_robots.empty()) {
        return;
    }

    // Prompt user for robot to attach to
    Item robot = RDK->ItemUserPick("Select a robot to attach " + last_clicked_item->Name(), list_robots);
    if (robot == nullptr) {
        return;
    }
    //robot = robot->getLink(IItem::ITEM_TYPE_ROBOT);

    // Prompt user for the target joint
    bool success = false;
    int dof = robot->Joints().Length();
    int joint_id = QInputDialog::getInt(this->MainWindow, "Enter the joint ID", "Enter the joint ID you would like to attach the object to (id 3 means joint 3)", dof, 1, dof, 1, &success);
    if (!success) {
        return;
    }

    // Attach the object to the robot
    attached_object_t new_item;
    new_item.joint_id = joint_id;
    new_item.parent = robot;
    new_item.object = last_clicked_item;
    new_item.pose = getCustomPose(robot, joint_id).inv() * last_clicked_item->PoseAbs();
    attached_objects.append(new_item);
}

void PluginPartAttached::callback_objet_detach_all() {
    if (last_clicked_item == nullptr) {
        return;
    }

    if (last_clicked_item->Type() != IItem::ITEM_TYPE_OBJECT) {
        return;
    }

    for (auto it = attached_objects.begin(); it != attached_objects.end(); it++) {
        attached_object_t attached_object = *it;
        if (attached_object.object == last_clicked_item) {
            attached_objects.erase(it--);
        }
    }
}

//----------------------------------------------------------------------------------

bool PluginPartAttached::isAttached(Item object) {
    for (const auto &attached_object : attached_objects) {
        if (attached_object.object == object) {
            return true;
        }
    }
    return false;
}

bool PluginPartAttached::hasObjects(Item parent) {
    for (const auto &attached_object : attached_objects) {
        if (attached_object.parent == parent) {
            return true;
        }
    }
    return false;
}

QList<Item> PluginPartAttached::attachedObjects(Item parent) {
    QList<Item> childs;

    for (const auto &attached_object : attached_objects) {
        if (attached_object.parent == parent) {
            childs.append(attached_object.object);
        }
    }
    return childs;
}

bool PluginPartAttached::validItem(Item item) {
    if (item == nullptr) {
        return false;
    }

    if (item->Type() == IItem::ITEM_TYPE_OBJECT) {
        last_clicked_item = item;
        return true;
    } else {
        // A robot, external axis, etc. can have multiple objects attached to it

        // Check if we right clicked a tool and get the robot pointer instead
        if (item->Type() == IItem::ITEM_TYPE_TOOL) {
            item = item->Parent();
        }

        // Check if we selected a robot or an item attached to a robot
        if (item->Type() == IItem::ITEM_TYPE_ROBOT) {

            // Get the parent robot, this will always return the pointer to the robot
            Item robot_item = item->getLink(IItem::ITEM_TYPE_ROBOT);

            qDebug() << "Found valid parent: " << robot_item->Name();

            // At this point, we don't know which objects to attach to this robot
            last_clicked_item = robot_item;
            return true;

        }
    }
    return false;
}

Mat PluginPartAttached::getCustomPose(Item item, int joint_id) {
    QList<Mat> poses = item->JointPoses(item->Joints());
    joint_id = qBound(0, joint_id, poses.length() - 1);
    Mat pose = poses[joint_id];
    return item->PoseAbs() * pose;
}

void PluginPartAttached::updatePoses() {

    // Update all objects
    for (const auto &attached_object : attached_objects) {
        attached_object.object->setPoseAbs(getCustomPose(attached_object.parent, attached_object.joint_id) * attached_object.pose);
    }

    // We must force a new update before render (a render is on its way),
    // Keep in mind we are already inside an update operation
    // RoboDK will check for recursivity and prevent it
    if (!attached_objects.empty()) {
        RDK->Render(RoboDK::RenderUpdateOnly);
    }
}
