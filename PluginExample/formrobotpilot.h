#ifndef FORMROBOTPILOT_H
#define FORMROBOTPILOT_H

#include <QWidget>
#include "irobodk.h"
#include "iitem.h"

namespace Ui {
class FormRobotPilot;
}

/// The form FormRobotPilot allows you to move a robot by increments of a desired size.
/// This forms shows and example that integrates the RoboDK API with a Plug-In to customize a window docked inside RoboDK's main window.
/// \image html formrobotpilot.png
class FormRobotPilot : public QWidget
{
    Q_OBJECT

public:

    explicit FormRobotPilot(RoboDK *rdk, QWidget *parent = nullptr);
    ~FormRobotPilot();

    /// \brief Select a robot in the Robot variable
    /// \return True if a robot was properly retrieved
    bool SelectRobot();

    /// \brief IncrementalMove
    /// \param id Joint id or cartesian move id [x,y,z,r,p,w]
    /// \param sense +1 (positive motion) or -1 (negative motion)
    void IncrementalMove(int id, double sense);

private:

    /// Set the jog button text as joint movements
    void setup_btn_joints();

    /// Set the jog button text as Cartesian movement
    void setup_btn_cartesian();

private slots:

    /// \brief Select a robot (useful if you have more than one robot in your station)
    void on_btnSelectRobot_clicked();

    // Radio buttons
    void on_radCartesianTool_clicked();
    void on_radJoints_clicked();
    void on_radCartesianReference_clicked();

    // 6x2 buttons:
    void on_btnTXn_clicked();
    void on_btnTYn_clicked();
    void on_btnTZn_clicked();
    void on_btnRXn_clicked();
    void on_btnRYn_clicked();
    void on_btnRZn_clicked();
    void on_btnTXp_clicked();
    void on_btnTYp_clicked();
    void on_btnTZp_clicked();
    void on_btnRXp_clicked();
    void on_btnRYp_clicked();
    void on_btnRZp_clicked();

    void on_chkRunOnRobot_clicked(bool checked);

private:
    Ui::FormRobotPilot *ui;

    /// \brief Pointer to the RoboDK interface.
    RoboDK *RDK;

    /// \brief Pointer to the robot that we are piloting.
    Item Robot;

};

#endif // FORMROBOTPILOT_H
