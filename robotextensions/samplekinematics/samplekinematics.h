#ifndef SAMPLEKINEMATICS_H
#define SAMPLEKINEMATICS_H


#if defined(_MSC_VER) || defined(WIN64) || defined(_WIN64) || defined(__WIN64__) || defined(WIN32) || defined(_WIN32) || defined(__WIN32__) || defined(__NT__)
#define MYLIB_EXPORT __declspec(dllexport)
#define MYLIB_IMPORT __declspec(dllimport)
#else
#define MYLIB_EXPORT __attribute__((visibility("default")))
#define MYLIB_IMPORT __attribute__((visibility("default")))
#endif



// Define real_T if not already defined by your environment
typedef double real_T;
typedef void robot_T;

extern "C" {

/*!
 * \brief SolveFK
 * Calculate the forward kinematics solution: provided a set of joints in mm/deg calculates the pose of the end effector with repect to the robot base (Matrix4x4/pose[16])
 * \param joints
 * robot joints in mm or deg
 * \param pose
 * forward kinematics solution. Values are a 16-double array [nx,ny,nz,0, ox,oy,oz,0, ax,ay,az,0, x,y,z,1]
 * \param ptr_robot
 * pointer to the robot parameters, if any
 * \return returns 1 if the solution is valid, returns 0 if there is no solution (such as joints out of limits), return -1 if we want to use the default/generic forward kinematics of RoboDK
 */
MYLIB_EXPORT int SolveFK(const real_T *joints, real_T *pose, const robot_T *ptr_robot);


/*!
 * \brief SolveFK_CAD
 * Calculate the forward kinematics solution including the poses for all joints: this function is similar to SolveFK but it is used to display the 3D model.
 * \param joints
 * robot joints (in mm or deg)
 * \param pose
 * forward kinematics solution. Values are a 16-double array [nx,ny,nz,0, ox,oy,oz,0, ax,ay,az,0, x,y,z,1]
 * \param joint_poses
 * array of poses packed as a multiple of 16*nposes
 * \param max_poses
 * number of poses available or that must be set
 * \param ptr_robot
 * pointer to the robot parameters, if any.
 * \return Returns 1 if the solution is valid, returns 0 if there is no solution (such as joints out of limits), return -1 if we want to use the default/generic forward kinematics of RoboDK
 */
MYLIB_EXPORT int SolveFK_CAD(const real_T *joints, real_T *pose, real_T *joint_poses, int max_poses, const robot_T *ptr_robot);



/*!
 * \brief Calculate the inverse kinematics solution: calculates the robot joints given the pose of the robot flange with respect to the robot base
 * \param pose
 * pose of the robot. Values are a 16-double array [nx,ny,nz,0, ox,oy,oz,0, ax,ay,az,0, x,y,z,1]
 * \param joints
 * robot joints solution in mm or deg
 * \param joints_all
 * list of optional solutions in mm or deg as a 12*n_solutions array (it should include the joints solution)
 * \param max_solutions
 * maximum number of solution. This is the size of the joints_all solutions buffer. For example, if max_solutions is 8, you can provide up to 8 valid solutions (8x12 array)
 * \param joints_approx
 * These joints hold the current robot joints. This can be used as a hint to obtain or choose a solution.
 * \param ptr_robot
 * pointer to the robot parameters, if any.
 * \return returns the number of valid solutions (equal or less than max_solutions), if any. Returns 0 if there is no solution (for example: target out of reach), return -1 if we want to use the default iterative solution provided by RoboDK
 */
MYLIB_EXPORT int SolveIK(const real_T *pose, real_T *joints, real_T *joints_all, int max_solutions, const real_T *joints_approx, const robot_T *ptr_robot);

}




#endif // SAMPLEKINEMATICS_H
