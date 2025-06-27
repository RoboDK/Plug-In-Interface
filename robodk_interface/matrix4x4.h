/****************************************************************************
**
** Copyright (c) 2015-2025 RoboDK Inc.
** Contact: https://robodk.com/
**
** This file is part of the RoboDK API.
**
** Permission is hereby granted, free of charge, to any person obtaining a copy
** of this software and associated documentation files (the "Software"), to deal
** in the Software without restriction, including without limitation the rights
** to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
** copies of the Software, and to permit persons to whom the Software is
** furnished to do so, subject to the following conditions:
**
** The above copyright notice and this permission notice shall be included in all
** copies or substantial portions of the Software.
**
** THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
** IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
** FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
** AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
** LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
** OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
** SOFTWARE.
**
** RoboDK is a registered trademark of RoboDK Inc.
**
****************************************************************************/

#ifndef ROBODK_MATRIX4X4_H
#define ROBODK_MATRIX4X4_H


#include "vector3.h"


#ifdef QT_GUI_LIB
#include <QString>
#include <QMatrix4x4>

namespace robodk
{
typedef ::QMatrix4x4 BaseMatrix4x4;
}
#else
#error "This class cannot yet be used without the Qt Framework"
#endif


namespace robodk
{

/*!
    \class Matrix4x4
    \brief The Matrix4x4 class represents a 4x4 transformation matrix in 3D space.

    The Matrix4x4 class in general is treated as a row-major matrix, in that the
    constructors and operator() functions take data in row-major format, as is
    familiar in C-style usage.

    Internally the data is stored as column-major format.

    When using these functions be aware that they return data in \b column-major format:
    - data()
    - constData()
*/
class Matrix4x4 : public BaseMatrix4x4
{
public:
    /*!
        Constructs an identity matrix.
    */
    Matrix4x4();

    /*!
        Constructs a valid or an invalid identity matrix.
    */
    explicit Matrix4x4(bool valid);

    /*!
        Constructs this Matrix4x4 object as a copy of matrix.
    */
    Matrix4x4(const Matrix4x4& matrix);

    /*!
        \brief Constructs a matrix from the given 16 double-precision \a values.

        The contents of the array \a values is assumed to be in \b column-major order.

        \param values
            \f$ \begin{bmatrix}
                v_1 & v_2 & v_3 & v_4 & v_5 & v_6 & v_7 & v_8 &
                v_9 & v_{10} & v_{11} & v_{12} & v_{13} & v_{14} & v_{15} & v_{16}
            \end{bmatrix} \f$

        \returns New Matrix4x4 object with the following structure:
            \f$ \begin{bmatrix}
                v_1 & v_5 & v_9    & v_{13} \\
                v_2 & v_6 & v_{10} & v_{14} \\
                v_3 & v_7 & v_{11} & v_{15} \\
                v_4 & v_8 & v_{12} & v_{16}
            \end{bmatrix} \f$
    */
    Matrix4x4(const double* values);

    /*!
        \brief Constructs a matrix from the given 16 single-precision \a values.

        The contents of the array \a values is assumed to be in \b column-major order.

        \param values
            \f$ \begin{bmatrix}
                v_1 & v_2 & v_3 & v_4 & v_5 & v_6 & v_7 & v_8 &
                v_9 & v_{10} & v_{11} & v_{12} & v_{13} & v_{14} & v_{15} & v_{16}
            \end{bmatrix} \f$

        \returns New Matrix4x4 object with the following structure:
            \f$ \begin{bmatrix}
                v_1 & v_5 & v_9    & v_{13} \\
                v_2 & v_6 & v_{10} & v_{14} \\
                v_3 & v_7 & v_{11} & v_{15} \\
                v_4 & v_8 & v_{12} & v_{16}
            \end{bmatrix} \f$
    */
    Matrix4x4(const float* values);

    /*!
        \brief Constructs a matrix that translates coordinates by the components
        \a x, \a y, and \a z.

        \returns New Matrix4x4 object with the following structure:
            \f$ \begin{bmatrix}
                1 & 0 & 0 & x \\
                0 & 1 & 0 & y \\
                0 & 0 & 1 & z \\
                0 & 0 & 0 & 1
            \end{bmatrix} \f$
    */
    Matrix4x4(double x, double y, double z);

    /*!
        \brief Constructs a matrix from the \a N, \a O, \a A, \a T vector components.

        \returns New Matrix4x4 object with the following structure:
            \f$ \begin{bmatrix}
                n_x & o_x & a_x & t_x \\
                n_y & o_y & a_y & t_y \\
                n_z & o_z & a_z & t_z \\
                0   & 0   & 0   & 1
            \end{bmatrix} \f$
    */
    Matrix4x4(
        double nx,
        double ox,
        double ax,
        double tx,
        double ny,
        double oy,
        double ay,
        double ty,
        double nz,
        double oz,
        double az,
        double tz);

    ~Matrix4x4() = default;

    /// Set the X vector values (N vector)
    void setVX(const Vector3& n);

    /// Set the Y vector values (O vector)
    void setVY(const Vector3& o);

    /// Set the Z vector values (A vector)
    void setVZ(const Vector3& a);

    /// Set the X vector values (N vector)
    void setVX(double x, double y, double z);

    /// Set the Y vector values (O vector)
    void setVY(double x, double y, double z);

    /// Set the Z vector values (A vector)
    void setVZ(double x, double y, double z);

    /// Set the position (T position) in mm
    void setPos(double x, double y, double z);

    /// Set the X vector values (N vector)
    void setVX(const double* xyz);

    /// Set the Y vector values (O vector)
    void setVY(const double* xyz);

    /// Set the Z vector values (A vector)
    void setVZ(const double* xyz);

    /// Set the position (T position) in mm
    void setPos(const double* xyz);

    /// Set the pose values
    void setValues(const double* values);

    /// Get the X vector (N vector)
    Vector3 vx() const;

    /// Get the Y vector (O vector)
    Vector3 vy() const;

    /// Get the Z vector (A vector)
    Vector3 vz() const;

    /// Get the X vector (N vector)
    void VX(double* xyz) const;

    /// Get the Y vector (O vector)
    void VY(double* xyz) const;

    /// Get the Z vector (A vector)
    void VZ(double* xyz) const;

    /// Get the position (T position), in mm
    void Pos(double* xyz) const;

    /// \brief Set a matrix value
    /// \param r row
    /// \param c column
    /// \param value value
    void Set(int r, int c, double value);

    /// \brief Get a matrix value
    /// \param r row
    /// \param c column
    /// \return value
    double Get(int r, int c) const;

    /// Invert the pose (homogeneous matrix assumed)
    Matrix4x4 inv() const;

    /// Returns true if the matrix is homogeneous, otherwise it returns false
    bool isHomogeneous() const;

    /// Forces 4x4 matrix to be homogeneous (vx,vy,vz must be unitary vectors and respect: vx x vy = vz). Returns True if the matrix was not homogeneous and it was be modified to make it homogeneous.
    bool MakeHomogeneous();

    /// <summary>
    /// Calculates the equivalent position and euler angles ([x,y,z,r,p,w] vector) of the given pose
    /// Note: transl(x,y,z)*rotz(w*pi/180)*roty(p*pi/180)*rotx(r*pi/180)
    /// See also: FromXYZRPW()
    /// </summary>
    /// <returns>XYZWPR translation and rotation in mm and degrees</returns>
    void ToXYZRPW(double* xyzwpr) const;

    /// <summary>
    /// Calculates the pose from the position and euler angles ([x,y,z,r,p,w] vector)
    /// The result is the same as:
    /// <br>
    /// H = transl(x,y,z)*rotz(w*pi/180)*roty(p*pi/180)*rotx(r*pi/180)
    /// </summary>
    /// <returns>Homogeneous matrix (4x4)</returns>
    void FromXYZRPW(const double* xyzwpr);

    /// <summary>
    /// Calculates the pose from the position and euler angles ([x,y,z,r,p,w] vector)
    /// The result is the same as:
    /// <br>
    /// H = transl(x,y,z)*rotz(w*pi/180)*roty(p*pi/180)*rotx(r*pi/180)
    /// </summary>
    /// <returns>Homogeneous matrix (4x4)</returns>
    static Matrix4x4 XYZRPW_2_Mat(double x, double y, double z, double r, double p, double w);
    static Matrix4x4 XYZRPW_2_Mat(const double* xyzwpr);

    /// Get a pointer to the 16-digit double array.
    const double* ValuesD() const;

    /// Get a pointer to the 16-digit array as an array of floats.
    const float* ValuesF() const;

#ifdef ROBODK_API_FLOATS
    /// Get a pointer to the 16-digit array (doubles or floats if ROBODK_API_FLOATS is defined).
    const float* Values() const;
#else
    /// Get a pointer to the 16-digit array (doubles or floats if ROBODK_API_FLOATS is defined).
    const double* Values() const;
#endif

    /// Copy the 16-values of the 4x4 matrix to a double array.
    void Values(double values[16]) const;

    /// Copy the 16-values of the 4x4 matrix to a double array.
    void Values(float values[16]) const;

    /// Check if the matrix is valid
    bool Valid() const;

    Matrix4x4& operator=(const Matrix4x4& matrix);

    /// <summary>
    /// Return a translation matrix.
    /// </summary>
    /// <param name="x">translation along X (mm)</param>
    /// <param name="y">translation along Y (mm)</param>
    /// <param name="z">translation along Z (mm)</param>
    /// <returns>
    /// \f$ rotx(\theta) = \begin{bmatrix} 1 & 0 & 0 & x \\
    /// 0 & 1 & 0 & y \\
    /// 0 & 0 & 1 & z \\
    /// 0 & 0 & 0 & 1 \\
    /// \end{bmatrix} \f$
    /// </returns>
    static Matrix4x4 transl(double x, double y, double z);

    /// <summary>
    /// Return the X-axis rotation matrix.
    /// </summary>
    /// <param name="rx">Rotation around X axis (in radians).</param>
    /// <returns>
    /// \f$ rotx(\theta) = \begin{bmatrix} 1 & 0 & 0 & 0 \\
    /// 0 & c_\theta & -s_\theta & 0 \\
    /// 0 & s_\theta & c_\theta & 0 \\
    /// 0 & 0 & 0 & 1 \\
    /// \end{bmatrix} \f$
    /// </returns>
    static Matrix4x4 rotx(double rx);

    /// <summary>
    /// Return a Y-axis rotation matrix
    /// </summary>
    /// <param name="ry">Rotation around Y axis (in radians)</param>
    /// <returns>
    /// \f$ roty(\theta) = \begin{bmatrix} c_\theta & 0 & s_\theta & 0 \\
    /// 0 & 1 & 0 & 0 \\
    /// -s_\theta & 0 & c_\theta & 0 \\
    /// 0 & 0 & 0 & 1 \\
    /// \end{bmatrix} \f$
    /// </returns>
    static Matrix4x4 roty(double ry);

    /// <summary>
    /// Return a Z-axis rotation matrix.
    /// </summary>
    /// <param name="rz">Rotation around Z axis (in radians)</param>
    /// <returns>
    /// \f$ rotz(\theta) = \begin{bmatrix} c_\theta & -s_\theta & 0 & 0 \\
    /// s_\theta & c_\theta & 0 & 0 \\
    /// 0 & 0 & 1 & 0 \\
    /// 0 & 0 & 0 & 1 \\
    /// \end{bmatrix} \f$
    /// </returns>
    static Matrix4x4 rotz(double rz);

#ifdef QT_GUI_LIB
    /// Create a copy of the matrix
    Matrix4x4(const BaseMatrix4x4& matrix);

    /// To String operator (use with qDebug() << tJoints;
    inline operator QString() const { return ToString(); }

    /// Set the matrix given a XYZRPW string array (6-values)
    bool FromString(const QString &str);

    /// \brief Retrieve a string representation of the pose
    /// \param separator String separator
    /// \param precision Number of decimals
    /// \param in_xyzwpr if set to true (default), the pose will be represented as XYZWPR 6-dimensional array using ToXYZRPW
    /// \return
    QString ToString(
        const ::QString& separator = QLatin1String(", "),
        int precision = 3,
        bool xyzrpw_only = false) const;

    Matrix4x4& operator=(const QMatrix4x4& matrix);
#endif

private:
    /*! \cond */

    double _valid;
    mutable double _md[16];

    /*! \endcond */
};

} // namespace robodk


#endif // ROBODK_MATRIX4X4_H
