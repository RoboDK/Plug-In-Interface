///This file implements the Class responsible for automically moving the robot,
///it uses the api rather than the plugin interface

#include "pluginchip8.h"
#include "robotplayer.h"
#include "iitem.h"

// In this module we use the RoboDK API instead of the Plugin Interface
// The naming of the RoboDK API/interface is almost the same but the main difference is that the RoboDK API is executed on
// RoboDK's event loop, therefore, there is less risk to block the UI when the robot is moving using blocked moves such as robot.MoveL(pose)
// More information here:
// https://github.com/RoboDK/Plug-In-Interface#plug-in-interface-vs-robodk-api

// Defining RDK_SKIP_NAMESPACE will prevent us from having to use RoboDK_API::
//#define RDK_SKIP_NAMESPACE
#include "robodk_api/robodk_api.h"
//using namespace RoboDK_API;

RobotPlayer::RobotPlayer(QObject *pPlugin, const QString &robot_name, bool &paused) :
    RobotName(robot_name),
    isPaused(paused)
{
    // Example to connect a signal to a callback in another thread
    // connect(this,SIGNAL(SignalToOtherThread), pPlugin, SLOT(Callback(double*)));

    // Important: do not call RoboDK API here because it won't be able to connect
    // until after the plugin has started if the plugin is loaded on startup
    // We need to run
    // (RDK = new RoboDK_API::RoboDK(); )
}


bool RobotPlayer::InitItems(RoboDK_API::RoboDK *rdk){
    //Retrieve the robodk items used in the simulation
    //RoboDK_API::Item SelectButton;

    // get the screen refence item
    ItemRef = rdk->getItem(NAME_SCREEN_REFERENCE, IItem::ITEM_TYPE_FRAME);
    if (!ItemRef.Valid()){
        return false;
    }

    // get the robot item
    ItemRobot = rdk->getItem(RobotName, IItem::ITEM_TYPE_ROBOT);
    if (!ItemRobot.Valid()){
        return false;
    }

    RoboDK_API::Item button_i;
    for (int i=0; i<16; i++){
        QString btnName = QString(NAME_KEY).arg(i);
        button_i = rdk->getItem(btnName, IItem::ITEM_TYPE_OBJECT);
        if (!button_i.Valid()){
            return false;
        }
    }

    // make the robot use the screen reference as a reference frame
    ItemRobot.setPoseFrame(ItemRef);

    // Move the robot ready to push a button
    ItemRobot.MoveJ(RoboDK_API::Mat::transl(0,0,100) * button_i.Pose() * RoboDK_API::Mat::rotx(M_PI));

    return true;
}

///Main thread for the automatic robot player, randomly picks a button and presses it.
void RobotPlayer::run(void) {
    // RoboDK API
    RoboDK_API::RoboDK *rdk;

    // Initialize: retrieve items
    bool pluginRunning = true;

    // Start RoboDK API and hold a pointer to relevant items
    rdk = new RoboDK_API::RoboDK();//"127.0.0.1",20500);
    if (!InitItems(rdk)){
        qDebug() << "Warning! Problems initalizing or retrieving objects";
        return;
    }

    // run thread loop:
    while (pluginRunning) {
        // check if we want to stop this thread
        if ((isInterruptionRequested() == true) ) {
            qDebug() << "Ending robot move thread";
            pluginRunning = false;

            // Delete/disconnect
            rdk->Disconnect();
            delete rdk;
            return;
        }

        // go back to the loop if we are paused
        if (isPaused) {
            qDebug() << "Paused robot move thread";
            QThread::msleep(200);
            continue;
        }

        // check if the API disconnected, if so, change to paused
        if (!rdk->Connected()) {
            qDebug() << "Connection ended ";
            isPaused = true;
            continue;
        }

        // Simulate the push of a button but just selecting it in RoboDK
        // We don't need a Mutex here: Most functions of the RoboDK API are executed when the event loop is executed
        // (no other functions of the plugin will be executed)
        // Note: If an item is invalid, call InitializeItems and continue the loop after a small pause

        // Step 1: Randomly decide what button must be pushed
        int currentButton;
        currentButton = rand() % 3;
        currentButton += 4;

        // Step 2: Move the robot to push the required button (approach, move to point, EMULATE push, retract)
        RoboDK_API::Item buttonObject = rdk->getItem(QString(NAME_KEY).arg(currentButton), IItem::ITEM_TYPE_OBJECT);
        /*if (!rdk->Exists(buttonObject) || !rdk->Exists(curRobot)) {
            qDebug() << "Button disappeared: " << currentButton;
            isPaused = true;
            InitItems(rdk);
            continue;
        }*/

        // Take the current robot pose and update XYZ values to reach the point

        // Get the current robot pose
        RoboDK_API::Mat  robotPose = ItemRobot.Pose();

        // Get the button pose
        RoboDK_API::Mat buttonPose = buttonObject.Pose();

        // Create the destination pose based on the robotPose orientation and buttonPose position
        RoboDK_API::Mat targetPose(robotPose);
        tXYZ pos_xyz;
        buttonPose.Pos(pos_xyz); // get XYZ
        targetPose.setPos(pos_xyz); // set XYZ
        //Go a bit into the button;
        targetPose = targetPose * RoboDK_API::transl(0,0,2);
        //qDebug() << "Moving to push button: " << targetPose.ToString();

        // make the approach point 50 mm higher along reference Z axis
        RoboDK_API::Mat targetPoseApproach = RoboDK_API::transl(0,0,20) * targetPose;

        // make movements blocking
        bool blocking = true;

       //This functions will block so aditional delay isn't necesasry
        ItemRobot.MoveJ(targetPoseApproach, blocking);

        // Move Linear to point
        ItemRobot.MoveL(targetPose, blocking);

        // for space invaders, make the "shoot" button (#5) last longer than the move buttons
        if (currentButton != 5) {
            QThread::msleep(600);
        }
        else {
            QThread::msleep(100);
        }
        // RDK->setSelection(QList<RoboDK_API::Item>() << buttonObject)

        // move linear to to retract
        ItemRobot.MoveL(targetPoseApproach, blocking);

        // pause 100 ms
        QThread::msleep(100);

        // if needed, trigger signal to other thread:
        //emit SignalToOtherThread(strin);
    }

    // Delete/disconnect
    pluginRunning = false;
    rdk->Disconnect();
    delete rdk;
}















