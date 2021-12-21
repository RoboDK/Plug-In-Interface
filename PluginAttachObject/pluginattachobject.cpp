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
#include <QMessageBox>

#include "pluginattachobject.h"

#include "robodk_interface.h"
#include "iitem.h"


//------------------------------- RoboDK Plug-in commands ------------------------------

PluginAttachObject::PluginAttachObject() {

}

QString PluginAttachObject::PluginName() {
    return "Plugin Attach Object";
}

QString PluginAttachObject::PluginLoad(QMainWindow *mw, QMenuBar *menubar, QStatusBar *statusbar, RoboDK *rdk, const QString &settings) {
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

    action_object_select_attach_multi = new QAction(tr("Attach selected object(s) to a robot"));
    action_objet_detach_all_multi = new QAction(tr("Detach selected object(s) from any robot"));

    // Make sure to connect the action to your callback (slot)
    connect(action_robot_select_attach, SIGNAL(triggered(bool)), this, SLOT(callback_robot_select_attach()));
    connect(action_robot_select_detach, SIGNAL(triggered(bool)), this, SLOT(callback_robot_select_detach()));
    connect(action_robot_detach_all, SIGNAL(triggered(bool)), this, SLOT(callback_robot_detach_all()));

    connect(action_object_select_attach_multi, SIGNAL(triggered(bool)), this, SLOT(callback_object_select_attach_multi()));
    connect(action_objet_detach_all_multi, SIGNAL(triggered(bool)), this, SLOT(callback_objet_detach_all_multi()));

    // return string is reserverd for future compatibility
    return "";
};

void PluginAttachObject::PluginUnload() {
    // Cleanup the plugin
    qDebug() << "Unloading plugin " << PluginName();

    attached_objects.clear();
    last_clicked_items.clear();

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

    if (nullptr != action_object_select_attach_multi) {
        disconnect(action_object_select_attach_multi, SIGNAL(triggered(bool)), this, SLOT(callback_object_select_attach_multi()));
        delete action_object_select_attach_multi;
        action_object_select_attach_multi = nullptr;
    }

    if (nullptr != action_objet_detach_all_multi) {
        disconnect(action_objet_detach_all_multi, SIGNAL(triggered(bool)), this, SLOT(callback_objet_detach_all_multi()));
        delete action_objet_detach_all_multi;
        action_objet_detach_all_multi = nullptr;
    }
}

bool PluginAttachObject::PluginItemClick(Item item, QMenu *menu, TypeClick click_type) {
    last_clicked_items.clear();

    if (click_type != ClickRight) {
        return false;
    }

    // If the user clicked a tool, this will return the robot.
    Item process_item = validItem(item);
    if (process_item == nullptr) {
        return false;
    }

    if (process_item->Type() == IItem::ITEM_TYPE_OBJECT) {

        // An object can only be attached once
        bool already_attached = isAttached(process_item);
        qDebug() << "Object " << process_item->Name() << " status: " << (already_attached ? "Attached" : "Free");

        // Create the menu option, or update if it already exist
        if (nullptr != menu) {
            menu->addSeparator();
            if (!already_attached) {
                menu->addAction(action_object_select_attach_multi);
            } else {
                menu->addAction(action_objet_detach_all_multi);
            }
        }

        last_clicked_items.append(process_item);
        return true;
    } else {
        // A parent can have multiple objects
        bool childs = hasObjects(process_item);
        qDebug() << "Parent " << process_item->Name() << " status: " << (childs ? "Attached" : "Free");

        // Create the menu option, or update if it already exist
        if (nullptr != menu) {
            menu->addSeparator();
            menu->addAction(action_robot_select_attach);
            if (childs) {
                menu->addAction(action_robot_select_detach);
                menu->addAction(action_robot_detach_all);
            }
        }

        last_clicked_items.append(process_item);
        return true;
    }
    return false;
}

bool PluginAttachObject::PluginItemClickMulti(QList<Item> &item_list, QMenu *menu, TypeClick click_type) {
    last_clicked_items.clear();

    if (click_type != ClickRight) {
        return false;
    }

    // Add multiple objects to one robot
    if (std::all_of(item_list.cbegin(), item_list.cend(), [](Item item) { return item->Type() == IItem::ITEM_TYPE_OBJECT; })) {

        bool any_attached = false;
        bool any_free = false;
        for (const auto &object : item_list) {
            if (isAttached(object)) {
                any_attached = true;
            } else {
                any_free = true;
            }
        }

        // Multi Attach/detach menus
        if (nullptr != menu) {
            menu->addSeparator();
            if (any_free) {
                menu->addAction(action_object_select_attach_multi);
            }
            if (any_attached) {
                menu->addAction(action_objet_detach_all_multi);
            }
        }

        last_clicked_items = item_list;
        return true;
    }
    return false;
}

QString PluginAttachObject::PluginCommand(const QString &command, const QString &value) {
    qDebug() << "Received command: " << command << "    with value: " << value;

    // Expected format: "Attach", "Joint|Robot|Object|". Attaches Object to Robot at Joint
    //                  "Detach", "Object". Detach Object from any Robot
    //                  "Detach", "Robot". Detach all Objects from Robot
    //
    // For now, prompting the user for selection is not supported through the PluginCommand.

    last_clicked_items.clear();

    if (command.compare("Attach", Qt::CaseInsensitive) == 0) {
        QStringList values = value.split("|");
        if (values.length() != 3) {
            return "Invalid values";
        }

        int joint_id = values.at(0).toInt();

        Item object = validItem(RDK->getItem(values.at(2), IItem::ITEM_TYPE_OBJECT));
        if (object == nullptr) {
            return "Invalid object item";
        }

        if (isAttached(object)) {
            return "Object already attached";
        }

        // Needs to be processed last so that last_clicked_item is the parent (robot can be the TCP, last_clicked_item will be the robot)
        Item robot = validItem(RDK->getItem(values.at(1)));
        if (robot == nullptr) {
            return "Invalid robot item";
        }

        attachObjects(robot, QList<Item>({ object }), joint_id);
        return "OK";

    } else if (command.compare("Detach", Qt::CaseInsensitive) == 0) {
        Item item = RDK->getItem(value);
        if (!RDK->Valid(item) || !validItem(item)) {
            return "Invalid item";
        }

        if (item->Type() == IItem::ITEM_TYPE_OBJECT) {
            detachRobotsAll(item);
        } else {
            detachObjectsAll(item);
        }
        return "OK";

    } else if (command.compare("Loaded", Qt::CaseInsensitive) == 0) {
        return "OK";
    }
    return "";
}

void PluginAttachObject::PluginEvent(TypeEvent event_type) {
    switch (event_type) {
    case EventChanged:
    {
        // Check if any attached objects or parent were removed
        for (auto it = attached_objects.begin(); it != attached_objects.end(); ) {
            attached_object_t attached_object = *it;
            if (!RDK->Valid(attached_object.parent)) {
                qDebug() << "Removing attached object(s) from deleted robot.";
                it = attached_objects.erase(it);
                continue;
            }
            if (!RDK->Valid(attached_object.object)) {
                qDebug() << "Removing deleted object from attached robot(s).";
                it = attached_objects.erase(it);
                continue;
            }
            ++it;
        }
        break;
    }
    case EventMoved:
    {
        updatePoses();
        break;
    }
    default:
        break;

    }
}

//----------------------------------------------------------------------------------
// Define your own button callbacks here (and other slots)

void PluginAttachObject::callback_robot_select_attach() {
    if (last_clicked_items.length() != 1) {
        return;
    }

    Item robot = last_clicked_items.back();
    if (robot->Type() != IItem::ITEM_TYPE_ROBOT) {
        return;
    }

    // Get a list of free objects to show the user
    QList<Item> list_objects = RDK->getItemList(IItem::ITEM_TYPE_OBJECT);
    if (!attached_objects.empty()) {
        for (auto it = list_objects.begin(); it != list_objects.end(); ) {
            if (isAttached(*it)) {
                it = list_objects.erase(it);
                continue;
            }
            ++it;
        }
    }

    if (list_objects.empty()) {
        StatusBar->showMessage("Could not find any free object to attach.");
        return;
    }

    // Prompt user for free objects to add. Stop adding when they cancel.
    // Note: RoboDK will return the only item available without prompting the user.
    //       If your select 2 out of 3 items, do not add the third automatically!

    // Get the first object
    QList<Item> selected_objects;
    Item object = RDK->ItemUserPick("Select an object to attach to " + robot->Name(), list_objects);
    if (object == nullptr) {
        return;
    }
    selected_objects.append(object);
    list_objects.removeOne(object);

    // Get additional objects
    while (!list_objects.empty()) {
        if (list_objects.size() == 1) {
            // ItemUserPick will return the only avaialbe item without prompting the user. Force-prompt the user manually.
            QMessageBox::StandardButton reply;
            reply = QMessageBox::question(nullptr, "Attach object", "Attach " + list_objects.back()->Name() + " to " + robot->Name() + "?", QMessageBox::Yes | QMessageBox::No);
            if (reply == QMessageBox::Yes) {
                object = list_objects.back();
            } else {
                object = nullptr;
            }
        } else {
            object = RDK->ItemUserPick("Select object #" + QString::number(selected_objects.size() + 1) + " to attach to " + robot->Name() + ",\nor Cancel to skip.", list_objects);
        }

        if (object == nullptr) {
            break;
        }
        selected_objects.append(object);
        list_objects.removeOne(object);
    }

    if (selected_objects.empty()) {
        return;
    }

    // Prompt user for the target joint
    bool success = false;
    int dof = robot->Joints().Length();
    int joint_id = QInputDialog::getInt(this->MainWindow, "Enter the joint ID for " + robot->Name(), "Enter the joint ID you would like to attach object(s) to (id 3 means joint 3)", dof, 1, dof, 1, &success);
    if (!success) {
        return;
    }

    // Attach selected objects to the robot
    attachObjects(robot, selected_objects, joint_id);
}

void PluginAttachObject::callback_robot_select_detach() {
    if (last_clicked_items.length() != 1) {
        return;
    }

    Item robot = last_clicked_items.back();
    if (robot->Type() != IItem::ITEM_TYPE_ROBOT) {
        return;
    }

    // Get a list of attached objects to show the user
    QList<Item> list_objects = attachedObjects(robot);
    if (list_objects.empty()) {
        return;
    }

    // Prompt user for attached objects to remove. Stop adding when they cancel.
    // Note: RoboDK will return the only item available without prompting the user.
    //       If your select 2 out of 3 items, do not add the third automatically!

    // Get the first object
    QList<Item> selected_objects;
    Item object = RDK->ItemUserPick("Select an object to detach from " + robot->Name(), list_objects);
    if (object == nullptr) {
        return;
    }
    selected_objects.append(object);
    list_objects.removeOne(object);

    // Get additional objects
    while (!list_objects.empty()) {
        if (list_objects.size() == 1) {
            // ItemUserPick will return the only avaialbe item without prompting the user. Force-prompt the user manually.
            QMessageBox::StandardButton reply;
            reply = QMessageBox::question(nullptr, "Detach object", "Detach " + list_objects.back()->Name() + " to " + robot->Name() + "?", QMessageBox::Yes | QMessageBox::No);
            if (reply == QMessageBox::Yes) {
                object = list_objects.back();
            } else {
                object = nullptr;
            }
        } else {
            object = RDK->ItemUserPick("Select object #" + QString::number(selected_objects.size() + 1) + " to remove from " + robot->Name() + ",\nor Cancel to skip.", list_objects);
        }

        if (object == nullptr) {
            break;
        }
        selected_objects.append(object);
        list_objects.removeOne(object);
    }

    if (selected_objects.empty()) {
        return;
    }

    // Remove selected objects from the robot
    detachObjects(robot, selected_objects);
}

void PluginAttachObject::callback_robot_detach_all() {
    if (last_clicked_items.length() != 1) {
        return;
    }

    Item robot = last_clicked_items.back();
    if (robot->Type() != IItem::ITEM_TYPE_ROBOT) {
        return;
    }

    detachObjectsAll(robot);
}

void PluginAttachObject::callback_object_select_attach_multi() {
    if (last_clicked_items.empty()) {
        return;
    }

    // Get a list of robots to show the user
    QList<Item> list_robots = RDK->getItemList(IItem::ITEM_TYPE_ROBOT);
    if (list_robots.empty()) {
        StatusBar->showMessage("Could not find any parent to attach to.");
        return;
    }

    // Prompt user for robot to attach to
    Item robot = RDK->ItemUserPick("Select a robot to attach selected object(s) to.", list_robots);
    if (robot == nullptr) {
        return;
    }

    // Prompt user for the target joint
    bool success = false;
    int dof = robot->Joints().Length();
    int joint_id = QInputDialog::getInt(this->MainWindow, "Enter the joint ID", "Enter the joint ID you would like to attach the selected object(s) to (id 3 means joint 3)", dof, 1, dof, 1, &success);
    if (!success) {
        return;
    }

    // Attach the object(s) to the robot
    attachObjects(robot, last_clicked_items, joint_id);
}

void PluginAttachObject::callback_objet_detach_all_multi() {
    if (last_clicked_items.empty()) {
        return;
    }

    // Detach object(s) from robots
    for (const auto &object : last_clicked_items) {
        detachRobotsAll(object);
    }
}

//----------------------------------------------------------------------------------

bool PluginAttachObject::isAttached(Item object) {
    for (const auto &attached_object : attached_objects) {
        if (attached_object.object == object) {
            return true;
        }
    }
    return false;
}

bool PluginAttachObject::hasObjects(Item parent) {
    for (const auto &attached_object : attached_objects) {
        if (attached_object.parent == parent) {
            return true;
        }
    }
    return false;
}

QList<Item> PluginAttachObject::attachedObjects(Item parent) {
    QList<Item> childs;

    for (const auto &attached_object : attached_objects) {
        if (attached_object.parent == parent) {
            childs.append(attached_object.object);
        }
    }
    return childs;
}

void PluginAttachObject::attachObjects(Item robot, const QList<Item> &objects, int joint) {
    if (nullptr == robot || objects.empty() || joint < 1) {
        return;
    }

    // Attach the object(s) to the robot
    for (const auto &object : objects) {
        if (object->Type() != IItem::ITEM_TYPE_OBJECT) {
            continue;
        }

        attached_object_t attached_object;
        attached_object.joint_id = joint;
        attached_object.parent = robot;
        attached_object.object = object;
        attached_object.pose = getCustomPose(robot, joint).inv() * object->PoseAbs();
        attached_objects.append(attached_object);
        qDebug() << "Attached " + attached_object.object->Name() + " to " + attached_object.parent->Name();
    }
}

void PluginAttachObject::detachObjects(Item robot, const QList<Item> &objects) {
    if (nullptr == robot || objects.empty()) {
        return;
    }

    // Detach object(s) from robot
    for (auto it = attached_objects.begin(); it != attached_objects.end(); ) {
        attached_object_t attached_object = *it;
        if (attached_object.parent != robot) {
            ++it;
            continue;
        }

        // Nested for-loop
        bool found = false;
        for (const auto &object : objects) {
            if (attached_object.object == object) {
                found = true;
                break;
            }
        }

        if (found) {
            qDebug() << "Detached " + attached_object.object->Name() + " from " + attached_object.parent->Name();
            it = attached_objects.erase(it);
            continue;
        }
        ++it;
    }
}

void PluginAttachObject::detachObjectsAll(Item robot) {
    if (nullptr == robot) {
        return;
    }

    // Detach object(s) from robot
    for (auto it = attached_objects.begin(); it != attached_objects.end(); ) {
        attached_object_t attached_object = *it;
        if (attached_object.parent != robot) {
            ++it;
            continue;
        }

        qDebug() << "Detached " + attached_object.object->Name() + " from " + attached_object.parent->Name();
        it = attached_objects.erase(it);
    }
}

void PluginAttachObject::detachRobotsAll(Item object) {
    if (nullptr == object) {
        return;
    }

    // Detach object from robot(s)
    for (auto it = attached_objects.begin(); it != attached_objects.end(); ) {
        attached_object_t attached_object = *it;
        if (attached_object.object != object) {
            ++it;
            continue;
        }

        qDebug() << "Detached " + attached_object.object->Name() + " from " + attached_object.parent->Name();
        it = attached_objects.erase(it);
    }
}

Item PluginAttachObject::validItem(Item item) {

    if ((item == nullptr) || !RDK->Valid(item)) {
        return nullptr;
    }

    if (item->Type() == IItem::ITEM_TYPE_OBJECT) {
        qDebug() << "Found valid object: " << item->Name();
        return item;
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
            return robot_item;
        }
    }
    return nullptr;
}

Mat PluginAttachObject::getCustomPose(Item item, int joint_id) {
    QList<Mat> poses = item->JointPoses(item->Joints());
    joint_id = qBound(0, joint_id, poses.length() - 1);
    Mat pose = poses[joint_id];
    return item->PoseAbs() * pose;
}

void PluginAttachObject::updatePoses() {

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
