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


#include "deprecated.h"
#include "vector3.h"


#ifdef QT_GUI_LIB
#include <QString>
#include <QMatrix4x4>

namespace robodk
{
typedef ::QMatrix4x4 BaseMatrix4x4;
}
#else // QT_GUI_LIB
#error "This class cannot yet be used without the Qt Framework"
#endif // QT_GUI_LIB


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
    - Values()
    - ValuesD()
    - ValuesF()
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
        Constructs this Matrix4x4 object as a copy of \a matrix.
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

    /*!
        Sets the X vector (N vector).
    */
    void SetVX(const Vector3& n);

    /*!
        Sets the Y vector (O vector).
    */
    void SetVY(const Vector3& o);

    /*!
        Sets the Z vector (A vector).
    */
    void SetVZ(const Vector3& a);

    /*!
        Sets the X vector values (N vector).
    */
    void SetVX(double x, double y, double z);

    /*!
        Sets the Y vector values (O vector).
    */
    void SetVY(double x, double y, double z);

    /*!
        Sets the Z vector values (A vector).
    */
    void SetVZ(double x, double y, double z);

    /*!
        Sets the position (T).
    */
    void SetPos(double x, double y, double z);

    /*!
        Sets the X vector values (N vector).
    */
    void SetVX(const double* xyz);

    /*!
        Sets the Y vector values (O vector).
    */
    void SetVY(const double* xyz);

    /*!
        Sets the Z vector values (A vector).
    */
    void SetVZ(const double* xyz);

    /*!
        Sets the position (T).
    */
    void SetPos(const double* xyz);

    /*!
        \brief Sets the elements of matrix from the given 16 double-precision \a values.

        The contents of the array \a values is assumed to be in \b column-major order.

        \f$ \begin{bmatrix}
            v_1 & v_5 & v_9    & v_{13} \\
            v_2 & v_6 & v_{10} & v_{14} \\
            v_3 & v_7 & v_{11} & v_{15} \\
            v_4 & v_8 & v_{12} & v_{16}
        \end{bmatrix} \f$

        \param values
            \f$ \begin{bmatrix}
                v_1 & v_2 & v_3 & v_4 & v_5 & v_6 & v_7 & v_8 &
                v_9 & v_{10} & v_{11} & v_{12} & v_{13} & v_{14} & v_{15} & v_{16}
            \end{bmatrix} \f$
    */
    void SetValues(const double* values);

    /*!
        Returns the X vector (N vector).
    */
    Vector3 VX() const;

    /*!
        Returns the Y vector (O vector).
    */
    Vector3 VY() const;

    /*!
        Returns the Z vector (A vector).
    */
    Vector3 VZ() const;

    /*!
        Writes the X vector (N vector) into array of 3 double-precision \a xyz values.
    */
    void VX(double* xyz) const;

    /*!
        Writes the Y vector (O vector) into array of 3 double-precision \a xyz values.
    */
    void VY(double* xyz) const;

    /*!
        Writes the Z vector (A vector) into array of 3 double-precision \a xyz values.
    */
    void VZ(double* xyz) const;

    /*!
        Writes the position (T vector) into array of 3 double-precision \a xyz values.
    */
    void Pos(double* xyz) const;

    /*!
        Sets a new \a value to the element at position (\a row, \a column) in this matrix.
    */
    void Set(int row, int column, double value);

    /*!
        Returns the value of the element at position (\a row, \a column) in this matrix.
    */
    double Get(int row, int column) const;

    /*!
        Returns the inverse of this matrix. Returns the identity if
        this matrix cannot be inverted; i.e. determinant() is zero.
    */
    Matrix4x4 Inverted(bool* invertible = nullptr) const;

    /*!
        Returns \c true if the matrix is homogeneous; false otherwise.
    */
    bool IsHomogeneous() const;

    /*!
        \brief Forces this matrix to be homogeneous.
        The \a vx, \a vy, \a vz must be unitary vectors and respect: vx x vy = vz.
        Returns \c true if the matrix was not homogeneous and it was modified to be homogeneous.
    */
    bool MakeHomogeneous();

    /*!
        \brief Calculates the position and euler angles ([x,y,z,r,p,w] vector) from this matrix.

        Note: transl(x, y, z) * rotz(w * pi / 180) * roty(p * pi / 180) * rotx(r * pi / 180)

        \returns The XYZWPR translation and rotation in the length units and degrees.
        \sa FromXYZRPW()
    */
    void ToXYZRPW(double* xyzwpr) const;

    /*!
        \brief Calculates this matrix from the position and euler angles ([x,y,z,r,p,w] vector).

        The result is the same as:
        H = transl(x, y, z) * rotz(w * pi / 180) * roty(p * pi / 180) * rotx(r * pi / 180)

        \sa ToXYZRPW()
    */
    void FromXYZRPW(const double* xyzwpr);


    /*!
        \brief Constructs a matrix from the position and euler angles ([x,y,z,r,p,w] vector).

        The result is the same as:
        H = transl(x, y, z) * rotz(w * pi / 180) * roty(p * pi / 180) * rotx(r * pi / 180)

        \returns New homogeneous Matrix4x4 object.

        \sa FromXYZRPW()
    */
    static Matrix4x4 XYZRPW_2_Mat(double x, double y, double z, double r, double p, double w);

    /*!
        \brief Constructs a matrix from the position and euler angles ([x,y,z,r,p,w] vector).

        The result is the same as:
        H = transl(x, y, z) * rotz(w * pi / 180) * roty(p * pi / 180) * rotx(r * pi / 180)

        \returns New homogeneous Matrix4x4 object.

        \sa FromXYZRPW()
    */
    static Matrix4x4 XYZRPW_2_Mat(const double* xyzwpr);

    /*!
        Returns a constant pointer to the raw data of this matrix as 16 double-precision numbers.
        This raw data is stored in column-major format.

        \sa Values(), ValuesF()
    */
    const double* ValuesD() const;

    /*!
        Returns a constant pointer to the raw data of this matrix as 16 single-precision numbers.
        This raw data is stored in column-major format.

        \sa Values(), ValuesD()
    */
    const float* ValuesF() const;

#ifdef ROBODK_API_FLOATS
    /*!
        Returns a constant pointer to the raw data of this matrix as
        16 double- or single-precision numbers.
        This raw data is stored in column-major format.

        \sa ValuesF(), ValuesD()
    */
    const float* Values() const;
#else
    /*!
        Returns a constant pointer to the raw data of this matrix as
        16 double- or single-precision numbers.
        This raw data is stored in column-major format.

        \sa ValuesF(), ValuesD()
    */
    const double* Values() const;
#endif

    /*!
        Writes the contents of this matrix into array of 16 double-precision \a values.

        \sa Values(), ValuesF(), ValuesD()
    */
    void Values(double* values) const;

    /*!
        Writes the contents of this matrix into array of 16 single-precision \a values.

        \sa Values(), ValuesF(), ValuesD()
    */
    void Values(float* values) const;

    /*!
        Returns \c true if the matrix is marked as valid; false otherwise.
    */
    bool Valid() const;

    /*!
        Sets this Matrix4x4 object as a copy of \a matrix.
    */
    Matrix4x4& operator=(const Matrix4x4& matrix);

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
    static Matrix4x4 transl(double x, double y, double z);

    /*!
        \brief Constructs a matrix that rotates coordinates around X axis.
        \param rx rotation angle in radians.

        \returns New Matrix4x4 object with the following structure:
            \f$ \begin{bmatrix}
                1 & 0       & 0         & 0 \\
                0 & \cos rx & - \sin rx & 0 \\
                0 & \sin rx & \cos rx   & 0 \\
                0 & 0       & 0         & 1
            \end{bmatrix} \f$
    */
    static Matrix4x4 rotx(double rx);

    /*!
        \brief Constructs a matrix that rotates coordinates around Y axis.
        \param ry rotation angle in radians.

        \returns New Matrix4x4 object with the following structure:
            \f$ \begin{bmatrix}
                \cos ry   & 0 & \sin ry & 0 \\
                0         & 1 & 0       & 0 \\
                - \sin ry & 0 & \cos ry & 0 \\
                0         & 0 & 0       & 1
            \end{bmatrix} \f$
    */
    static Matrix4x4 roty(double ry);

    /*!
        \brief Constructs a matrix that rotates coordinates around Z axis.
        \param rz rotation angle in radians.

        \returns New Matrix4x4 object with the following structure:
            \f$ \begin{bmatrix}
                \cos rz & - \sin rz & 0 & 0 \\
                \sin rz & \cos rx   & 0 & 0 \\
                0       & 0         & 1 & 0 \\
                0       & 0         & 0 & 1
            \end{bmatrix} \f$
    */
    static Matrix4x4 rotz(double rz);

#ifdef QT_GUI_LIB
    /*!
        Constructs this Matrix4x4 object as a copy of \a matrix.
    */
    Matrix4x4(const BaseMatrix4x4& matrix);

    /*!
        Returns string representation of this matrix.
        \sa ToString()
    */
    inline operator QString() const { return ToString(); }

    /// Set the matrix given a XYZRPW string array (6-values)
    bool FromString(const QString& str);


    /*!
        Returns string representation of this matrix with each element separated by
        the given \a separator (which can be an empty string).
        \param separator string that separates elements of the matrix.
        \param precision represents the number of digits after the decimal point.
        \param xyzrpwOnly if set to \s true, the pose will be represented as
        XYZWPR 6-dimensional array using ToXYZRPW().
    */
    QString ToString(
        const ::QString& separator = QLatin1String(", "),
        int precision = 3,
        bool xyzrpwOnly = false) const;

    /*!
        Sets this Matrix4x4 object as a copy of \a matrix.
    */
    Matrix4x4& operator=(const QMatrix4x4& matrix);
#endif

    /* Deprecated methods */
public:
    ROBODK_DEPRECATED("Use Inverted() instead")
    inline Matrix4x4 inv() { return Inverted(); }

    ROBODK_DEPRECATED("Use SetPos() instead")
    inline void setPos(double x, double y, double z) { SetPos(x, y, z); }



private:
    /*! \cond */

    double _valid;
    mutable double _md[16];

    /*! \endcond */
};

} // namespace robodk


#endif // ROBODK_MATRIX4X4_H
