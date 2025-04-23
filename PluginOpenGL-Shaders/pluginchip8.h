#ifndef PluginChip8_H
#define PluginChip8_H


#include <QObject>
#include <QtPlugin>
#include <QDockWidget>
#include "iapprobodk.h"
#include "robodktypes.h"
#include "robotplayer.h"
#include <QTimer>

#include <QOpenGLWidget>
#include <QOpenGLFunctions>
#include <QMatrix4x4>
#include <QQuaternion>
#include <QVector2D>
#include <QBasicTimer>
#include <QOpenGLShaderProgram>
#include <QOpenGLTexture>
#include <QOpenGLBuffer>
#include <QFuture>
#include <QtConcurrent>

class QToolBar;
class QMenu;
class QAction;
class IRoboDK;
class IItem;
class FormRobotPilot;


#define NAME_SCREEN_REFERENCE "Chip8 Emulator"
#define NAME_KEY "%1"



class PluginChip8 : public QObject, IAppRoboDK
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
    /// \brief Called when the robot pilot button/action is selected
    ///
    void callback_display(bool on);    

    /// Load a ROM ID or from a file (-1)
    void callback_LoadROM();

    /// Trigger automatic play
    void callback_SetRunning(bool running);

private:
    ///
    /// \brief RoboDK callback to update the screen (add your OpenGL code here). Here we can implement customized OpenGL rendering.
    // Here, we MUST draw
    ///
    void RenderOpenGL();
    void UpdateRoboDK();
    //New
    void pluginIntegrationInit();
    void pluginStop();
    void LoadRom(int rom_id);

    QList<Item> buttonList;
    Item ScreenRef;
    Item robotItem;
    QFuture<void> SimulationThread;
    RobotPlayer *PlayerEmulator;
    bool isPaused = false;


private:
    // define your actions: usually, one action per button
    QToolBar *toolbar1;
    QMenu *menu1;
    QAction *autoplay;
    QAction *action_display;
    QAction *action_LoadROM;


    /// Timer to automatically provoke display rendering
    QTimer timer_Update;

    /// Flag to display customized OpenGL objects
    bool DisplayActive;


};

#endif // PluginChip8_H
