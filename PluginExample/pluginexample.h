#ifndef PLUGINEXAMPLE_H
#define PLUGINEXAMPLE_H


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
class FormRobotPilot;

///
/// \brief The PluginExample class shows the structure of a RoboDK plugin.
/// A RoboDK plugin must implement the IAppRoboDK and the QObject class.
///
/// \image html robodk-plugin-example.png
///
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
    /// RoboDK's <strong>main window</strong> pointer.
    QMainWindow *MainWindow;

    /// RoboDK's main <strong>status bar</strong> pointer.
    QStatusBar *StatusBar;

    /// Pointer to the <strong>RoboDK API</strong> interface.
    RoboDK *RDK;

public slots:
    // define button callbacks (or slots) here. They are triggered automatically when the button is selected.

    /// Called when the information button/action is selected
    void callback_information();

    /// Called when the robot pilot button/action is selected
    void callback_robotpilot();

    /// Called when the robot pilot window is closed (event triggered by the dock window)
    void callback_robotpilot_closed();

    /// Called when the user select the button/action for help
    void callback_help();

// define your actions: usually, one action per button
private:
    /// Pointer to the customized toolbar
    QToolBar *toolbar1;

    /// Pointer to the customized menu
    QMenu *menu1;

    /// Information action. callback_information is triggered with this action. Actions are required to populate toolbars and menus and allows getting callbacks.
    QAction *action_information;

    /// Open robot pilot form action. callback_robotpilot is triggered with this action. Actions are required to populate toolbars and menus and allows getting callbacks.
    QAction *action_robotpilot;

    /// Open help action. callback_help is triggered with this action. Actions are required to populate toolbars and menus and allows getting callbacks.
    QAction *action_help;

    /// Pointer to the docked window.
    QDockWidget *dock_robotpilot;

    /// Pointer to the robot pilot form.
    FormRobotPilot *form_robotpilot;
};
//! [0]


#endif // PLUGINEXAMPLE_H
