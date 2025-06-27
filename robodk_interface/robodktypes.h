#ifndef ROBODKTYPES_H
#define ROBODKTYPES_H


#include <QString>
#include <QtGui/QMatrix4x4>
#include <QDebug>

#include "matrix4x4.h"
#include "joints.h"


#ifndef M_PI
#define M_PI 3.14159265358979323846264338327950288
#endif


class IItem;
class IRoboDK;
typedef IItem* Item;
typedef IRoboDK RoboDK;




/// maximum size of robot joints (maximum allowed degrees of freedom for a robot)
#define RDK_SIZE_JOINTS_MAX 12
// IMPORTANT!! Do not change this value

/// Constant defining the size of a robot configuration (at least 3 doubles are required)
#define RDK_SIZE_MAX_CONFIG 4
// IMPORTANT!! Do not change this value


/// @brief tXYZWPR (mm, rad) holds the same information as a \ref tMatrix4x4 pose but represented as XYZ position (in mm) and WPR orientation (in rad) (XYZWPR = [X,Y,Z,W,P,R])
/// This type of variable is easier to read and it is what most robot controllers use to input a pose. However, for internal calculations it is better to use a 4x4 pose matrix as it is faster and more accurate.
/// To calculate a 4x4 matrix: pose4x4 = transl(X,Y,Z)*rotx(W)*roty(P)*rotz(R)
/// See \ref POSE_2_XYZWPR and \ref XYZWPR_2_POSE to exchange between \ref tMatrix4x4 and \ref tXYZWPR
typedef double tXYZWPR[6];

/// @brief tXYZ (mm) represents a position or a vector in mm
typedef double tXYZ[3];


/// @brief A robot configuration defines a specific state of the robot. It should be possible to accomplish a movement between two positions with the same robot configuration, without crossing any singularities.
/// Changing the robot configuration requires crossing a singularity.
/// For example, for a 6-axis robot there are 2x2x2=8 different configurations/solutions.
/// A robot configurations is also known as "Assembly mode".
/// <br>
/// The robot configuration is defined as an array of 3 doubles: [FACING REAR, LOWER ARM, WRIST FLIP].
/// <br>
/// FACING REAR=0 means FACING FRONT
/// <br>
/// LOWER ARM=0 means ELBOW UP
/// <br>
/// WRIST FLIP=0 means WRIST NON FLIP
/// <br>
/// the 4th value is reserved
typedef double tConfig[RDK_SIZE_MAX_CONFIG];



/// Calculate the dot product
#define DOT(v,q)   ((v)[0]*(q)[0] + (v)[1]*(q)[1] + (v)[2]*(q)[2])

/// Calculate the norm of a vector
#define NORM(v)   (sqrt((v)[0]*(v)[0] + (v)[1]*(v)[1] + (v)[2]*(v)[2]))

/// Normalize a vector (dimension 3)
#define NORMALIZE(inout){\
    double norm;\
    norm = sqrt((inout)[0]*(inout)[0] + (inout)[1]*(inout)[1] + (inout)[2]*(inout)[2]);\
    (inout)[0] = (inout)[0]/norm;\
    (inout)[1] = (inout)[1]/norm;\
    (inout)[2] = (inout)[2]/norm;}

/// Calculate the cross product
#define CROSS(out,a,b) \
    (out)[0] = (a)[1]*(b)[2] - (b)[1]*(a)[2]; \
    (out)[1] = (a)[2]*(b)[0] - (b)[2]*(a)[0]; \
    (out)[2] = (a)[0]*(b)[1] - (b)[0]*(a)[1];

/// Copy a 3D-array
#define COPY3(out,in)\
    (out)[0]=(in)[0];\
    (out)[1]=(in)[1];\
    (out)[2]=(in)[2];

/// Multiply 2 4x4 matrices
#define MULT_MAT(out,inA,inB)\
    (out)[0] = (inA)[0]*(inB)[0] + (inA)[4]*(inB)[1] + (inA)[8]*(inB)[2];\
    (out)[1] = (inA)[1]*(inB)[0] + (inA)[5]*(inB)[1] + (inA)[9]*(inB)[2];\
    (out)[2] = (inA)[2]*(inB)[0] + (inA)[6]*(inB)[1] + (inA)[10]*(inB)[2];\
    (out)[3] = 0;\
    (out)[4] = (inA)[0]*(inB)[4] + (inA)[4]*(inB)[5] + (inA)[8]*(inB)[6];\
    (out)[5] = (inA)[1]*(inB)[4] + (inA)[5]*(inB)[5] + (inA)[9]*(inB)[6];\
    (out)[6] = (inA)[2]*(inB)[4] + (inA)[6]*(inB)[5] + (inA)[10]*(inB)[6];\
    (out)[7] = 0;\
    (out)[8] = (inA)[0]*(inB)[8] + (inA)[4]*(inB)[9] + (inA)[8]*(inB)[10];\
    (out)[9] = (inA)[1]*(inB)[8] + (inA)[5]*(inB)[9] + (inA)[9]*(inB)[10];\
    (out)[10] = (inA)[2]*(inB)[8] + (inA)[6]*(inB)[9] + (inA)[10]*(inB)[10];\
    (out)[11] = 0;\
    (out)[12] = (inA)[0]*(inB)[12] + (inA)[4]*(inB)[13] + (inA)[8]*(inB)[14] + (inA)[12];\
    (out)[13] = (inA)[1]*(inB)[12] + (inA)[5]*(inB)[13] + (inA)[9]*(inB)[14] + (inA)[13];\
    (out)[14] = (inA)[2]*(inB)[12] + (inA)[6]*(inB)[13] + (inA)[10]*(inB)[14] + (inA)[14];\
    (out)[15] = 1;

/// Rotate a 3D vector (Multiply a 4x4 pose x 3D vector)
#define MULT_MAT_VECTOR(out,H,p)\
    (out)[0] = (H)[0]*(p)[0] + (H)[4]*(p)[1] + (H)[8]*(p)[2];\
    (out)[1] = (H)[1]*(p)[0] + (H)[5]*(p)[1] + (H)[9]*(p)[2];\
    (out)[2] = (H)[2]*(p)[0] + (H)[6]*(p)[1] + (H)[10]*(p)[2];

/// Translate a 3D point (Multiply a 4x4 pose x 3D point)
#define MULT_MAT_POINT(out,H,p)\
    (out)[0] = (H)[0]*(p)[0] + (H)[4]*(p)[1] + (H)[8]*(p)[2] + (H)[12];\
    (out)[1] = (H)[1]*(p)[0] + (H)[5]*(p)[1] + (H)[9]*(p)[2] + (H)[13];\
    (out)[2] = (H)[2]*(p)[0] + (H)[6]*(p)[1] + (H)[10]*(p)[2] + (H)[14];

    

/// The Color struct represents an RGBA color (each color component should be in the range [0-1])
struct tColor{
    /// Red color
    float r;

    /// Green color
    float g;

    /// Blue color
    float b;

    /// Alpha value (0 = transparent; 1 = opaque)
    float a;
};






//------------------------------------------------------------------------------------------------------------



/// \brief The tMatrix2D struct represents a variable size 2d Matrix. Use the Matrix2D_... functions to oeprate on this variable sized matrix.
/// This type of data can be used to get/set a program as a list. This is also useful for backwards compatibility functions related to RoKiSim.
struct tMatrix2D {
    /// Pointer to the data
    double *data;

    /// Pointer to the size array.
    int *size;

    /// Allocated size.
    int allocatedSize;

    /// Number of dimensions (usually 2)
    int numDimensions;

    bool canFreeData;
};




// -------------------------------------------


/// @brief Creates a new 2D matrix \ref Matrix2D.. Use \ref Matrix2D_Delete to delete the matrix (to free the memory).
/// The Procedure \ref Debug_Matrix2D shows an example to read data from a tMatrix2D
tMatrix2D* Matrix2D_Create();

/// @brief Deletes a \ref tMatrix2D.
/// @param[in] mat: Pointer of the pointer to the matrix
void Matrix2D_Delete(tMatrix2D **mat);

/// @brief Sets the size of a \ref tMatrix2D.
/// @param[in/out] mat: Pointer to the matrix
/// @param[in] rows: The number of rows.
/// @param[in] cols: The number of columns.
void Matrix2D_Set_Size(tMatrix2D *mat, int rows, int cols);

/// @brief Sets the size of a \ref tMatrix2D.
/// @param[in/out] mat: Pointer to the matrix
/// @param[in] dim: Dimension (1 or 2)
int Matrix2D_Size(const tMatrix2D *mat, int dim);

/// @brief Returns the number of columns of a \ref tMatrix2D.
/// @param[in] mat: Pointer to the matrix
/// Returns the number of columns (Second dimension)
int Matrix2D_Get_ncols(const tMatrix2D *var);

/// @brief Returns the number of rows of a \ref tMatrix2D.
/// @param[in] mat: Pointer to the matrix
/// Returns the number of rows (First dimension)
int Matrix2D_Get_nrows(const tMatrix2D *var);

/// @brief Returns the value at location [i,j] of a \ref tMatrix2D.
/// @param[in] mat: Pointer to the matrix
/// Returns the value of the cell
double Matrix2D_Get_ij(const tMatrix2D *var, int i, int j);

/// @brief Set the value at location [i,j] of a \ref tMatrix2D.
/// @param[in] mat: Pointer to the matrix
/// @param[in] i: Row
/// @param[in] j: Column
/// @param[in] value: matrix value
void Matrix2D_Set_ij(const tMatrix2D *var, int i, int j, double value);

/// @brief Returns the pointer of a column of a \ref tMatrix2D.
/// A column has \ref Matrix2D_Get_nrows(mat) values that can be accessed/modified from the returned pointer continuously.
/// @param[in] mat: Pointer to the matrix
/// @param[in] col: Column to retreive.
/// /return double array (internal pointer) to the column
double* Matrix2D_Get_col(const tMatrix2D *var, int col);

/// @brief Copy a Matrix2D
bool Matrix2D_Copy(const tMatrix2D *in, tMatrix2D *out);

/// @brief Show an array through STDOUT
/// Given an array of doubles, it generates a string
void Debug_Array(const double *array, int arraysize);

/// @brief Display the content of a \ref tMatrix2D through STDOUT. This is only intended for debug purposes.
/// @param[in] mat: Pointer to the matrix
void Debug_Matrix2D(const tMatrix2D *mat);

/// @brief Save a matrix as binary data
void Matrix2D_Save(QDataStream *st, tMatrix2D *emx);

/// @brief Save a matrix as text
void Matrix2D_Save(QTextStream *st, tMatrix2D *emx, bool csv=false);

/// @brief Load a matrix
void Matrix2D_Load(QDataStream *st, tMatrix2D **emx);


typedef robodk::Joints tJoints;

/*!
    \typedef Mat
    \brief The Mat class represents a 4x4 pose matrix.

    The main purpose of this object is to represent a pose
    in the 3D space (position and orientation).

    In other words, a pose is a 4x4 matrix that represents
    the position and orientation of one reference frame with
    respect to another one, in the 3D space.

    Poses are commonly used in robotics to place objects,
    reference frames and targets with respect to each other.

    <br>
    \f$ transl(x,y,z) rotx(r) roty(p) rotz(w) = \\
    \begin{bmatrix} n_x & o_x & a_x & x \\
    n_y & o_y & a_y & y \\
    n_z & o_z & a_z & z \\
    0 & 0 & 0 & 1 \end{bmatrix} \f$
*/
typedef robodk::Matrix4x4 Mat;

/// Translation matrix class: Mat::transl.
Mat transl(double x, double y, double z);

/// Translation matrix class: Mat::rotx.
Mat rotx(double rx);

/// Translation matrix class: Mat::roty.
Mat roty(double ry);

/// Translation matrix class: Mat::rotz.
Mat rotz(double rz);

//QDataStream &operator<<(QDataStream &data, const QMatrix4x4 &);
inline QDebug operator<<(QDebug dbg, const Mat &m){ return dbg.noquote() << m.ToString(); }
inline QDebug operator<<(QDebug dbg, const tJoints &jnts){ return dbg.noquote() << jnts.ToString(); }

inline QDebug operator<<(QDebug dbg, const Mat *m){ return dbg.noquote() << (m == nullptr ? "Mat(null)" : m->ToString()); }
inline QDebug operator<<(QDebug dbg, const tJoints *jnts){ return dbg.noquote() << (jnts == nullptr ? "tJoints(null)" : jnts->ToString()); }



#endif // ROBODKTYPES_H
