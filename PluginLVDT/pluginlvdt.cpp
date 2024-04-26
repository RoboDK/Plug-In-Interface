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

#include "pluginlvdt.h"

#include "robodk_interface.h"
#include "iitem.h"


//------------------------------- RoboDK Plug-in commands ------------------------------

PluginLVDT::PluginLVDT(){
}


QString PluginLVDT::PluginName(){
    return "Plugin LVDT";
}


QString PluginLVDT::PluginLoad(QMainWindow *mw, QMenuBar *menubar, QStatusBar *statusbar, RoboDK *rdk, const QString &settings){
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
    action_active = new QAction(tr("Activate LVDT simulation"));
    action_active->setCheckable(true);

    // Make sure to connect the action to your callback (slot)
    connect(action_active, SIGNAL(triggered(bool)), this, SLOT(callback_mechanism_active(bool)));

    // return string is reserverd for future compatibility
    return "";
}


void PluginLVDT::PluginUnload(){
    // Cleanup the plugin
    qDebug() << "Unloading plugin " << PluginName();

    last_clicked_item = nullptr;
    lvdts.clear();

    if (nullptr != action_active)
    {
        action_active->deleteLater();
        action_active = nullptr;
    }
}


void PluginLVDT::PluginLoadToolbar(QMainWindow *mw, int icon_size){
    Q_UNUSED(mw)
    Q_UNUSED(icon_size)
}


bool PluginLVDT::PluginItemClick(Item item, QMenu *menu, TypeClick click_type){
    qDebug() << "Selected item: " << item->Name() << " of type " << item->Type() << " click type: " << click_type;

    last_clicked_item = nullptr;

    if (click_type != ClickRight){
        return false;
    }

    if (processItem(item)){
        last_clicked_item = item;

        // Find the current state of this item
        bool active = false;
        for (const auto &lvdt : lvdts){
            if (lvdt.mechanism == last_clicked_item){
                active = lvdt.active;
                break;
            }
        }

        // Create the menu option, or update if it already exist
        menu->addSeparator();
        action_active->blockSignals(true);
        action_active->setChecked(active);
        action_active->blockSignals(false);
        menu->addAction(action_active);

        return true;
    }

    return false;
}


QString PluginLVDT::PluginCommand(const QString &command, const QString &value){
    qDebug() << "Sent command: " << command << "    With value: " << value;
    return "";
}


void PluginLVDT::PluginEvent(TypeEvent event_type){
    switch (event_type) {
    case EventChangedStation:
    case EventChanged:
    {
        cleanupRemovedItems();
        updateLvdts(); // If a robot/tool was removed, we might need to reset an LVDT
        break;
    }
    case EventMoved:
        updateLvdts();
        break;
    default:
        break;

    }
}


//----------------------------------------------------------------------------------
// Define your own button callbacks here (and other slots)

void PluginLVDT::callback_mechanism_active(bool activate){
    if (last_clicked_item == nullptr){
        return;
    }

    if (!activate){
        QMutableListIterator<lvdt_data_t> i(lvdts);
        while (i.hasNext()) {
            if (i.next().mechanism == last_clicked_item){
                i.remove();
            }
        }
        return;
    }

    lvdt_data_t lvdt;
    lvdt.mechanism = last_clicked_item;
    lvdt.station = RDK->getActiveStation();
    lvdt.active = true;

    bool isok;
    double value = QInputDialog::getDouble(nullptr, tr("Enter contact radius"), tr("Enter contact/surface radius for the LVDT (mm)"), lvdt.radius, 0.0, 999.9, 3, &isok);
    if (isok){
        lvdt.radius = value;
        RDK->Render(RoboDK::RenderComplete);
    }

    lvdts.append(lvdt);
    qDebug() << "Starting mechanism simulation for " << lvdt.mechanism->Name();
}


//----------------------------------------------------------------------------------
QList<Item> PluginLVDT::getLvdtList() {
    QList<Item> lvdts;

    for (const auto& lvdt : RDK->getItemList(IItem::ITEM_TYPE_ROBOT_AXES)){
        if (lvdt->getLink(IItem::ITEM_TYPE_ROBOT) != lvdt){
            // this axis is part of a multi axis system
            continue;
        }
        if (lvdt->Joints().Length() != 1){
            // this is not a 1 DOF axis
            continue;
        }
        lvdts.append(lvdt);
    }

    return lvdts;
}


bool PluginLVDT::processItem(Item item){
    if (item == nullptr){
        return false;
    }

    // User can right-click a robot, a TCP or a mechanism with 1 DOF

    // Check if there is a LVDT candidate in the station
    QList<Item> lvdts = getLvdtList();
    if (lvdts.isEmpty()){
        return false;
    }

    // Check if we right-clicked an LVDT
    if (lvdts.contains(item)) {
        qDebug() << "Found valid mechanism: " << item->Name();
        return true;
    }
    return false;
}


void PluginLVDT::updateLvdts(){
    if (lvdts.empty()){
        return;
    }

    QList<Item> tools = RDK->getItemList(IItem::ITEM_TYPE_TOOL);

    for (const auto& lvdt : lvdts){
        Mat poseabs_lvdt = lvdt.mechanism->PoseAbs();

        tJoints lower_limits;
        tJoints upper_limits;
        lvdt.mechanism->JointLimits(&lower_limits, &upper_limits);

        double low = lower_limits.Data()[0];
        double high = upper_limits.Data()[0];
        double new_value = low;

        for (const auto& tool : tools){
            if (!tool->Visible()) {
                continue;
            }

            Mat poseabs_tcp = tool->PoseAbs() * tool->PoseTool();
            Mat tcp_wrt_lvdt = poseabs_lvdt.inv() * poseabs_tcp;

            tXYZ xyz_tcp;
            tcp_wrt_lvdt.Pos(xyz_tcp);
            if ((std::abs(xyz_tcp[0]) > lvdt.radius) || (std::abs(xyz_tcp[1]) > lvdt.radius)){
                // Out of reach in the XY plane
                continue;
            }

            if ((-xyz_tcp[2] < low) || (-xyz_tcp[2] > high)){
                // Out of reach in the Z axis
                continue;
            }

            new_value = std::max(new_value, -xyz_tcp[2]);
        }

        tJoints joints;
        joints.SetValues(&new_value, 1);
        lvdt.mechanism->setJoints(joints);
    }

    // We must force a new update before render (a render is on its way),
    // Keep in mind we are already inside an update operation
    // RoboDK will check for recursivity and prevent it
    RDK->Render(RoboDK::RenderUpdateOnly);
}


void PluginLVDT::cleanupRemovedItems() {
    if (lvdts.empty()){
        return;
    }

    // Check if any active LVDTs were removed
    Item station = RDK->getActiveStation();
    QList<Item> stations = RDK->getOpenStations();
    for (auto it = lvdts.begin(); it != lvdts.end(); ){
        lvdt_data_t lvdt = *it;

        // Remove deleted stations
        if (!stations.contains(lvdt.station)) {
            qDebug() << "Station closed. Removing affected items.";
            it = lvdts.erase(it);
            continue;
        }

        // Remove deleted items from the current station
        // Note: RDK->Valid(item) return false for items in other stations
        if (lvdt.station == station) {
            if (!RDK->Valid(lvdt.mechanism)) {
                qDebug() << "LVDT deleted. Removing affected items.";
                it = lvdts.erase(it);
                continue;
            }
        }
        ++it;
    }
}
