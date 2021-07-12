#include "PluginLockTCP.h"

#include <QAction>
#include <QStatusBar>
#include <QMenuBar>


//------------------------------- RoboDK Plug-in commands ------------------------------

QString PluginLockTCP::PluginName(){
    return "Lock TCP Plugin";
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
    locked_items.clear();

    disconnect(action_lock, SIGNAL(triggered(bool)), this, SLOT(callback_tcp_lock(bool)));
    delete action_lock;
    action_lock = nullptr;
}


bool PluginLockTCP::PluginItemClick(Item item, QMenu *menu, TypeClick click_type){

    // Ensure this is a tool attached to a 6 dof robot, mounted on a synchronized external axis
    if (item->Type() == IItem::ITEM_TYPE_TOOL){
        Item robot_item = item->Parent();

        if (RDK->Valid(robot_item) && (robot_item->Type() == IItem::ITEM_TYPE_ROBOT)){
            if (robot_item->Joints().Length() == 7){ // 6 axis + 1 external axis.

                this->last_clicked_item = item;
                menu->addSeparator();
                menu->addAction(action_lock);

                // Add this combination to the list of possible locked TCPs
                bool exist = false;
                for (const auto& locked_item : locked_items){
                    if ((locked_item.robot == robot_item) && (locked_item.tool == item)){
                        exist = true;
                        break;
                    }
                }

                if (!exist){
                    locked_item_t new_item;
                    new_item.robot = robot_item;
                    new_item.tool = item;
                    new_item.pose = item->PoseAbs();
                    new_item.locked = false;
                    locked_items.append(new_item);
                }

                return true;
            }
        }
    }
    return false;
}

QString PluginLockTCP::PluginCommand(const QString &command, const QString &value){

    // Get the item by it's name
    Item tool_item = RDK->getItem(value, IItem::ITEM_TYPE_TOOL);
    if ((tool_item == nullptr) || (tool_item->Name() != value)){
        qDebug() << "Invalid tool item name: " << value;
        return "INVALID_NAME";
    }

    // Update the status
    last_clicked_item = tool_item;
    callback_tcp_lock(command.compare("Lock", Qt::CaseInsensitive) == 0);
    return "Done";
}



void PluginLockTCP::PluginEvent(TypeEvent event_type){
    switch (event_type){
    case EventChanged:{
        // Check if any locked TCPs were removed
        for (auto it = locked_items.begin(); it != locked_items.end(); it++){
            locked_item_t l_item = *it;
            if (!RDK->Valid(l_item.robot) || !RDK->Valid(l_item.tool)){
                qDebug() << "Deleting TCP lock: " << l_item.tool->Name();
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
void PluginLockTCP::update_tcp_pose(){
    bool renderUpdate = false;
    for (auto& locked_item : locked_items){
        if (locked_item.locked){
            Mat robot_pose = locked_item.robot->Parent()->PoseAbs().inv() * locked_item.pose;
            tJoints jnew = locked_item.robot->SolveIK(robot_pose);

            if (jnew.Length() == 0){
                continue;
            }

            locked_item.robot->setJoints(jnew);
            locked_item.robot->setPoseAbs(locked_item.pose);
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
        if (l_item.tool == last_clicked_item){
            l_item.locked = lock;
            l_item.pose = l_item.robot->Parent()->PoseAbs() * l_item.robot->SolveFK(l_item.robot->Joints());
        }
    }
}

