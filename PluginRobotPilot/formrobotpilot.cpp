#include "formrobotpilot.h"
#include "ui_formrobotpilot.h"

FormRobotPilot::FormRobotPilot(RoboDK *rdk, QWidget *parent) : QWidget(parent),
    ui(new Ui::FormRobotPilot)
{
    // keep the pointer to RoboDK
    RDK = rdk;
    Robot = nullptr;

    // Create the window
    ui->setupUi(this);

    // important to delete the form when we close it (free memory)
    setAttribute(Qt::WA_DeleteOnClose);

    // Make this form as a separate window
    setWindowFlags(windowFlags() | Qt::Window);

    // Use the Cartesian Tool or Reference movement by default
    //ui->radCartesianTool->click();
    ui->radCartesianReference->click();

    // Try to select the robot (updates the robot label)
    SelectRobot();
}

FormRobotPilot::~FormRobotPilot(){
    delete ui;
}

void FormRobotPilot::on_btnSelectRobot_clicked(){
    SelectRobot(true);
}

bool FormRobotPilot::SelectRobot(bool force_selection){
    if (!force_selection && RDK->Valid(Robot)){
        return true;
    }

    // force the user to select a robot in the RDK project
    QList<Item> all_robots = RDK->getItemList(IItem::ITEM_TYPE_ROBOT);
    if (all_robots.length() == 0){
        ui->lblRobot->setText("Load a robot");
        RDK->ShowMessage("Select File-Open to load a robot or a RoboDK station", false);
        //QString file = QFileDialog::getOpenFilename()
        //RDK->AddFile()
        return false;
    } else {
        Robot = RDK->ItemUserPick("Select a robot", IItem::ITEM_TYPE_ROBOT);
    }
    bool robot_is_selected = (Robot != nullptr);
    if (robot_is_selected) {
        ui->lblRobot->setText("Selected robot:\n" + Robot->Name());
    } else {
        ui->lblRobot->setText("Robot not selected");
    }
    return robot_is_selected;
}



void FormRobotPilot::setup_btn_joints(){
    ui->btnTXn->setText("J1-");
    ui->btnTXp->setText("J1+");
    ui->btnTYn->setText("J2-");
    ui->btnTYp->setText("J2+");
    ui->btnTZn->setText("J3-");
    ui->btnTZp->setText("J3+");
    ui->btnRXn->setText("J4-");
    ui->btnRXp->setText("J4+");
    ui->btnRYn->setText("J5-");
    ui->btnRYp->setText("J5+");
    ui->btnRZn->setText("J6-");
    ui->btnRZp->setText("J6+");
}
void FormRobotPilot::setup_btn_cartesian(){
    ui->btnTXn->setText("Tx-");
    ui->btnTXp->setText("Tx+");
    ui->btnTYn->setText("Ty-");
    ui->btnTYp->setText("Ty+");
    ui->btnTZn->setText("Tz-");
    ui->btnTZp->setText("Tz+");
    ui->btnRXn->setText("Rx-");
    ui->btnRXp->setText("Rx+");
    ui->btnRYn->setText("Ry-");
    ui->btnRYp->setText("Ry+");
    ui->btnRZn->setText("Rz-");
    ui->btnRZp->setText("Rz+");
}
void FormRobotPilot::on_radCartesianReference_clicked(){
    setup_btn_cartesian();
}

void FormRobotPilot::on_radCartesianTool_clicked()
{
    setup_btn_cartesian();
}

void FormRobotPilot::on_radJoints_clicked()
{
    setup_btn_joints();
}

void FormRobotPilot::on_btnTXn_clicked(){ IncrementalMove(0, -1); }
void FormRobotPilot::on_btnTYn_clicked(){ IncrementalMove(1, -1); }
void FormRobotPilot::on_btnTZn_clicked(){ IncrementalMove(2, -1); }
void FormRobotPilot::on_btnRXn_clicked(){ IncrementalMove(3, -1); }
void FormRobotPilot::on_btnRYn_clicked(){ IncrementalMove(4, -1); }
void FormRobotPilot::on_btnRZn_clicked(){ IncrementalMove(5, -1); }

void FormRobotPilot::on_btnTXp_clicked(){ IncrementalMove(0, +1); }
void FormRobotPilot::on_btnTYp_clicked(){ IncrementalMove(1, +1); }
void FormRobotPilot::on_btnTZp_clicked(){ IncrementalMove(2, +1); }
void FormRobotPilot::on_btnRXp_clicked(){ IncrementalMove(3, +1); }
void FormRobotPilot::on_btnRYp_clicked(){ IncrementalMove(4, +1); }
void FormRobotPilot::on_btnRZp_clicked(){ IncrementalMove(5, +1); }


void FormRobotPilot::IncrementalMove(int id, double sense){
    if (!SelectRobot(false)) { return; }

    // Calculate the relative movement
    double step = sense * ui->spnStep->value();

    // check if it is a joint movement or a Cartesian movement
    bool is_joint_move = ui->radJoints->isChecked();
    if (is_joint_move){
        tJoints joints = Robot->Joints();
        if (!joints.Valid()){
            RDK->ShowMessage(tr("Invalid robot joints or unable retrieve joints from connected robot"), false);
            return;
        }
        if (id >= joints.Length()){
            qDebug() << "Internal problem: Invalid joint ID";
            return;
        }
        joints.Data()[id] = joints.Data()[id] + step;
        bool can_move = Robot->MoveJ(joints);
        if (!can_move){
            RDK->ShowMessage(tr("The robot can't move to this location"), false);
        }
    } else {
        // check the index so that is is within 0-5
        if (id < 0 || id >= 6){
            qDebug()<< "Internal problem: Invalid id provided for an incremental move";
            return;
        }

        // apply to XYZWPR
        tXYZWPR xyzwpr;
        for (int i=0; i<6; i++){
            xyzwpr[i] = 0;
        }
        xyzwpr[id] = step;

        Mat pose_increment;
        pose_increment.FromXYZRPW(xyzwpr);

        // get the current robot pose
        Mat pose_robot = Robot->Pose();

        Mat pose_robot_new;

        bool is_tcp_relative_move = ui->radCartesianTool->isChecked();
        if (is_tcp_relative_move){
            // apply relative to the TCP:
            // if the movement is relative to the TCP we must POST MULTIPLY the movement
            pose_robot_new = pose_robot * pose_increment;
        } else {
            // it is a movement relative to the reference frame
            // if the movement is relative to the reference frame we must PRE MULTIPLY the XYZ translation:
            // new_robot_pose = movement_pose * robot_pose;
            // Note: Rotation applies from the robot axes.

            Mat transformation_axes(pose_robot);
            transformation_axes.setPos(0, 0, 0);
            Mat movement_pose_aligned = transformation_axes.inv() * pose_increment * transformation_axes;
            pose_robot_new = pose_robot * movement_pose_aligned;
        }

        bool canmove = Robot->MoveJ(pose_robot_new);
        if (!canmove){
            RDK->ShowMessage(tr("The robot can't move to this location"), false);
        }
        /*if (!Robot->setPose(pose_robot_new)){
            RDK->ShowMessage("The robot can not reach the requested position!", false);
        }*/
    }

    // This is very important to update robot joints and force a display RoboDK
    RDK->Render();
}




void FormRobotPilot::on_chkRunOnRobot_clicked(bool checked){
    if (checked) {
        if (!SelectRobot(false)) {
            RDK->ShowMessage(tr("Select a robot first"), false);
            ui->chkRunOnRobot->setChecked(false);
            return;
        }
        /*if (!){
            RDK->ShowMessage(tr("Robot not connected! Select Connect->Connect Robot and enter the IP"), false);
            return;
        }*/
        Robot->Connect();
        RDK->setRunMode(RoboDK::RUNMODE_RUN_ROBOT);
        Robot->Joints(); // this will retrieve the joints from the real robot if connection was successful (it should be at this point)
        RDK->Render();
        RDK->ShowMessage(tr("Run Mode set to run the real robot. Make sure you are properly connected to the robot (select Connect-Connect Robot)"), false);

    } else {
        RDK->setRunMode(RoboDK::RUNMODE_SIMULATE);
        RDK->ShowMessage(tr("Run Mode set to simulate"), false);
    }
}
