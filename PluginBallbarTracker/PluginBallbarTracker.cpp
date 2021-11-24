#include "PluginBallbarTracker.h"

#include <QAction>
#include <QStatusBar>
#include <QMenuBar>
#include <QtMath>

// Parents of an item up to the station, with type filtering
static QList<Item> parentsOf(Item item, QList<int> filters = {}){
    Item parent = item;
    QList<Item> parents;
    while (parent != nullptr && parent->Type() != IItem::ITEM_TYPE_STATION && parent->Type() != IItem::ITEM_TYPE_ANY) {
        parent = parent->Parent();

        if (filters.empty()){
            parents.push_back(parent);
            continue;
        }

        for (const auto &filter : filters) {
            if (parent->Type() == filter){
                parents.push_back(parent);
                break;
            }
        }
    }
    return parents;
}

// Find the common ancestor of two items
static Item findLCA(Item item1, Item item2){

    // Make an ordered list of parents (backwards). Iter on it until the parent differs.. and you get the lowest common ancestor (LCA)
    QList<Item> parents1 = parentsOf(item1);
    QList<Item> parents2 = parentsOf(item2);

    Item lca = nullptr;
    int size = std::min(parents1.size(), parents2.size());
    for (int i = 0; i < size; ++i){
        if (parents1.back() != parents2.back()){
            break;
        }
        lca = parents1.back();
        parents1.pop_back();
        parents2.pop_back();
    }
    if (lca == nullptr){
        qDebug() << item1->Name() << " does not share an ancestor with " << item2->Name();
    }
    return lca;
}

// Find the pose to apply to obtain child from parent
static Mat poseFromTo(Item item_child, Item item_parent){

    QList<Item> parents = parentsOf(item_child);
    if (!parents.contains(item_parent)){
        qDebug() << item_child->Name() << " is not a child of " << item_parent->Name();
        return Mat(false);
    }

    Mat pose = item_parent->Pose();
    for (int i = parents.size() - 1; i >= 0; --i){
        pose *= parents[i]->Pose();
    }
    pose *= item_child->Pose();

    return pose;
}

// Validates (and retrieve) a ballbar by it's two ends
bool validateBallbar(const Item bar_end_item, const Item bar_center_item, Item &bb_orbit, Item &bb_extend){
    if ((bar_end_item == nullptr) || (bar_center_item == nullptr)){
        return false;
    }

    bool is_child = false;
    Item parent = bar_end_item;
    while (parent->Type() != IItem::ITEM_TYPE_STATION && parent->Type() > IItem::ITEM_TYPE_ANY){
        if (parent->Type() == IItem::ITEM_TYPE_ROBOT_AXES || parent->Type() == IItem::ITEM_TYPE_ROBOT){
            if (bb_extend == nullptr && parent->Joints().Length() == 1){
                bb_extend = parent;
                qDebug() << "Found ballbar extend mechanism: " << bb_extend->Name();
            }
            else if (bb_orbit == nullptr && parent->Joints().Length() == 2){
                bb_orbit = parent;
                qDebug() << "Found ballbar orbit mechanism: " << bb_orbit->Name();
            }
        }

        if (parent == bar_center_item){
            is_child = true;
            break;
        }

        parent = parent->Parent();
    }

    if (is_child && bb_orbit != nullptr && bb_extend != nullptr){
        return true;
    }
    else{
        bb_orbit = nullptr;
        bb_extend = nullptr;
        return false;
    }
}

// Retrieves a ballbar starting from the attachment point item.
// A ballbar is strctured as such: attachment frame->extend mechanism->orbit mechanism->rotation frame
bool retriveBallbar(const Item bar_end_item, Item &bar_center_item, Item &bb_orbit, Item &bb_extend){
    QList<Item> frames = parentsOf(bar_end_item, { IItem::ITEM_TYPE_FRAME });
    for (const auto &frame : frames){
        if (validateBallbar(bar_end_item, frame, bb_orbit, bb_extend)){
            bar_center_item = frame;
            return true;
        }
    }
    return false;
}

//------------------------------- RoboDK Plug-in commands ------------------------------

QString PluginBallbarTracker::PluginName(){
    return "Ballbar Tracker";
}


QString PluginBallbarTracker::PluginLoad(QMainWindow *mw, QMenuBar *menubar, QStatusBar *statusbar, RoboDK *rdk, const QString &settings){
    RDK = rdk;
    MainWindow = mw;
    StatusBar = statusbar;

    qDebug() << "Loading plugin " << PluginName();
    qDebug() << "Using settings: " << settings; // reserved for future compatibility

    // it is highly recommended to use the statusbar for debugging purposes (pass /DEBUG as an argument to see debug result in RoboDK)
    qDebug() << "Setting up the status bar";
    StatusBar->showMessage(tr("RoboDK Plugin %1 is being loaded").arg(PluginName()));

    // Here you can add all the "Actions": these actions are callbacks from buttons selected from the menu or the toolbar
    action_attach = new QAction(tr("Attach ballbar"));
    action_attach->setCheckable(true);

    // Make sure to connect the action to your callback (slot)
    connect(action_attach, SIGNAL(triggered(bool)), this, SLOT(callback_attach_ballbar(bool)));

    // return string is reserverd for future compatibility
    return "";
}


void PluginBallbarTracker::PluginUnload(){
    last_clicked_item = nullptr;
    attached_ballbars.clear();

    if (nullptr != action_attach)
    {
        disconnect(action_attach, SIGNAL(triggered(bool)), this, SLOT(callback_attach_ballbar(bool)));
        delete action_attach;
        action_attach = nullptr;
    }
}


bool PluginBallbarTracker::PluginItemClick(Item item, QMenu *menu, TypeClick click_type){
    if (click_type != ClickRight){
        return false;
    }

    if (process_item(item)){
        // Find the current state of this item
        bool attached = false;
        for (const auto &bb : attached_ballbars){
            if (bb.robot == last_clicked_item){
                attached = bb.attached;
                break;
            }
        }

        // Create the menu option, or update if it already exist
        menu->addSeparator();
        action_attach->blockSignals(true);
        action_attach->setChecked(attached);
        action_attach->blockSignals(false);
        menu->addAction(action_attach);

        return true;
    }

    return false;
}

QString PluginBallbarTracker::PluginCommand(const QString &command, const QString &item_name){
    Item item = RDK->getItem(item_name);
    if (item == nullptr){
        qDebug() << "Item not found";
        return "ITEM NOT FOUND";
    }

    if (!process_item(item)){
        qDebug() << item->Name() << " is invalid";
        return "ITEM INVALID";
    }

    if (command.compare("Attach", Qt::CaseInsensitive) == 0){
        // Warning! This might open a selection menu..
        callback_attach_ballbar(true);
        qDebug() << "Attached " << item->Name();
        return "OK";
    }
    else if (command.compare("Detach", Qt::CaseInsensitive) == 0){
        callback_attach_ballbar(false);
        qDebug() << "Detached " << item->Name();
        return "OK";
    }

    if (command.compare("Reachable", Qt::CaseInsensitive) == 0){
        for (const auto &bb : attached_ballbars){
            if (bb.robot == last_clicked_item){
                return bb.reachable ? "1" : "0";
            }
        }
    }

    if (command.compare("Attached", Qt::CaseInsensitive) == 0){
        for (const auto &bb : attached_ballbars){
            if (bb.robot == last_clicked_item){
                return bb.attached ? "1" : "0";
            }
        }
    }

    return "INVALID COMMAND";
}

void PluginBallbarTracker::PluginEvent(TypeEvent event_type){
    switch (event_type){
    case EventChanged:{
        // Check if any attached ballbars were removed
        for (auto it = attached_ballbars.begin(); it != attached_ballbars.end(); it++){
            attached_ballbar_t bb = *it;
            if (!RDK->Valid(bb.robot) || !RDK->Valid(bb.ballbar_center_frame) || !RDK->Valid(bb.ballbar_end_frame) || !RDK->Valid(bb.ballbar_extend_mech) || !RDK->Valid(bb.ballbar_orbit_mech)){
                qDebug() << "Detaching ballbar, items removed.";
                attached_ballbars.erase(it--);
            }
        }
        break;
    }
    case EventMoved:
        // Update the pose of attached ballbars
        update_ballbar_pose();
        break;
    default:
        break;

    }
}

//----------------------------------------------------------------------------------
bool PluginBallbarTracker::process_item(Item item){
    if (item == nullptr){
        return false;
    }

    // Check if there is the orbit and extend mechanisms in the station
    if (RDK->getItemList(IItem::ITEM_TYPE_ROBOT_AXES).size() < 2){
        return false;
    }

    // Check if we right clicked a tool and get the robot pointer instead
    if (item->Type() == IItem::ITEM_TYPE_TOOL){
        item = item->Parent();
    }

    // Check if we selected a robot or an item attached to a robot
    if (item->Type() == IItem::ITEM_TYPE_ROBOT){

        // External axis such as the ballbar shows as ITEM_TYPE_ROBOT using Type(), but are also listed as ITEM_TYPE_ROBOT_AXES
        if (RDK->getItemList(IItem::ITEM_TYPE_ROBOT_AXES).contains(item)){
            return false;
        }

        // Get the parent robot, this will always return the pointer to the 6 axis robot, or the robot itself
        Item robot_item = item->getLink(IItem::ITEM_TYPE_ROBOT);
        qDebug() << "Found valid robot: " << robot_item->Name();

        last_clicked_item = robot_item;
        return true;
    }
    return false;
}

void PluginBallbarTracker::update_ballbar_pose(){
    bool renderUpdate = false;
    for (auto &bb : attached_ballbars){
        if (bb.attached){

            // Current ballbar values
            tJoints extend_joints = bb.ballbar_extend_mech->Joints();
            tJoints orbit_joints = bb.ballbar_orbit_mech->Joints();

            // Poses
            Item lca = findLCA(bb.robot, bb.ballbar_center_frame);
            if (lca == nullptr){
                qDebug() << "Unable to find lowest common ancestor.";
                continue;
            }
            Mat robot_pose = poseFromTo(bb.robot, lca);
            Mat bb_center_pose = poseFromTo(bb.ballbar_center_frame, lca);
            Mat bb_pose = poseFromTo(bb.ballbar_end_frame, lca);
            if (!robot_pose.Valid() || !bb_center_pose.Valid() || !bb_pose.Valid()){
                qDebug() << "Unable to retreive the ballbar poses.";
                continue;
            }

            // XYZs
            // TODO: Refactor tXYZ so that it is easier to work with. i.e. r = norm(subs2(v1, v2))
            QVector3D robot_pos(robot_pose.Get(0, 3), robot_pose.Get(1, 3), robot_pose.Get(2, 3));
            QVector3D bb_center_pos(bb_center_pose.Get(0, 3), bb_center_pose.Get(1, 3), bb_center_pose.Get(2, 3));
            QVector3D bb_pos(bb_pose.Get(0, 3), bb_pose.Get(1, 3), bb_pose.Get(2, 3));

            // Vectors
            QVector3D center2tool = bb_center_pos - robot_pos;
            QVector3D center2end = bb_center_pos - bb_pos;

            // Calculate the spherical coordinate system (r, θ, φ)
            // Radius r
            double r = center2tool.length();  // desired radius
            double r0 = center2end.length();  // current radius

            // Rho φ
            double rho = qRadiansToDegrees(qAcos(center2tool.z() / r)) - 90.0;

            // Theta θ
            double theta = 90.0;
            if (center2tool.x() != 0){
                theta = qRadiansToDegrees(qAtan2(center2tool.y(), center2tool.x()));
            }

            // Update the ballbar
            extend_joints.Data()[0] += r - r0;
            orbit_joints.Data()[0] = theta;
            orbit_joints.Data()[1] = rho;

            bb.ballbar_extend_mech->setJoints(extend_joints);
            bb.ballbar_orbit_mech->setJoints(orbit_joints);

            // Check if the position is unreachable/invalid
            tJoints lower_limits;
            tJoints upper_limits;
            bb.ballbar_extend_mech->JointLimits(&lower_limits, &upper_limits);

            bb.reachable = true;
            if ((extend_joints.Data()[0] < lower_limits.Data()[0]) || (extend_joints.Data()[0] > upper_limits.Data()[0])){
                bb.reachable = false;
                // as an option, you can add bb.detach();
            }

            renderUpdate = true;
        }
    }

    if (renderUpdate){
        RDK->Render(RoboDK::RenderUpdateOnly);
    }
}

void PluginBallbarTracker::callback_attach_ballbar(bool attach){
    if (last_clicked_item == nullptr){
        return;
    }

    // If the request is to detach, do so
    if (!attach){
        QMutableListIterator<attached_ballbar_t> i(attached_ballbars);
        while (i.hasNext()) {
            if (i.next().robot == last_clicked_item){
                i.remove();
            }
        }
        return;
    }

    // If the request is to attach, allow attaching to multiple ballbars
    attached_ballbar_t bb;
    bb.robot = last_clicked_item;

    // Select the ballbar attachment point.
    // Ease the process by showing only frames that are child of a extending mechanism (1 joint)
    {
        QList<Item> mechanisms = RDK->getItemList(IItem::ITEM_TYPE_ROBOT_AXES);
        {
            QMutableListIterator<Item> i(mechanisms);
            while (i.hasNext()) {
                if (i.next()->Joints().Length() != 1){
                    i.remove();
                }
            }
        }

        QList<Item> frames = RDK->getItemList(IItem::ITEM_TYPE_FRAME);
        {
            QMutableListIterator<Item> i(frames);
            while (i.hasNext()) {
                QList<Item> parents = parentsOf(i.next());
                bool remove = true;
                for (const Item &m : mechanisms){
                    if (parents.contains(m)){
                        remove = false;
                        break;
                    }
                }
                if (remove){
                    i.remove();
                }
            }
        }

        QList<Item> choices;
        choices.append(frames);
        bb.ballbar_end_frame = RDK->ItemUserPick("Select the ballbar attachment point", choices);
    }

    // Autotically select the ballbar origin/rotation point using parent relationship
    if (retriveBallbar(bb.ballbar_end_frame, bb.ballbar_center_frame, bb.ballbar_orbit_mech, bb.ballbar_extend_mech)){
        bb.attached = true;
        attached_ballbars.append(bb);
        update_ballbar_pose();
    }
}
