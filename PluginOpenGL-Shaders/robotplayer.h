#ifndef ROBOTPLAYER_H
#define ROBOTPLAYER_H

//#include "irobodk.h"
#include "robodk_api/robodk_api.h"

#include <QThread>

class RobotPlayer : public QThread {

    Q_OBJECT

public:
    RobotPlayer(QObject *pPlugin, const QString &robot_name, bool &paused);

    /// Configures the items used by the autonomous control
    bool InitItems(RoboDK_API::RoboDK *rdk);

    // Run main thread loop
    void run(void);

    // reference to paused flag (menu checkbox)
    bool &isPaused;

    // remember the screen reference and the robot items
    QString RobotName;
    RoboDK_API::Item ItemRef;
    RoboDK_API::Item ItemRobot;
};

#endif // ROBOTPLAYER_H
