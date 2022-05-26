#ifndef APPLOADER_H
#define APPLOADER_H


#include <QObject>
#include <QtPlugin>
#include <QDockWidget>
#include "iapprobodk.h"
#include "robodktypes.h"

class QToolBar;
class QMenu;
class QAction;
class QProcess;

class IRoboDK;
class IItem;

class DialogAppList;

class tAppMenu;



/// Hold information related to an action for sorting purposes
class tAppAction {
public:
    tAppAction(QAction *action, double priority, tAppMenu *app, QList<int> rightclick_types={}, QList<int> doubleclick_types={}):
        Priority(priority),
        TypesShowOnContextMenu(rightclick_types),
        TypesDoubleClick(doubleclick_types),
        AppMenu(app)
    {
        Action = action;
    }
    QAction *Action;
    double Priority;
    QList<int> TypesShowOnContextMenu;
    QList<int> TypesDoubleClick;
    tAppMenu *AppMenu;
};

/// Hold the information related to toolbars for sorting purposes
class tAppToolbar {
public:
    tAppToolbar(const QString &name, double priority, int area, double szratio, bool active):
        Name(name),
        Priority(priority),
        ToolbarArea(area),
        SizeRatio(szratio),
        Active(active)
    {

    }
    QString Name;
    double Priority;
    QList<QAction*> Actions;
    int ToolbarArea;
    double SizeRatio;
    bool Active;
};

/// Hold the information related to an App (menu) for sorting purposes
class tAppMenu {
public:
    tAppMenu(const QString &name, const QString &parentMenu, double priority,  bool visible, bool active, const QString &apppath, const QString &inipath):
        Name(name),
        ParentMenu(parentMenu),
        Priority(priority),
        Visible(visible),
        Active(active),
        NamePath(apppath),
        IniPath(inipath),
        Toolbar(nullptr)
    {

    }
    bool Active;
    bool Visible;
    QString Name;
    QString ParentMenu;
    QString NamePath;
    QString IniPath;
    double Priority;
    QList<QAction*> Actions;
    tAppToolbar *Toolbar;
};




///
/// \brief The AppLoader plugin allows you to place multiple scripts inside the Apps folder as if they were plugins.
/// Make sure to create a sub folder in this Apps folder. Each sub folder will be a new toolbar and a new menu entry.
///
/// \image html robodk-plugin-example.png
///
class AppLoader : public QObject, IAppRoboDK
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
    virtual bool PluginItemClickMulti(QList<Item> &item_list, QMenu *menu, TypeClick click_type) override;
    virtual QString PluginCommand(const QString &command, const QString &value) override;
    virtual void PluginEvent(TypeEvent event_type) override;

    //----------------------------------------------------------------------------------
    friend class DialogAppList;

public:
    /// Reload all apps
    void AppsReload();

    /// Unload and delete all apps (cleanup)
    void AppsDelete();

    /// Look for apps in the Apps folder
    void AppsSearch(bool install_requirements=false);

    /// Retrieve all apps and load them in the main menu
    void AppsLoadMenus();

    /// Reload the toolbar
    void AppsLoadToolbars();

    /// Remove all apps
    void AppsUnloadMenus();

    /// remove all toolbars
    void AppsUnloadToolbars();

    /// Run Python code from Qt
    //bool RunPythonShell(const QString &python_exec, const QString &python_code);

// Recommended pointers to use in your plugin:
public:
    /// RoboDK's <strong>main window</strong> pointer.
    QMainWindow *MainWindow;

    /// Pointer to the main menu bar
    QMenuBar *MenuBar;

    /// RoboDK's main <strong>status bar</strong> pointer.
    QStatusBar *StatusBar;

    /// Pointer to the <strong>RoboDK API</strong> interface.
    RoboDK *RDK;

    int IconSize;

public slots:
    // define button callbacks (or slots) here. They are triggered automatically when the button is selected.

    /// Called when we select Tools-App List
    void callback_AppList();

    /// Called when the user select the button/action for help
    void callback_help();

    /// Called when we execute an action related to a script
    void onRunScript();

    /// Called when the script completes
    void onScriptFinished();

    /// Called on app output (eg: print to stdout/default)
    void onScriptReadyRead();

// define your actions: usually, one action per button
private:

    /// Path to Apps folder (usually C:/RoboDK/Apps/)
    QString PathApps;

    /// List of directories containing enabled Apps (including AppLinks) to add to PYTHONPATH. i.e. C:/RoboDK/Apps/MyApp -> C:/RoboDK/Apps, C:/RoboDK/Apps/MyApp/AppLink.ini -> C:/DirOfMyApp
    QStringList PypathAppsDirs;

    /// List of all actions that need to be deleted
    QList<QAction*> AllActions;

    /// List of all menus that need to be deleted
    QList<QMenu*> AllMenus;

    /// List of toolbars that need to be deleted
    QList<QToolBar*> AllToolbars;

    /// List of actions available inside the menus or through the toolbar
    QList<tAppAction*> ListActions;

    /// List of all menus available from the main menu
    QList<tAppMenu*> ListMenus;

    /// List of toolbars
    QList<tAppToolbar*> ListToolbars;    

    /// Pointer to Apps action to list current apps:
    QAction *action_Apps;

    /// Show errors as a popup window (no errors are displayed when we are closing RoboDK as we trigger the stop_process signal)
    bool showErrors;

    /// List of processes to not kill
    QList<QProcess*> Process_SkipKill_List;

signals:
    void stop_process();

};
//! [0]


#endif // APPLOADER_H
