#include "PluginLockTCP.h"

#include <QAction>
#include <QStatusBar>
#include <QMenuBar>


//------------------------------- RoboDK Plug-in commands ------------------------------

QString PluginLockTCP::PluginName(){
    return "Lock TCP";
}


QString PluginLockTCP::PluginLoad(QMainWindow *mw, QMenuBar *menubar, QStatusBar *statusbar, RoboDK *rdk, const QString &settings){
    RDK = rdk;
    MainWindow = mw;
    StatusBar = statusbar;

    qDebug() << "Loading plugin " << PluginName();
    qDebug() << "Using settings: " << settings; // reserved for future compatibility

    // it is highly recommended to use the statusbar for debugging purposes (pass /DEBUG as an argument to see debug result in RoboDK)
    qDebug() << "Setting up the status bar";
    StatusBar->showMessage(tr("RoboDK Plugin %1 is being loaded").arg(PluginName()));

    // Here you can add all the "Actions": these actions are callbacks from buttons selected from the menu or the toolbar
    action_lock = new QAction(tr("Lock TCP"));
    action_lock->setCheckable(true);

    // Make sure to connect the action to your callback (slot)
    connect(action_lock, SIGNAL(triggered(bool)), this, SLOT(callback_tcp_lock(bool)));

    // return string is reserverd for future compatibility
    return "";
}


void PluginLockTCP::PluginUnload(){
    last_clicked_item = nullptr;
    locked_items.clear();

    if (nullptr != action_lock)
    {
        disconnect(action_lock, SIGNAL(triggered(bool)), this, SLOT(callback_tcp_lock(bool)));
        delete action_lock;
        action_lock = nullptr;
    }
}


bool PluginLockTCP::PluginItemClick(Item item, QMenu *menu, TypeClick click_type){
    if (click_type != ClickRight){
        return false;
    }

    if (process_item(item)){
        // Find the current state of this item
        bool locked = false;
        for (const auto& locked_item : locked_items){
            if (locked_item.robot == last_clicked_item){
                locked = locked_item.locked;
                break;
            }
        }

        // Create the menu option, or update if it already exist
        menu->addSeparator();
        action_lock->blockSignals(true);
        action_lock->setChecked(locked);
        action_lock->blockSignals(false);
        menu->addAction(action_lock);

        return true;
    }

    return false;
}

QString PluginLockTCP::PluginCommand(const QString &command, const QString &item_name){
    Item item = RDK->getItem(item_name);
    if (item == nullptr){
        return "ITEM NOT FOUND";
    }

     if (!process_item(item)){
         return "ITEM INVALID";
     }

    callback_tcp_lock(command.compare("Lock", Qt::CaseInsensitive) == 0);
    return "OK";
}

void PluginLockTCP::PluginEvent(TypeEvent event_type){
    switch (event_type){
    case EventChanged:{
        // Check if any locked TCPs were removed
        for (auto it = locked_items.begin(); it != locked_items.end(); it++){
            locked_item_t l_item = *it;
            if (!RDK->Valid(l_item.robot)){
                // here, l_item.robot is not accessible anymore
                qDebug() << "Deleting TCP lock for robot";
                locked_items.erase(it--);
            }
        }

        break;
    }
    case EventMoved:
        // Update the pose of locked TCPs
        update_tcp_pose();
        break;
    default:
        break;

    }
}

//----------------------------------------------------------------------------------
bool PluginLockTCP::process_item(Item item){
    if (item == nullptr){
        return false;
    }

    // Check if we right clicked a tool and get the robot pointer instead
    if (item->Type() == IItem::ITEM_TYPE_TOOL){
        item = item->Parent();
    }

    // Check if we selected a robot or an item attached to a robot
    if (item->Type() == IItem::ITEM_TYPE_ROBOT){

        // Get the parent robot, this will always return the pointer to the 6 axis robot, or the robot itself
        Item robot_item = item->getLink(IItem::ITEM_TYPE_ROBOT);

        if (robot_item->Joints().Length() >= 7){ // 6 axis + 1 external axis or more

            // Add this combination to the list of possible locked TCPs
            bool exist = false;
            for (const auto& locked_item : locked_items){
                if (locked_item.robot == robot_item){
                    exist = true;
                    break;
                }
            }

            if (!exist){
                locked_item_t new_item;
                new_item.robot = robot_item;
                new_item.pose = Mat();
                new_item.last_jnts = tJoints();
                new_item.locked = false;
                locked_items.append(new_item);
            }

            last_clicked_item = robot_item;
            return true;
        }
    }
    return false;
}

void PluginLockTCP::update_tcp_pose(){
    bool renderUpdate = false;
    for (auto& locked_item : locked_items){
        if (locked_item.locked){
            Mat robot_pose = locked_item.robot->Parent()->PoseAbs().inv() * locked_item.pose;
            tJoints jnew = locked_item.robot->SolveIK(robot_pose);

            // Out of reach, fully extended
            if (jnew.Length() == 0){
                locked_item.robot->setJoints(locked_item.last_jnts);
                renderUpdate = true;
                continue;
            }

            // Joints config changed
            tConfig new_config;
            locked_item.robot->JointsConfig(jnew, new_config);
            tConfig prev_config;
            locked_item.robot->JointsConfig(locked_item.last_jnts, prev_config);
            for (int i = 0; i < RDK_SIZE_MAX_CONFIG; ++i){
                if (std::abs(new_config[i] - prev_config[i]) > 10e-10){
                    locked_item.robot->setJoints(locked_item.last_jnts);
                    renderUpdate = true;
                    continue;
                }
            }

            locked_item.robot->setJoints(jnew);
            locked_item.robot->setPoseAbs(locked_item.pose);
            locked_item.last_jnts = locked_item.robot->Joints();
            renderUpdate = true;
        }
    }

    if (renderUpdate){
        RDK->Render(RoboDK::RenderUpdateOnly);
    }
}

void PluginLockTCP::callback_tcp_lock(bool lock){
    if (last_clicked_item == nullptr){
        return;
    }

    for (auto& l_item : locked_items){
        if (l_item.robot == last_clicked_item){
            l_item.locked = lock;
            l_item.pose = l_item.robot->Parent()->PoseAbs() * l_item.robot->SolveFK(l_item.robot->Joints());
            l_item.last_jnts = l_item.robot->Joints();
        }
    }
}

