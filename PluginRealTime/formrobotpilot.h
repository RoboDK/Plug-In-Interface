#ifndef FORMROBOTPILOT_H
#define FORMROBOTPILOT_H

#include <QWidget>
#include "irobodk.h"
#include "iitem.h"

namespace Ui {
class FormRobotPilot;
}

class FormRobotPilot : public QWidget
{
    Q_OBJECT

public:
    explicit FormRobotPilot(RoboDK *rdk, QWidget *parent = nullptr);
    ~FormRobotPilot();

    ///
    /// \brief Select a robot in the Robot variable
    /// \return True if a robot was properly retrieved
    ///
    bool SelectRobot();

    void IncrementalMove(int id, double sense);

private:
    ///
    /// \brief Set the jog button text as joint movements
    ///
    void setup_btn_joints();

    ///
    /// \brief Set the jog button text as Cartesian movement
    ///
    void setup_btn_cartesian();

private slots:
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

private:
    Ui::FormRobotPilot *ui;
    RoboDK *RDK;
    Item Robot;

};

#endif // FORMROBOTPILOT_H
