#ifndef PLUGINEXAMPLE_H
#define PLUGINEXAMPLE_H


#include <QObject>
#include <QtPlugin>
#include <QDockWidget>
#include "iapprobodk.h"
#include "robodktypes.h"


#include <QTimer>
#include <QElapsedTimer>




class QToolBar;
class QMenu;
class QAction;
class IRoboDK;
class IItem;
class FormRobotPilot;

///
/// \brief The PluginLVDT class allows you to simulate a linear gage (such as an LVDT).
///        It maps the TCP of a robot to the displacement of the linear gage.
///
class PluginLVDT : public QObject, IAppRoboDK
{
    Q_OBJECT
    Q_PLUGIN_METADATA(IID "RoboDK.IAppRoboDK")// FILE "metadatalugin.json")
    Q_INTERFACES(IAppRoboDK)

public:
    //------------------------------- RoboDK Plug-in Interface commands ------------------------------

    PluginLVDT();

    QString PluginName(void) override;    
    virtual QString PluginLoad(QMainWindow *mw, QMenuBar *menubar, QStatusBar *statusbar, RoboDK *rdk, const QString &settings="") override;
    virtual void PluginUnload() override;
    virtual void PluginLoadToolbar(QMainWindow *mw, int icon_size) override;
    virtual bool PluginItemClick(Item item, QMenu *menu, TypeClick click_type) override;
    virtual QString PluginCommand(const QString &command, const QString &value) override;
    virtual void PluginEvent(TypeEvent event_type) override;

    //----------------------------------------------------------------------------------

    // Recommended pointers to use in your plugin:
public:
    /// RoboDK's <strong>main window</strong> pointer.
    QMainWindow *MainWindow { nullptr };

    /// RoboDK's main <strong>status bar</strong> pointer.
    QStatusBar *StatusBar { nullptr };

    /// Pointer to the <strong>RoboDK API</strong> interface.
    RoboDK *RDK { nullptr };


public slots:
    /// define button callbacks (or slots) here. They are triggered automatically when the button is selected.
    void callback_mechanism_active(bool active);

public:

    /// Get a list of LVDT candidate in the station
    QList<Item> getLvdtList();

    /// Process/validates an item candidate. Returns true if it succeeds, else false.
    bool processItem(Item item);

    /// Update the poses of LVDTs
    void updateLvdts();

    /// Remove deleted or invalid LVDTs
    void cleanupRemovedItems();


private:

    /// Activate an LVDT
    QAction *action_active { nullptr };

    /// Data structure of a LVDT
    struct lvdt_data_t
    {
        bool active { false };
        float radius { 12.5f };
        Item mechanism { nullptr };
        Item station { nullptr };
    };

    /// Vector of all available LVDT
    QList<lvdt_data_t> lvdts;

    /// Last clicked item --or item to attach to
    Item last_clicked_item { nullptr };


};
//! [0]


#endif // PLUGINEXAMPLE_H
