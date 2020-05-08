///This file implements the plugin class used to register and connect a plugin to robodk.

#include "pluginchip8.h"
#include "robodktools.h"
#include "irobodk.h"
#include "iitem.h"

#include "chip8roms.h"

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
#include <QElapsedTimer>

#include <QVector2D>
#include <QVector3D>
#include <QFuture>
#include <QtConcurrent>
#include <QFileDialog>


#include "chip8core.h"
#include "robotplayer.h"

//------------------------------- RoboDK Plug-in commands ------------------------------

///This function returns the plugin name shown in the plugin list in robodk
QString PluginChip8::PluginName(){
    return "OpenGL Chip8 Emulator";
}


///This function is called when the plugin is first loaded or enabled.
QString PluginChip8::PluginLoad(QMainWindow *mw, QMenuBar *menubar, QStatusBar *statusbar, RoboDK *rdk, const QString &settings){
    RDK = rdk;
    MainWindow = mw;
    StatusBar = statusbar;
    qDebug() << "Loading plugin " << PluginName();
    qDebug() << "Using settings: " << settings; // reserved for future compatibility

    // it is highly recommended to use the statusbar for debugging purposes (pass /DEBUG as an argument to see debug result in RoboDK)
    qDebug() << "Setting up the status bar";
    StatusBar->showMessage(tr("RoboDK Plugin %1 is being loaded").arg(PluginName()));

    // Here you can add all the "Actions": these actions are callbacks from buttons selected from the menu or the toolbar
    action_display = new QAction(tr("Display"));
    action_display->setCheckable(true);

    action_LoadROM = new QAction(tr("Load from file"));
    timer_Update.setInterval(0);

    // Make sure to connect the action to your callback (slot)
    connect(action_display, SIGNAL(triggered(bool)), this, SLOT(callback_display(bool)), Qt::QueuedConnection);
    connect(action_LoadROM, SIGNAL(triggered()), this, SLOT(callback_LoadROM()), Qt::QueuedConnection);

    // Here you can add one or more actions in the menu
    menu1 = menubar->addMenu("OpenGL Chip8 Emulator");
    qDebug() << "Setting up the menu bar";
    menu1->addAction(action_display);

    autoplay = menu1->addAction("Automatic Play");
    autoplay->setCheckable(true);
    autoplay->setChecked(!isPaused); //important, when you change isPaused we need to call autoplay.setChecked(!isPaused)
    connect(autoplay, SIGNAL(triggered(bool)), this, SLOT(callback_SetRunning(bool)));


    QMenu *menuROMs = menu1->addMenu("Load ROM");

    menuROMs->addAction(action_LoadROM);
    menuROMs->addSeparator();
    action_LoadROM->setObjectName("");

    int nROMs = sizeof(LIST_ROM_DATASIZE)/sizeof(uint16_t);
    for (int i=0; i<nROMs; i++) {
        QAction *action = menuROMs->addAction(QIcon(), LIST_ROM_NAMES[i], this, SLOT(callback_LoadROM()));
        action->setObjectName(QString::number(i));
    }

    // If desired, trigger the real time operation here:
    action_display->setChecked(true);
    DisplayActive = true;
    timer_Update.start();
    //New init
    pluginIntegrationInit();
    callback_LoadROM();

    // return string is reserverd for future compatibility
    return "";
};


/// This plugin configures the classes varaibles to their intial state.
/// Starts threads for autonomous control and the virtual systems emulation
void PluginChip8::pluginIntegrationInit() {
    #define ButtonSpacing 30.1
    #define xOriginOffset 115
    #define yOriginOffset -105

    // on windows, this returns: C:/RoboDK/Library/
    QString libPath = RDK->getParam("PATH_LIBRARY");

    //Generate the button models
    robotItem = RDK->getItem("", IItem::ITEM_TYPE_ROBOT);
    if (!ItemValid(robotItem)) {
        robotItem = RDK->AddFile(libPath+ "Mecademic-Meca500-R3.robot");
    }
    Item robotReference = robotItem->Parent();
    ScreenRef = RDK->getItem(NAME_SCREEN_REFERENCE, IItem::ITEM_TYPE_FRAME);
    if (!ItemValid(ScreenRef)) {
        ScreenRef = RDK->AddFrame(NAME_SCREEN_REFERENCE, robotItem->Parent());
        ScreenRef = RDK->getItem(NAME_SCREEN_REFERENCE, IItem::ITEM_TYPE_FRAME);

        Mat screenPose = transl(200,160,80)*rotz(-M_PI_2);
        qDebug() << "Pose screen: " << screenPose;
        ScreenRef->setPose(screenPose);
        robotReference->setPoseFrame(ScreenRef);
    }
    RDK->Render();

    // load a reference part
    Item buttonRef = RDK->AddFile(libPath+ "part.sld", ScreenRef);
    if (!RDK->Valid(buttonRef)) {
        return;
    }

    // We know the part.sld is a cylinder of size 60 x 80 (DxL) (part of the RoboDK Library)
    double xyzscale[3] = {0.5,0.5,-0.1};

    // make the object visible but not its coordinate system
    buttonRef->setVisible(true, 0);
    buttonRef->setGeometryPose(transl(0,0,0));
    buttonRef->Scale(xyzscale);
    buttonRef->Copy();

    //Array for converting the buttons numerical value to it's position in the grid
    int buttonPosMap[16] = {1,12,13,14,
                            8,9,10,4,
                            5,6,0,2,
                            15,11,7,3};

    // create the identity matrix
    //Mat noOffset = new Mat();
    for (int i=0; i<16; i++){
        int x = buttonPosMap[i] % 4;
        int y = buttonPosMap[i] / 4;
        Item button_i = ScreenRef->Paste();
        /*Item button_i = RDK->AddFile(libPath+ "part.sld", ScreenRef);
        if (!RDK->Valid(button_i)) {
            return;
        }
        button_i->setGeometryPose(transl(0,0,0));
        button_i->Scale(xyzscale);
        */

        button_i->setName(QString(NAME_KEY).arg(i));
        button_i->setPose(transl(x*ButtonSpacing+xOriginOffset, y*ButtonSpacing+yOriginOffset, 0));
        buttonList.append(button_i);
    }
    // Special Parameter to collapse the items in the tree (hides the buttons)
    //ScreenRef->setParam("Tree","Collapse");

    // delete the reference item
    buttonRef->Delete();

    // remove selection of last item added
    RDK->Command("ClearSelection");

    //-----------------------------------------------
    // Start the robot player effect in another thread
    PlayerEmulator = new RobotPlayer(this, robotItem->Name(), isPaused);
    //QObject::connect(PlayerEmulator,SIGNAL(finished()), &app, SLOT(quit()));
    PlayerEmulator->start();

    return;
}

///Cleans up the plugins state when it's unloaded, stops other threads.
void PluginChip8::PluginUnload(){
    // Cleanup the plugin
    qDebug() << "Unloading plugin " << PluginName();

    // remove the menu
    menu1->deleteLater();
    menu1 = nullptr;

    // remove the toolbar
    if (toolbar1 != nullptr){
        toolbar1->deleteLater();
        toolbar1 = nullptr;
    }

    //End the simulation thread (c style)
    chip8EndEmulationLoop();
    SimulationThread.waitForFinished();

    //End the automatic movement thread (c++ style)
    PlayerEmulator->requestInterruption();
}

///Called on plugin loading, used to configure the custom toolbar
void PluginChip8::PluginLoadToolbar(QMainWindow *mw, int icon_size){
    // Create a new toolbar:
    toolbar1 = nullptr;

    /*toolbar1 = mw->addToolBar("Chip8 Game Emulator");
    toolbar1->setIconSize(QSize(icon_size, icon_size));

    // Important: It is highly recommended to set an object name on toolbars. This allows saving the preferred location of the toolbar by the user
    toolbar1->setObjectName(PluginName() + "-Display");

    // Add a new button to the toolbar
    toolbar1->addAction(action_display);
    */
}


bool PluginChip8::PluginItemClick(Item item, QMenu *menu, TypeClick click_type){
    qDebug() << "Selected item: " << item->Name() << " of type " << item->Type() << " click type: " << click_type;
    return false;
}

QString PluginChip8::PluginCommand(const QString &command, const QString &value){
    qDebug() << "Received command: " << command << "    With value: " << value;
    if (command.compare("Information", Qt::CaseInsensitive) == 0){
        return "Done";
    }

    return "";
}

// Render your own graphics here. This function is called every time the OpenGL window is displayed. The RoboDK OpenGL context is active at this moment.
// Make sure to make this code as fast as possible to not provoke render lags
void PluginChip8::PluginEvent(TypeEvent event_type){
    switch (event_type) {
    case EventChanged:
        //qDebug() << "An item has been added or deleted. Current station: " << RDK->getActiveStation()->Name();
        // Use: RDK->getActiveStation() to get the open station. This call always returns a valid pointer
        // Use: RDK->Valid(item ) to check if an item exists (it could have been deleted! Therefore, provoke a crash when using a method)
        /*if (!RDK->Valid(Robot)){
            Robot = nullptr;
        }*/

        /*if (!RDK->Valid(Robot)) {
            Robot = nullptr;
        }*/
        break;
    case EventMoved:
        break;
    case EventRender:
        //qDebug() << "Render event";
        RenderOpenGL();
        break;
    default:
        qDebug() << "Unknown/future event: " << event_type;

    }
}

//----------------------------------------------------------------------------------
// Define your own button callbacks here

///Used to update the automatically update the screen
void PluginChip8::callback_display(bool display_on){
    DisplayActive = display_on;
    qDebug() << "Display active: " << DisplayActive;
    if (DisplayActive) {
        timer_Update.start();
    } else {
        timer_Update.stop();
    }
    // redisplay the screen
    RDK->Render();
}


///Load one of the preconfigured chip8 roms by id, restarts the emulation thread
void PluginChip8::LoadRom(int rom_id) {
    const uint8_t *data = LIST_ROM_DATA[rom_id];
    QByteArray romData((const char *)data, LIST_ROM_DATASIZE[rom_id]);
    chip8EndEmulationLoop();
    SimulationThread.waitForFinished();
    chip8Init(RDK);
    chip8LoadFile(romData);
    // Start the simulation in another thread
    SimulationThread = QtConcurrent::run(chip8EmulationLoop);

    if (rom_id == 0) {
        isPaused = false;
        autoplay->setChecked(!isPaused);
    }
}

///Callback function to load ROM files, called by using the menu
void PluginChip8::callback_LoadROM(){
    QAction *sender = qobject_cast<QAction*>(QObject::sender());
    if (sender == nullptr) {
        LoadRom(0);
    } else if (!sender->objectName().isEmpty()) {
        LoadRom(sender->objectName().toInt());
    } else {
        QString fileName = QFileDialog::getOpenFileName(nullptr, tr("Load ROM file for Chip8"), "", "*.ch8, *.bin\n*.*", nullptr);
        QFile romFile(fileName);
        romFile.open(QIODevice::ReadOnly);
        if (romFile.size() > (4096-0x200) ) {
            RDK->ShowMessage("File too big for Chip 8 make sure the ROM is 3584 bytes at most");
        }
        else {
            QByteArray romData = romFile.readAll();
            chip8EndEmulationLoop();
            SimulationThread.waitForFinished();
            chip8Init(RDK);
            chip8LoadFile(romData);
            SimulationThread = QtConcurrent::run(chip8EmulationLoop);
        }
    }
}

///Callback function used to control the autonomous control of the robot via the api
void PluginChip8::callback_SetRunning(bool running){
    isPaused = !running;
    autoplay->setChecked(running);
}

///Provokes a full screen update in robodk, this includes a PluginEvent of type render
void PluginChip8::UpdateRoboDK(){
    // provoke full RoboDK screen update
    RDK->Render();
}

/// Implement custom rendering. This must be called inside PluginEvent(RenderOpenGL)
/// This function is called with the current OpenGL context active
void PluginChip8::RenderOpenGL(){
    if (!DisplayActive){
        qDebug() << "Skipping custom OpenGL render";
        return;
    }
    //qDebug() << "Customized OpenGL display...";
    if (!(RDK->Valid(ScreenRef) && RDK->Valid(robotItem))) {
        return;
    }

    robotItem->setPoseFrame(ScreenRef); // we should not reset the robot reference here
    Mat ToolPoseRobotSpace = robotItem->Pose();
    double toolxyz[6];
    ToolPoseRobotSpace.ToXYZRPW(toolxyz);

    bool aButtonSelected = false;
    bool buttonStatesCopy[16];
    for (int i=0; i<buttonList.length(); i++){
        //UI pressed
        Item button_i = buttonList[i];
        if (!RDK->Valid(button_i)) {
            continue;
        }
        bool isSelected = button_i->Selected();
        //Robot Pressed
        double buttonXYZ[6];
        button_i->Pose().ToXYZRPW(buttonXYZ);
        double distance2D = sqrt(pow(buttonXYZ[0] - toolxyz[0], 2) +
                                 pow(buttonXYZ[1] - toolxyz[1], 2) * 1.0);
        //double distance3D = sqrt(pow(buttonXYZ[0]-toolxyz[0],2.0)+pow(buttonXYZ[1]-toolxyz[1],2.0)+pow(buttonXYZ[2]-toolxyz[2],2.0));
        double zDistance = toolxyz[2]-buttonXYZ[2];

        if ( (distance2D < ButtonSpacing*0.75) && (zDistance < 0)) {
            //qDebug() << "RobotPress";
            //qDebug() << i;
            isSelected = true;
        }

        aButtonSelected |= isSelected;
        buttonStatesCopy[i] = isSelected;
    }


    static bool buttonsReleased = false;
    if (aButtonSelected) {
        buttonsReleased = false;
        chip8UpdateButtons(buttonStatesCopy);
        //RDK->Command("ClearSelection");
    } else {
        //Released
        if (buttonsReleased == false) {
            chip8UpdateButtons(buttonStatesCopy);
            buttonsReleased = true;
        }
    }
    chip8Render(RDK,ScreenRef);
    //qDebug() << "Done";
}








