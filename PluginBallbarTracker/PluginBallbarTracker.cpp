#include "PluginBallbarTracker.h"

#include <QAction>
#include <QStatusBar>
#include <QMenuBar>
#include <QtMath>

// Get the list of parents of an Item up to the Station, with type filtering (i.e. [ITEM_TYPE_FRAME, ITEM_TYPE_ROBOT, ..]).
static QList<Item> getAncestors(Item item, QList<int> filters = {}){
    Item parent = item;
    QList<Item> parents;
    while (parent != nullptr && parent->Type() != IItem::ITEM_TYPE_STATION && parent->Type() != IItem::ITEM_TYPE_ANY){
        parent = parent->Parent();

        if (filters.empty()){
            parents.push_back(parent);
            continue;
        }

        for (const auto &filter : filters){
            if (parent->Type() == filter){
                parents.push_back(parent);
                break;
            }
        }
    }
    return parents;
}


// Finds the lowest common ancestor (LCA) between two Items in the Station's tree.
static Item getLowestCommonAncestor(Item item1, Item item2){

    // Make an ordered list of parents (backwards). Iter on it until the parent differs.. and you get the lowest common ancestor (LCA)
    QList<Item> parents1 = getAncestors(item1);
    QList<Item> parents2 = getAncestors(item2);

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


// Gets the pose between two Items that have a hierarchical relationship in the Station's tree.
static Mat getAncestorPose(Item item_child, Item item_parent){

    if (item_child == item_parent){
        return Mat();
    }

    QList<Item> parents = getAncestors(item_child);
    if (!parents.contains(item_parent)){
        qDebug() << item_child->Name() << " is not a child of " << item_parent->Name();
        return Mat(false);
    }

    parents.push_front(item_child);
    int idx = parents.indexOf(item_parent);
    QList<Mat> poses;
    for (int i = idx - 1; i >= 0; --i){
        if (parents[i]->Type() == IItem::ITEM_TYPE_TOOL){
            poses.append(parents[i]->PoseTool());
        } else if (parents[i]->Type() == IItem::ITEM_TYPE_ROBOT){
            poses.append(parents[i]->SolveFK(parents[i]->Joints()));
        } else{
            poses.append(parents[i]->Pose());
        }
    }

    Mat pose;
    for (const auto &p : poses){
        pose *= p;
    }
    return pose;
}


// Gets the pose of an Item (item1) with respect to an another Item (item2).
static Mat getPoseWrt(Item item1, Item item2, RoboDK *rdk){

    if (item1 == item2){
        return Mat();
    }

    Mat pose1 = item1->PoseAbs();
    Mat pose2 = item2->PoseAbs();


    Item station = rdk->getActiveStation();

    if (item1->Type() == IItem::ITEM_TYPE_ROBOT || item1->Type() == IItem::ITEM_TYPE_TOOL){
        pose1 = getAncestorPose(item1, station);
    }

    if (item2->Type() == IItem::ITEM_TYPE_ROBOT || item2->Type() == IItem::ITEM_TYPE_TOOL){
        pose2 = getAncestorPose(item2, station);
    }

    return pose2.inv() * pose1;
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
            } else if (bb_orbit == nullptr && parent->Joints().Length() == 2){
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
    } else{
        bb_orbit = nullptr;
        bb_extend = nullptr;
        return false;
    }
}

// Retrieves a ballbar starting from the attachment point item.
// A ballbar is strctured as such: attachment frame->extend mechanism->orbit mechanism->rotation frame
bool retriveBallbar(const Item bar_end_item, Item &bar_center_item, Item &bb_orbit, Item &bb_extend){
    QList<Item> frames = getAncestors(bar_end_item, { IItem::ITEM_TYPE_FRAME });
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
    Q_UNUSED(menubar)

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

    if (nullptr != action_attach){
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

        return false;
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
    } else if (command.compare("Detach", Qt::CaseInsensitive) == 0){
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
    case EventChanged:
    {
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
    case EventChangedStation:
    case EventAbout2ChangeStation:
    case EventAbout2CloseStation:
        attached_ballbars.clear();
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

        if (item->Parent()->Type() == IItem::ITEM_TYPE_ROBOT){
            qDebug() << "Found valid robot tool: " << item->Name();

            last_clicked_item = item;
            return true;
        }
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
            Mat pillar_2_tool = getPoseWrt(bb.robot, bb.ballbar_center_frame, RDK);
            Mat pillar_2_end = getPoseWrt(bb.ballbar_center_frame, bb.ballbar_end_frame, RDK);

            QVector3D pillar_2_tool_vec(pillar_2_tool.Get(0, 3), pillar_2_tool.Get(1, 3), pillar_2_tool.Get(2, 3));
            QVector3D pillar_2_end_vec(pillar_2_end.Get(0, 3), pillar_2_end.Get(1, 3), pillar_2_end.Get(2, 3));

            // Calculate the spherical coordinate system (r, θ, φ)
            // Radius r
            double r = pillar_2_tool_vec.length();  // desired radius
            double r0 = pillar_2_end_vec.length();  // current radius

            // Rho φ
            double rho = 90.0 - qRadiansToDegrees(qAcos(pillar_2_tool_vec.z() / std::max(1e-6, r)));

            // Theta θ
            double theta = 180 - qRadiansToDegrees(qAcos(pillar_2_tool_vec.x() / std::max(1e-6, qSqrt(pillar_2_tool_vec.x() * pillar_2_tool_vec.x() + pillar_2_tool_vec.y() * pillar_2_tool_vec.y()))));
            if (pillar_2_tool_vec.y() > 0){
                theta = -theta;
            }

            // Update the ballbar
            extend_joints.Data()[0] += r - r0;
            orbit_joints.Data()[0] = theta;
            orbit_joints.Data()[1] = rho;

            // Check if the position is unreachable/invalid
            tJoints extend_lower_limits;
            tJoints extend_upper_limits;
            tJoints orbit_lower_limits;
            tJoints orbit_upper_limits;
            bb.ballbar_extend_mech->JointLimits(&extend_lower_limits, &extend_upper_limits);
            bb.ballbar_orbit_mech->JointLimits(&orbit_lower_limits, &orbit_upper_limits);

            bb.reachable = false;
            if ((extend_joints.Data()[0] >= extend_lower_limits.Data()[0]) && (extend_joints.Data()[0] <= extend_upper_limits.Data()[0]) &&
                (orbit_joints.Data()[0] >= orbit_lower_limits.Data()[0]) && (orbit_joints.Data()[0] <= orbit_upper_limits.Data()[0]) &&
                (orbit_joints.Data()[1] >= orbit_lower_limits.Data()[1]) && (orbit_joints.Data()[1] <= orbit_upper_limits.Data()[1])){
                bb.reachable = true;
            }

            // Remove the false check to enable auto-detach
            // By default, the ballbar is always tracked within its limits (this can lead to funny behaviours outside reach)
            if (false && !bb.reachable){
                bb.detach();
            } else{
                extend_joints.Data()[0] = std::max(extend_lower_limits.Data()[0], std::min(extend_joints.Data()[0], extend_upper_limits.Data()[0]));
                orbit_joints.Data()[0] = std::max(orbit_lower_limits.Data()[0], std::min(orbit_joints.Data()[0], orbit_upper_limits.Data()[0]));
                orbit_joints.Data()[1] = std::max(orbit_lower_limits.Data()[1], std::min(orbit_joints.Data()[1], orbit_upper_limits.Data()[1]));

                bb.ballbar_extend_mech->setJoints(extend_joints);
                bb.ballbar_orbit_mech->setJoints(orbit_joints);
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
        while (i.hasNext()){
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
            while (i.hasNext()){
                if (i.next()->Joints().Length() != 1){
                    i.remove();
                }
            }
        }

        QList<Item> frames = RDK->getItemList(IItem::ITEM_TYPE_FRAME);
        {
            QMutableListIterator<Item> i(frames);
            while (i.hasNext()){
                QList<Item> parents = getAncestors(i.next());
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
