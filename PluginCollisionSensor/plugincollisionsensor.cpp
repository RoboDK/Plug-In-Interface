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
#include <QList>

#include "plugincollisionsensor.h"

#include "robodk_interface.h"
#include "iitem.h"


//------------------------------- RoboDK Plug-in commands ------------------------------

PluginCollisionSensor::PluginCollisionSensor() {}


QString PluginCollisionSensor::PluginName() {
    return "Plugin Collision Sensor";
}


QString PluginCollisionSensor::PluginLoad(QMainWindow *mw, QMenuBar *menubar, QStatusBar *statusbar, RoboDK *rdk, const QString &settings) {
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
    action_set_as_sensor = new QAction(tr("Set as sensor"));
    action_set_as_sensor->setCheckable(true);

    // Make sure to connect the action to your callback (slot)
    connect(action_set_as_sensor, SIGNAL(triggered(bool)), this, SLOT(callback_set_as_sensor(bool)));

    // return string is reserverd for future compatibility
    return "";
}


void PluginCollisionSensor::PluginUnload() {
    // Cleanup the plugin
    qDebug() << "Unloading plugin " << PluginName();

    sensors.clear();
    last_clicked_item = nullptr;

    if (nullptr != action_set_as_sensor) {
        action_set_as_sensor->deleteLater();
        action_set_as_sensor = nullptr;
    }
}


bool PluginCollisionSensor::PluginItemClick(Item item, QMenu *menu, TypeClick click_type) {
    qDebug() << "Selected item: " << item->Name() << " of type " << item->Type() << " click type: " << click_type;

    last_clicked_item = nullptr;

    if (click_type != ClickRight) {
        return false;
    }

    if (processItem(item)) {
        last_clicked_item = item;

        bool active = false;
        for (const auto &sensor : sensors) {
            if (sensor.sensor == last_clicked_item) {
                active = true;
                break;
            }
        }

        // Create the menu option, or update if it already exist
        menu->addSeparator();
        action_set_as_sensor->blockSignals(true);
        action_set_as_sensor->setChecked(active);
        action_set_as_sensor->blockSignals(false);
        menu->addAction(action_set_as_sensor);

        return false;
    }

    return false;
}


QString PluginCollisionSensor::PluginCommand(const QString &command, const QString &value) {

    // Expected format: "Activate", "Sensor Item.Name() or Python's Item.item pointer"
    //                  "Deactivate", "Sensor Item.Name() or Python's Item.item pointer"

    last_clicked_item = nullptr;

    bool activate = true;
    if (command.compare("Activate", Qt::CaseInsensitive) == 0) {
        activate = true;
    } else if (command.compare("Deactivate", Qt::CaseInsensitive) == 0) {
        activate = false;
    } else {
        return "Unknown Command";
    }

    Item candidate = nullptr;

    // Passing by pointer
    bool is_pointer;
    qulonglong item_ptr = value.toULongLong(&is_pointer);
    if (is_pointer) {
        candidate = reinterpret_cast<Item>(item_ptr + QT_POINTER_SIZE * 8);
        if (!RDK->Valid(candidate)) {
            candidate = nullptr;
        }
    }

    // Passing by name
    if (candidate == nullptr) {
        candidate = RDK->getItem(value);
    }

    if (!processItem(candidate)) {
        return "Invalid Item";
    }

    last_clicked_item = candidate;
    callback_set_as_sensor(activate);
    return "OK";
}


void PluginCollisionSensor::PluginEvent(TypeEvent event_type) {
    switch (event_type) {
    case EventChangedStation:
    case EventChanged:
    {
        cleanupRemovedItems();
        break;
    }
    case EventRender:
        updateSensors();
        break;
    default:
        break;

    }
}

//------------------------------- Plug-in commands ------------------------------

void PluginCollisionSensor::callback_set_as_sensor(bool activate) {
    if (last_clicked_item == nullptr) {
        return;
    }

    // Request to deactivate
    if (!activate) {
        QMutableListIterator<sensor_t> i(sensors);
        while (i.hasNext()) {
            if (i.next().sensor == last_clicked_item) {
                i.remove();
            }
        }
        return;
    }

    // Request to activate
    sensor_t sensor;
    sensor.sensor = last_clicked_item;
    sensor.station = RDK->getActiveStation();
    sensors.append(sensor);
}


bool PluginCollisionSensor::processItem(Item item) {
    if (item == nullptr) {
        return false;
    }

    if (!RDK->Valid(item)) {
        return false;
    }

    if (QList<int>({ IItem::ITEM_TYPE_OBJECT }).contains(item->Type())) {
        return true;
    }
    return false;
}


void PluginCollisionSensor::updateSensors() {

    QList<Item> objects = RDK->getItemList(IItem::ITEM_TYPE_OBJECT);

    for (const auto &sensor : sensors) {
        QString status = "0";
        for (const auto &object : objects) {
            if (sensor.sensor == object) {
                continue;
            }

            if (RDK->Collision(sensor.sensor, object)) {
                qDebug() << sensor.sensor->Name() << " is sensing " << object->Name();
                status = "1";
                break;
            }
        }
        RDK->setParam(sensor.sensor->Name(), status);
    }
}


void PluginCollisionSensor::cleanupRemovedItems() {

    if (sensors.empty()) {
        return;
    }

    Item station = RDK->getActiveStation();
    QList<Item> stations = RDK->getOpenStations();
    for (auto it = sensors.begin(); it != sensors.end(); ) {
        sensor_t sensor = *it;

        // Remove deleted stations
        if (!stations.contains(sensor.station)) {
            qDebug() << "Station closed. Removing affected items.";
            it = sensors.erase(it);
            continue;
        }

        // Remove deleted items from the current station
        // Note: RDK->Valid(item) return false for items in other stations
        if (sensor.station == station) {
            if (!RDK->Valid(sensor.sensor)) {
                qDebug() << "Item deleted. Removing affected items.";
                it = sensors.erase(it);
                continue;
            }
        }
        ++it;
    }
}
