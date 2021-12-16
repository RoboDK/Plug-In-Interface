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
/// \brief The PluginPartAttached allow attaching one or more objects to one or more robot links.
///
class PluginPartAttached : public QObject, IAppRoboDK
{
    Q_OBJECT
    Q_PLUGIN_METADATA(IID "RoboDK.IAppRoboDK")// FILE "metadatalugin.json")
    Q_INTERFACES(IAppRoboDK)

public:
    //------------------------------- RoboDK Plug-in Interface commands ------------------------------

    PluginPartAttached();

    ///
    /// @brief Return the plugin name. Try to be creative and make sure the name is unique.
    QString PluginName(void) override;

    ///
    /// \brief Load the plugin. This function is called only once when the plugin is loaded (or RoboDK is started with the plugin).
    /// \param mw RoboDK's QMainwindow. Use this object to add menus in the main window.
    /// \param menubar Pointer to RoboDK's main menu bar
    /// \param statusbar Pointer to RoboDK's main status bar
    /// \param statusbar Pointer RoboDK's interface (implementation of the RoboDK API): \ref IRoboDK and \ref IItem
    /// \param settings Additional settings (reserved for future compatibility)
    virtual QString PluginLoad(QMainWindow *mw, QMenuBar *menubar, QStatusBar *statusbar, RoboDK *rdk, const QString &settings = "") override;

    ///
    /// \brief This function is called once only when the plugin is being unloaded.
    // It is recommended to remove the toolbar and menus that were added by the plugin. It will help during de debugging process.
    virtual void PluginUnload() override;

    ///
    /// \brief This function is called every time the toolbar is set up. This function is called at least once right after \ref PluginLoad and it can be called when the user changes the view settings (such as changing from cinema to normal mode) or changes the default toolbar layout (in Tools-Toolbar Layout)
    /// \param mw Pointer to RoboDK's main window.
    /// \param iconsize Size of the toolbar icons. The size may differ depending on the screen's DPI. It can also be set in Tools-Options-Display menu.
    //virtual void PluginLoadToolbar(QMainWindow *mw, int icon_size) override;

    ///
    /// \brief This function is called every time a new context menu is created for an item.
    /// \param item The Item (\ref IItem) clicked
    /// \param menu Pointer to the context menu
    /// \param click_type Click type (usually left click)
    /// \return
    virtual bool PluginItemClick(Item item, QMenu *menu, TypeClick click_type) override;

    ///
    /// \brief Specific commands can be passed from the RoboDK API. For example, a parent application can rely on a plugin for certain operations (for example, to create native windows within RoboDK application or take advantage of the RoboDK API speed within the plugin).
    /// Use the RoboDK API (PluginCommand(plugin_name, command, value) to send specific commands to your plugin from an external application.
    /// \param command
    /// \param value
    /// \return
    virtual QString PluginCommand(const QString &command, const QString &value) override;

    ///
    /// \brief This function is called every time there is a new RoboDK event such as rendering the screen, adding/removing items or changing the active station.
    /// If event_type is \ref EventRender you can render your own graphics here using IRoboDK::DrawGeometry.
    // Make sure to make this code as fast as possible to not provoke render lags
    /// \param event_type type of event (EventRender, EventMoved, EventChanged)
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

    /// Called when the attach objects to robot is clicked
    void callback_robot_select_attach();

    /// Called when the detach objects from robot is clicked
    void callback_robot_select_detach();

    /// Called when the detach all objects from robot is clicked
    void callback_robot_detach_all();

    /// Called when the attach object to robot is clicked
    void callback_object_select_attach();

    /// Called when the detach object from robots is clicked
    void callback_objet_detach_all();


public:

    /// Checks if an objects is attached to a parent
    bool isAttached(Item object);

    /// Checks if a parent has attached objects
    bool hasObjects(Item parent);

    /// Get the objects attached to a parent
    QList<Item> attachedObjects(Item parent);

    /// Process an item. Returns true if it succeeds, else false.
    bool validItem(Item item);

    /// Update event
    void updatePoses();

    /// Get the pose of the moving frame we want
    Mat getCustomPose(Item item, int joint_id);


    // define your actions: usually, one action per button
private:

    /// Menu to select objects to attach to the ROBOT
    QAction *action_robot_select_attach;

    /// Menu to select objects to detach from the ROBOT
    QAction *action_robot_select_detach;

    /// Menu to detach all objects from the ROBOT
    QAction *action_robot_detach_all;

    /// Menu to select the robot to attach the OBJECT to
    QAction *action_object_select_attach;

    /// Menu to detach an OBJECT from all robots
    QAction *action_objet_detach_all;

    /// Data structure of an attached object
    struct attached_object_t
    {
        int joint_id { -1 }; // Parent joint the object is attached to
        Item parent { nullptr }; // Parent to which the object is attached (robot, external axis, etc)
        Item object { nullptr }; // The object itself
        Mat pose; // Initial object pose when attached
    };

    /// Vector of all available attached objects
    QVector<attached_object_t> attached_objects;

    /// Last clicked item
    Item last_clicked_item { nullptr };

};


#endif // PLUGINEXAMPLE_H
