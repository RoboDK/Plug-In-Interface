#ifndef PLUGINBALLBARTRACKER_H
#define PLUGINBALLBARTRACKER_H


#include "iapprobodk.h"

class QAction;

///
/// \brief The PluginBallbarTracker allows you to attach a ballbar to a robot TCP.
///        A ballbar is statically attached to a base, and it's end can extend and rotate to follow the TCP.
///
class PluginBallbarTracker : public QObject, IAppRoboDK
{
    Q_OBJECT
    Q_PLUGIN_METADATA(IID "RoboDK.IAppRoboDK")// FILE "metadatalugin.json")
    Q_INTERFACES(IAppRoboDK)

public:
    //------------------------------- RoboDK Plug-in Interface commands ------------------------------

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
    // define button callbacks (or slots) here. They are triggered automatically when the button is selected.

    /// Called when the attach ballbar button/action is selected
    void callback_attach_ballbar(bool attach);

public:
    /// Process an item. Returns true if it succeeds, else false.
    bool process_item(Item item);

    /// Update the pose of all attached ballbars
    void update_ballbar_pose();


private:

    /// Attach/detach action. callback_attach_ballbar is triggered with this action.  Actions are required to populate toolbars and menus and allows getting callbacks.
    QAction *action_attach;

    /// Data structure of an attached ballbar
    struct attached_ballbar_t
    {
        bool attached { false };
        bool reachable { false };
        Item robot { nullptr };
        Item ballbar_end_frame { nullptr };
        Item ballbar_center_frame { nullptr };
        Item ballbar_orbit_mech { nullptr };
        Item ballbar_extend_mech { nullptr };

        void detach(){
            attached = false;
            reachable = false;
            robot = nullptr;
            ballbar_end_frame = nullptr;
            ballbar_center_frame = nullptr;
            ballbar_orbit_mech = nullptr;
            ballbar_extend_mech = nullptr;
        }
    };

    /// Vector of all available attached ballbars
    QList<attached_ballbar_t> attached_ballbars;

    /// Last clicked item --or item to attach to
    Item last_clicked_item { nullptr };

};


#endif // PLUGINBALLBARTRACKER_H
