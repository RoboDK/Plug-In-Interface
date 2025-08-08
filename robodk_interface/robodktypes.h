#ifndef ROBODKTYPES_H
#define ROBODKTYPES_H


#include <QString>
#include <QtGui/QMatrix4x4>
#include <QDebug>

#include "matrix4x4.h"
#include "legacymatrix2d.h"
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



typedef robodk::legacy::Matrix2D tMatrix2D;

/*!
    Creates a new \ref Matrix2D object with no dimensions.

    \returns pointer to the Matrix2D object if no allocation errors occurred; nullptr otherwise.

    \sa Matrix2D_Delete()
*/
inline tMatrix2D* Matrix2D_Create()
{
    return robodk::legacy::Matrix2D_Create();
}

/*!
    Deletes an existing \ref Matrix2D object.

    \param matrix pointer of the pointer variable to the matrix object.

    \sa Matrix2D_Create()
*/
inline void Matrix2D_Delete(tMatrix2D** matrix)
{
    robodk::legacy::Matrix2D_Delete(matrix);
}

/*!
    Sets new dimensions for existing matrix object.

    \param matrix pointer to the matrix object.
    \param rows number of rows.
    \param columns number of columns.

    \sa Matrix2D_Size()
*/
inline void Matrix2D_Set_Size(tMatrix2D* matrix, int rows, int columns)
{
    robodk::legacy::Matrix2D_SetDimensions(matrix, rows, columns);
}

/*!
    Returns \a dimension (number of rows or columns) of \a matrix.

    \deprecated Use \ref Matrix2D_ColumnCount() and \ref Matrix2D_RowCount() instead of this one.

    \param matrix pointer to the matrix object.
    \param dimension may have a value of 1 or 2 to retrieve number of
        rows or columns respectively.

    \sa Matrix2D_Set_Size(), Matrix2D_Get_ncols(), Matrix2D_Get_nrows()
*/
inline int Matrix2D_Size(const tMatrix2D* matrix, int dimension)
{
    return robodk::legacy::Matrix2D_GetDimension(matrix, dimension);
}

/*!
    Returns the total number of columns in the \a matrix.

    \sa Matrix2D_Set_Size(), Matrix2D_Get_nrows()
*/
inline int Matrix2D_Get_ncols(const tMatrix2D* matrix)
{
    return robodk::legacy::Matrix2D_ColumnCount(matrix);
}

/*!
    Returns the total number of rows in the \a matrix.

    \sa Matrix2D_Set_Size(), Matrix2D_Get_ncols()
*/
inline int Matrix2D_Get_nrows(const tMatrix2D* matrix)
{
    return robodk::legacy::Matrix2D_RowCount(matrix);
}

/*!
    Returns the value of the element at position (\a row, \a column) in the \a matrix.
*/
inline double Matrix2D_Get_ij(const tMatrix2D* matrix, int row, int column)
{
    return robodk::legacy::Matrix2D_Get(matrix, row, column);
}

/*!
    Sets a new \a value to the element at position (\a row, \a column) in the \a matrix.
*/
inline void Matrix2D_Set_ij(const tMatrix2D* matrix, int row, int column, double value)
{
    robodk::legacy::Matrix2D_Set(matrix, row, column, value);
}

/*!
    Returns the elements of \a column as a pointer to its values in the \a matrix.
*/
inline double* Matrix2D_Get_col(const tMatrix2D* matrix, int column)
{
    return robodk::legacy::Matrix2D_GetColumn(matrix, column);
}

/*!
    \brief Copies the matrix \a source to the \a destination.

    Both matrices must be initialized and have the same size.

    \returns true if successful; otherwise returns false.
*/
inline bool Matrix2D_Copy(const tMatrix2D* source, tMatrix2D* destination)
{
    return robodk::legacy::Matrix2D_Copy(source, destination);
}

/*!
    Writes the contents of the \a array with \a size elements using qDebug().
*/
inline void Debug_Array(const double* array, int size)
{
    robodk::legacy::Matrix2D_DebugArray(array, size);
}

/*!
    Writes the contents of the \a matrix using qDebug().
*/
inline void Debug_Matrix2D(const tMatrix2D* matrix)
{
    robodk::legacy::Matrix2D_Debug(matrix);
}

/*!
    \brief Writes the contents of the \a matrix into text \a stream.

    The values can be written in the CSV format.
*/
inline void Matrix2D_Save(QTextStream* stream, tMatrix2D* matrix, bool csv = false)
{
    robodk::legacy::Matrix2D_Save(stream, matrix, csv);
}

/*!
    Writes the contents of the \a matrix into binary \a stream.
*/
inline void Matrix2D_Save(QDataStream* stream, tMatrix2D* matrix)
{
    robodk::legacy::Matrix2D_Save(stream, matrix);
}

/*!
    Creates a new \ref Matrix2D object by loading its contents from a binary \a stream.
*/
inline void Matrix2D_Load(QDataStream* stream, tMatrix2D** matrix)
{
    robodk::legacy::Matrix2D_Load(stream, matrix);
}


typedef robodk::Joints tJoints;
typedef robodk::Matrix4x4 Mat;

inline Mat transl(double x, double y, double z)
{
    return Mat::transl(x,y,z);
}

inline Mat rotx(double rx)
{
    return Mat::rotx(rx);
}

inline Mat roty(double ry)
{
    return Mat::roty(ry);
}

inline Mat rotz(double rz)
{
    return Mat::rotz(rz);
}


inline QDebug operator<<(QDebug dbg, const Mat &m)
{
    return dbg.noquote() << m.ToString();
}

inline QDebug operator<<(QDebug dbg, const tJoints &jnts)
{
    return dbg.noquote() << jnts.ToString();
}

inline QDebug operator<<(QDebug dbg, const Mat *m)
{
    return dbg.noquote() << (m == nullptr ? "Mat(null)" : m->ToString());
}

inline QDebug operator<<(QDebug dbg, const tJoints *jnts)
{
    return dbg.noquote() << (jnts == nullptr ? "tJoints(null)" : jnts->ToString());
}


#endif // ROBODKTYPES_H
