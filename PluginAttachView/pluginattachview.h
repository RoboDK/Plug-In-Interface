#ifndef PLUGINATTACHVIEW_H
#define PLUGINATTACHVIEW_H


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
/// \brief The PluginAttachView class allows you to attach a Camera to an Item and vice-versa.
///
class PluginAttachView : public QObject, IAppRoboDK
{
    Q_OBJECT
    Q_PLUGIN_METADATA(IID "RoboDK.IAppRoboDK")// FILE "metadatalugin.json")
    Q_INTERFACES(IAppRoboDK)

public:
    //------------------------------- RoboDK Plug-in Interface commands ------------------------------

    PluginAttachView();

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
    void callback_activate_slave_view_to_anchor(bool active);
    void callback_activate_slave_anchor_to_view(bool active);

public:

    /// Process/validates an item candidate. Returns true if it succeeds, else false.
    bool processItem(Item item);

    /// Update the pose of the 3D View using the anchor
    void updateViewPose();

    /// Update the pose of the anchor using the 3D View
    void updateAnchorPose();

    /// Update the pose of the master anchor (view or anchor)
    void updatePose();

    /// Remove deleted or invalid Items
    void cleanupRemovedItems();


private:

    QAction *action_slave_view_to_anchor { nullptr };
    QAction *action_slave_anchor_to_view { nullptr };

    struct view_anchor_t
    {
        bool is_master { false }; // True if the view updates the anchor, else the anchor updates the view
        Item anchor { nullptr };
        Item station { nullptr };

        void clear(){
            is_master = false;
            anchor = nullptr;
            station = nullptr;
        }
    };

    view_anchor_t view_anchor;

    Item last_clicked_item { nullptr };


};
//! [0]


#endif // PLUGINATTACHVIEW_H
