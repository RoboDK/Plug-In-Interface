#ifndef PLUGINEXAMPLE_H
#define PLUGINEXAMPLE_H


#include <QObject>
#include <QtPlugin>
#include <QDockWidget>
#include "iapprobodk.h"
#include "robodktypes.h"
#include <QTimer>



class QToolBar;
class QMenu;
class QAction;
class IRoboDK;
class IItem;
class FormRobotPilot;


class PluginExample : public QObject, IAppRoboDK
{
    Q_OBJECT
    Q_PLUGIN_METADATA(IID "RoboDK.IAppRoboDK")// FILE "metadatalugin.json")
    Q_INTERFACES(IAppRoboDK)

public:
    //------------------------------- RoboDK Plug-in Interface commands ------------------------------

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
    QMainWindow *MainWindow;  // Main window
    QStatusBar *StatusBar;    // Status bar
    RoboDK *RDK;              // Pointer to RoboDK API (fast API)

public slots:
    // define button callbacks (or slots) here. They are triggered automatically when the button is selected.

    ///
    /// \brief Called when the information button/action is selected
    ///
    void callback_information();

    ///
    /// \brief Called when the robot pilot button/action is selected
    ///
    void callback_robotpilot();

    ///
    /// \brief Called when the robot pilot window is closed (event triggered by the dock window)
    ///
    void callback_robotpilot_closed();

    ///
    /// \brief Called when the user select the button/action for help
    ///
    void callback_help();


    void callback_realtime(bool realtime);

    void callback_realtime_process();

private:
    // define your actions: usually, one action per button
    QToolBar *toolbar1;
    QToolBar *toolbar2;
    QMenu *menu1;
    QAction *action_information;
    QAction *action_robotpilot;
    QAction *action_help;
    QAction *action_realtime;
    QDockWidget *dock_robotpilot;
    FormRobotPilot *form_robotpilot;
    QTimer timer_realtime;

    //Item Robot;
    QList<Item> RobotList;
};
//! [0]


#endif // PLUGINEXAMPLE_H
