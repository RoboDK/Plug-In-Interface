/*
 * Copyright (c) 2026 RoboDK Global. All rights reserved.
 */

// This is required on top to have M_PI
#define _USE_MATH_DEFINES
#include <cmath>

#include "samplekinematics.h"

#include <iostream>


// You must remove the line "CONFIG -= qt" from the .pro file if you want to use Qt features like QDebug
// #include <QDebug>

// #include <cstring> // For memset or memcpy if needed


/*!
 * \brief iRobot_BaseXYZWPR
 * Get the pointer of the robot base adaptor robot base (not the active base frame)
 * \param ptr_robot
 * \return Pointer to a 6D array (mm and rad)
 */
const real_T* iRobot_BaseXYZWPR(const robot_T *ptr_robot){
    return ((const real_T*) ptr_robot) + 9*20;
}

/*!
 * \brief iRobot_ToolXYZWPR
 * Get the pointer of the robot tool flange adaptor (pose that takes from the DHM calculation to the robot flange (not the active Tool)
 * \param ptr_robot
 * \return Pointer to a 6D array (mm and rad)
 */
const real_T* iRobot_ToolXYZWPR(const robot_T *ptr_robot){
    return ((const real_T*) ptr_robot) + 28*20;
}

/*!
 * \brief iRobot_JointLimLower
 * \param ptr_robot
 * \return Returns an array pointer to the lower joint limits (mm and deg)
 */
const real_T* iRobot_JointLimLower(const robot_T *ptr_robot){
    return ((const real_T*) ptr_robot) + 30*20;
}

/*!
 * \brief iRobot_JointLimUpper
 * \param ptr_robot
 * \return Returns an array pointer to the upper joint limits (mm and deg)
 */
const real_T* iRobot_JointLimUpper(const robot_T *ptr_robot){
    return ((const real_T*) ptr_robot) + 31*20;
}

/*!
 * \brief iRobot_JointSenses
 * \param ptr_robot
 * \return Returns a pointer to an array of joint senses (-1 or +1)
 */
const real_T* iRobot_JointSenses(const robot_T *ptr_robot){
    return ((const real_T*) ptr_robot) + 3*20+4;
}

/*!
 * \brief iRobot_DHM_JointId
 * Retrieve the DHM parameters for the joint id. The Joint ID must be an index between 0 and <nDOFs.
 * The DHM parameters provide the [alpha (rX in rad), a (tx in mm), theta (rZ in rad), d (tZ in mm), translation], the index 5 is 0 if the joint is rotative and 1 if it is translation.
 * \param ptr_robot
 * \param joint_id
 * \return
 */
const real_T* iRobot_DHM_JointId(const robot_T *ptr_robot, int joint_id){
    return ((const real_T*) ptr_robot) + (10+joint_id)*20;
}

/*!
 * \brief iRobot_nDOFs returns the number of degrees of freedom
 * \param ptr_robot
 * \return
 */
int iRobot_nDOFs(const robot_T *ptr_robot){
    return ((const real_T*) ptr_robot)[1*20+1];
}


///
/// \brief Convert the 4 values of a DHM transformation to a pose
/// \param rx_tx_rz_tz values in rad and mm [rx (rad), tx (mm), rz (rad), tz (mm)]
/// \param pose
///
void DHM_2_Pose(const real_T rx_tx_rz_tz[4], real_T pose[16]){
    real_T rx = rx_tx_rz_tz[0];
    real_T tx = rx_tx_rz_tz[1];
    real_T rz = rx_tx_rz_tz[2];
    real_T tz = rx_tx_rz_tz[3];

    pose[0] = cos(rz);
    pose[1] = cos(rx)*sin(rz);
    pose[2] = sin(rx)*sin(rz);
    pose[4] = -sin(rz);
    pose[5] = cos(rx)*cos(rz);
    pose[6] = cos(rz)*sin(rx);
    pose[8] = 0.0;
    pose[9] = -sin(rx);
    pose[10] = cos(rx);
    pose[12] = tx;
    pose[13] = -tz*sin(rx);
    pose[14] = tz*cos(rx);
    pose[3] = 0.0;
    pose[7] = 0.0;
    pose[11] = 0.0;
    pose[15] = 1.0;
}

///
/// \brief Convert the 6 values of XYZWPR (mm and rad) to a pose
/// \param xyzwpr
/// \param pose
///
void XYZWPR_2_Pose(const real_T xyzwpr[6], real_T pose[16]){
    pose[0] = cos(xyzwpr[4]) * cos(xyzwpr[5]);
    pose[1] = cos(xyzwpr[3]) * sin(xyzwpr[5]) + cos(xyzwpr[5]) * sin(xyzwpr[3]) * sin(xyzwpr[4]);
    pose[2] = sin(xyzwpr[3]) * sin(xyzwpr[5]) - cos(xyzwpr[3]) * cos(xyzwpr[5]) * sin(xyzwpr[4]);
    pose[4] = -cos(xyzwpr[4]) * sin(xyzwpr[5]);
    pose[5] = cos(xyzwpr[3]) * cos(xyzwpr[5]) - sin(xyzwpr[3]) * sin(xyzwpr[4]) * sin(xyzwpr[5]);
    pose[6] = cos(xyzwpr[5]) * sin(xyzwpr[3]) + cos(xyzwpr[3]) * sin(xyzwpr[4]) * sin(xyzwpr[5]);
    pose[8] = sin(xyzwpr[4]);
    pose[9] = -cos(xyzwpr[4]) * sin(xyzwpr[3]);
    pose[10] = cos(xyzwpr[3]) * cos(xyzwpr[4]);
    pose[12] = xyzwpr[0];
    pose[13] = xyzwpr[1];
    pose[14] = xyzwpr[2];
    pose[3] = 0.0;
    pose[7] = 0.0;
    pose[11] = 0.0;
    pose[15] = 1.0;
}

///
/// \brief Multiple 2 matrices
/// \param inA
/// \param inB
/// \param out The output matrix should not be any of the input matrices for the calculation to work
///
void Pose_Mult(const real_T inA[16], const real_T inB[16], real_T out[16]){
    (out)[0] = (inA)[0]*(inB)[0] + (inA)[4]*(inB)[1] + (inA)[8]*(inB)[2] + (inA)[12]*(inB)[3];
    (out)[1] = (inA)[1]*(inB)[0] + (inA)[5]*(inB)[1] + (inA)[9]*(inB)[2] + (inA)[13]*(inB)[3];
    (out)[2] = (inA)[2]*(inB)[0] + (inA)[6]*(inB)[1] + (inA)[10]*(inB)[2] + (inA)[14]*(inB)[3];
    (out)[3] = 0.0;
    (out)[4] = (inA)[0]*(inB)[4] + (inA)[4]*(inB)[5] + (inA)[8]*(inB)[6] + (inA)[12]*(inB)[7];
    (out)[5] = (inA)[1]*(inB)[4] + (inA)[5]*(inB)[5] + (inA)[9]*(inB)[6] + (inA)[13]*(inB)[7];
    (out)[6] = (inA)[2]*(inB)[4] + (inA)[6]*(inB)[5] + (inA)[10]*(inB)[6] + (inA)[14]*(inB)[7];
    (out)[7] = 0.0;
    (out)[8] = (inA)[0]*(inB)[8] + (inA)[4]*(inB)[9] + (inA)[8]*(inB)[10] + (inA)[12]*(inB)[11];
    (out)[9] = (inA)[1]*(inB)[8] + (inA)[5]*(inB)[9] + (inA)[9]*(inB)[10] + (inA)[13]*(inB)[11];
    (out)[10] = (inA)[2]*(inB)[8] + (inA)[6]*(inB)[9] + (inA)[10]*(inB)[10] + (inA)[14]*(inB)[11];
    (out)[11] = 0.0;
    (out)[12] = (inA)[0]*(inB)[12] + (inA)[4]*(inB)[13] + (inA)[8]*(inB)[14] + (inA)[12]*(inB)[15];
    (out)[13] = (inA)[1]*(inB)[12] + (inA)[5]*(inB)[13] + (inA)[9]*(inB)[14] + (inA)[13]*(inB)[15];
    (out)[14] = (inA)[2]*(inB)[12] + (inA)[6]*(inB)[13] + (inA)[10]*(inB)[14] + (inA)[14]*(inB)[15];
    (out)[15] = 1;
}

///
/// \brief Inverse of a 4x4 homogeneous matrix
/// \param in
/// \param out input and output matrices must be different, otherwise the inverse operation won't be properly calculated.
///
void Pose_Inv(const real_T in[16], real_T out[16]){
    (out)[0] = (in)[0];
    (out)[1] = (in)[4];
    (out)[2] = (in)[8];
    (out)[3] = 0.0;
    (out)[4] = (in)[1];
    (out)[5] = (in)[5];
    (out)[6] = (in)[9];
    (out)[7] = 0.0;
    (out)[8] = (in)[2];
    (out)[9] = (in)[6];
    (out)[10] = (in)[10];
    (out)[11] = 0.0;
    (out)[12] = -((in)[0]*(in)[12] + (in)[1]*(in)[13] + (in)[2]*(in)[14]);
    (out)[13] = -((in)[4]*(in)[12] + (in)[5]*(in)[13] + (in)[6]*(in)[14]);
    (out)[14] = -((in)[8]*(in)[12] + (in)[9]*(in)[13] + (in)[10]*(in)[14]);
    (out)[15] = 1.0;
}






int SolveFK(const real_T *joints, real_T pose[16], const robot_T *ptr_robot) {
    std::cout << "Using custom/default SolveFK" << std::endl;
    // return -1; // Return -1 to use RoboDK default, return 1 for success, return 0 for target out of reach

    // Below is RoboDK's default calculation:

    // Retrieve the number of axes (degrees of freedom)
    int nDOFs = iRobot_nDOFs(ptr_robot);

    // Retrieve the robot lower and upper joint limits
    const real_T *joints_lim_lower = iRobot_JointLimLower(ptr_robot);
    const real_T *joints_lim_upper = iRobot_JointLimUpper(ptr_robot);
    const real_T *joints_senses = iRobot_JointSenses(ptr_robot);

    // Retrieve the robot base and tool flange adaptors (part of the kinematics, not the active frame and tool)
    real_T pose_base[16];
    real_T pose_tool[16];
    XYZWPR_2_Pose(iRobot_BaseXYZWPR(ptr_robot), pose_base);
    XYZWPR_2_Pose(iRobot_ToolXYZWPR(ptr_robot), pose_tool);

    // Matrices for operations
    real_T *last_pose = pose_base;
    real_T next_pose[16];


    // Iterate over all joints to calculate the forward kinematics as:
    // pose = pose_base * pose_j[0] * pose_j[1] * ... * pose_tool
    for (int i=0; i<nDOFs; i++){
        // Check if the joint value is within limits.
        // joints[i] is i mm or deg

        // Apply the sense of rotation (+1 or -1)
        real_T joint_i = joints[i]*joints_senses[i];
        if (joint_i < joints_lim_lower[i] || joint_i > joints_lim_upper[i]){
            return -2; // Return -1 to use RoboDK default, return 0 for success, return -2 for target out of reach
        }

        // Calculate the transofrmation for joint i
        const real_T *dhm_joint_i = iRobot_DHM_JointId(ptr_robot, i);
        // Add the transformation applied by the movement of the joint
        real_T rx_tx_rz_tz[4] = {dhm_joint_i[0], dhm_joint_i[1], dhm_joint_i[2], dhm_joint_i[3]};
        if (dhm_joint_i[4] == 0.0){
            // revolute joint
            rx_tx_rz_tz[2] = rx_tx_rz_tz[2] + joint_i * M_PI / 180.0;
        } else { // == 1.0
            // translation joint
            rx_tx_rz_tz[3] = rx_tx_rz_tz[3] + joint_i;
        }

        // Apply the pose of the joint i to the accumulated  final pose
        real_T pose_ji[16];
        DHM_2_Pose(rx_tx_rz_tz, pose_ji);
        Pose_Mult(last_pose, pose_ji, next_pose);
        last_pose = next_pose;
    }

    Pose_Mult(last_pose, pose_tool, pose);

    return 1; // Return -1 to use RoboDK default, return 0 for target out of reach, return 1 for success
}

int SolveFK_CAD(const real_T *joints, real_T pose[16], real_T *joint_poses, int max_poses, const robot_T *ptr_robot) {
    std::cout << "Using custom SolveFK_CAD" << std::endl;
    // return -1; // Return -1 to use RoboDK default, return 0 for success

    // Below is RoboDK's default calculation:

    // Retrieve the number of axes (degrees of freedom)
    int nDOFs = iRobot_nDOFs(ptr_robot);
    if (max_poses < nDOFs + 1){
        // RoboDK Must provide with a buffer large enough for all joints (at least nDOFs + 1)
        // If not, something went wrong, we could write past an allowed buffer
        std::cout << "Something went wrong with SolveFK_CAD" << std::endl;
        return -1;
    }

    const real_T *joints_senses = iRobot_JointSenses(ptr_robot);

    // Retrieve the robot base and tool flange adaptors (part of the kinematics, not the active frame and tool)
    real_T *pose_base = joint_poses + 16*0; // map the base pose to the origin
    real_T pose_tool[16];
    XYZWPR_2_Pose(iRobot_BaseXYZWPR(ptr_robot), pose_base);
    XYZWPR_2_Pose(iRobot_ToolXYZWPR(ptr_robot), pose_tool);

    // Matrices for operations
    real_T *last_pose = pose_base;
    //real_T *next_pose = joint_poses + 16*(joint_id+1);


    // Iterate over all joints to calculate the forward kinematics as:
    // pose = pose_base * pose_j[0] * pose_j[1] * ... * pose_tool
    for (int i=0; i<nDOFs; i++){
        // The joint limit check is irrelevant at this stage

        // Apply the sense of rotation (+1 or -1)
        real_T joint_i = joints[i]*joints_senses[i];

        // Calculate the transofrmation for joint i
        const real_T *dhm_joint_i = iRobot_DHM_JointId(ptr_robot, i);
        // Add the transformation applied by the movement of the joint
        real_T rx_tx_rz_tz[4] = {dhm_joint_i[0], dhm_joint_i[1], dhm_joint_i[2], dhm_joint_i[3]};
        if (dhm_joint_i[4] == 0.0){
            // revolute joint
            rx_tx_rz_tz[2] = rx_tx_rz_tz[2] + joint_i * M_PI / 180.0;
        } else { // == 1.0
            // translation joint
            rx_tx_rz_tz[3] = rx_tx_rz_tz[3] + joint_i;
        }

        // Apply the pose of the joint i to the accumulated  final pose
        real_T pose_ji[16];
        DHM_2_Pose(rx_tx_rz_tz, pose_ji);
        real_T *next_pose = joint_poses + 16*(i+1);
        Pose_Mult(last_pose, pose_ji, next_pose);
        last_pose = next_pose;
    }

    Pose_Mult(last_pose, pose_tool, pose);

    return 1; // Return -1 to use RoboDK default, return 0 for target out of reach, return 1 for success

    // return -1; // return -1 to use RoboDK default
}

int SolveIK(const real_T pose[16], real_T *joints, real_T *joints_all, int max_solutions, const real_T *joints_approx, const robot_T *ptr_robot) {
    std::cout << "Using custom SolveIK..." << std::endl;
    
    // Retrieve the number of axes (degrees of freedom)
    int nDOFs = iRobot_nDOFs(ptr_robot);
    
    // Random sample that outputs 2 joints solutions:
    // [0, 10, 20, 30, 40, 50]
    // [0, -10, -20, -30, -40, -50]
    
    // Define the number of solutions and map them to potential other solutions
    int n_solutions = 2;    
    real_T *solution_1 = joints_all;
    real_T *solution_2 = joints_all+12*1;    

    // Important: we should never exceed the buffer provided by max_solutions
    n_solutions = std::min(n_solutions, max_solutions);
    
    // Sample output 
    for (int i=0; i<6; i++){
        // This is the chosen solution
        joints[i] = i*10;
        
        // These are potential other solutions (the chosen solution should be within the other candidates):
        solution_1[i] = i*10;
        solution_2[i] = -i*10;
    }
    std::cout << "Done with SolveIK. Solutions: " << n_solutions << std::endl;
    return n_solutions;

    // Logic: Calculate inverse kinematics
    // Fill joints_all with up to max_solutions
    //return -1; returns the number of valid solutions (equal or less than max_solutions), if any. Returns 0 if there is no solution (for example: target out of reach), return -1 if we want to use the default iterative solution provided by RoboDK
}
