#ifndef PLUGINCOLLISIONSENSOR_H
#define PLUGINCOLLISIONSENSOR_H


#include <QObject>
#include <QtPlugin>
#include <QDockWidget>
#include "iapprobodk.h"
#include "robodktypes.h"


class QToolBar;
class QMenu;
class QAction;
class IRoboDK;
class IItem;


///
/// \brief The PluginCollisionSensor class allows you to simulate sensors, such as a laser sensors or contact switches.
///        It uses collision detection between a sensor and its environnement to update a station parameter.
///
class PluginCollisionSensor : public QObject, IAppRoboDK
{
    Q_OBJECT
    Q_PLUGIN_METADATA(IID "RoboDK.IAppRoboDK")// FILE "metadatalugin.json")
    Q_INTERFACES(IAppRoboDK)

public:
    //------------------------------- RoboDK Plug-in Interface commands ------------------------------

    PluginCollisionSensor();

    QString PluginName(void) override;
    virtual QString PluginLoad(QMainWindow *mw, QMenuBar *menubar, QStatusBar *statusbar, RoboDK *rdk, const QString &settings = "") override;
    virtual void PluginUnload() override;
    virtual bool PluginItemClick(Item item, QMenu *menu, TypeClick click_type) override;
    virtual QString PluginCommand(const QString &command, const QString &value) override;
    virtual void PluginEvent(TypeEvent event_type) override;

    //----------------------------------------------------------------------------------

public:
    /// RoboDK's <strong>main window</strong> pointer.
    QMainWindow *MainWindow { nullptr };

    /// RoboDK's main <strong>status bar</strong> pointer.
    QStatusBar *StatusBar { nullptr };

    /// Pointer to the <strong>RoboDK API</strong> interface.
    RoboDK *RDK { nullptr };


public slots:

    /// Callback to set the lact clicked Item as a Sensor
    void callback_set_as_sensor(bool active);

public:

    /// Process/validates an item candidate. Returns true if it succeeds, else false.
    bool processItem(Item item);

    /// Remove deleted or invalid Items
    void cleanupRemovedItems();

    /// Update sensor statuses
    void updateSensors();

private:

    /// Action to set the selected Item as a Sensor
    QAction *action_set_as_sensor { nullptr };

    struct sensor_t
    {
        Item sensor { nullptr };
        Item station { nullptr };
    };

    QList<sensor_t> sensors;

    Item last_clicked_item { nullptr };

};
//! [0]


#endif // PLUGINCOLLISIONSENSOR_H
