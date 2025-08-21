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

#ifndef ROBODK_JOINTS_H
#define ROBODK_JOINTS_H


#ifdef QT_GUI_LIB
#include <QString>
#else
#error "This class cannot yet be used without the Qt Framework"
#endif


namespace robodk
{

namespace legacy
{
struct Matrix2D;
}

/// The Joints class represents a joint position of a robot (robot axes).
class Joints
{
public:
    /// \brief Joints
    Joints();

    /// \brief Joints
    /// \param ndofs number of robot joint axes or degrees of freedom
    explicit Joints(int ndofs);

    /// \brief Set joint values given a double array and the number of joint values
    /// \param joints Pointer to the joint values
    /// \param ndofs Number of joints
    Joints(const double* joints, int ndofs = 0);

    /// \brief Set joint values given a float array and the number of joint values
    /// \param joints Pointer to the joint values
    /// \param ndofs Number of joints
    Joints(const float* joints, int ndofs = 0);

    /// \brief Create a copy of an object
    /// \param jnts
    Joints(const Joints& joints) = default;

    Joints& operator=(const Joints& joints) = default;

    /// \brief Create joint values given a 2D matrix and the column selecting the desired values
    /// \param mat2d
    /// \param column
    /// \param ndofs
    Joints(const legacy::Matrix2D* mat2d, int column = 0, int ndofs = -1);

    /// \brief Convert a string to joint values
    /// \param str Comma separated joint values (spaces or tabs are also accepted)
    Joints(const QString& str);

    ~Joints() = default;

    /// \brief Joint values
    /// \return Returns a pointer to the joint data array (doubles)
    const double* ValuesD() const;

    /// \brief Joint values
    /// \return Returns a pointer to the joint data array (floats)
    const float* ValuesF() const;

#ifdef ROBODK_API_FLOATS
    /// \brief Joint values
    /// \return Returns a pointer to the joint data array (doubles or floats if ROBODK_API_FLOATS is defined)
    const float* Values() const;
#else
    /// \brief Joint values
    /// \return Returns a pointer to the joint data array (doubles or floats if ROBODK_API_FLOATS is defined)
    const double* Values() const;
#endif


    double Compare(const Joints &other) const;

    /// \brief
    /// \return Data same as Values. The only difference is that the array pointer is not const. This is provided for backwards compatibility.
    double *Data();

    /// \brief Number of joint axes of the robot (or degrees of freedom)
    /// \return
    int Length() const;

    /// Set the length of the array (only shrinking the array is allowed)
    void setLength(int new_length);

    /// \brief Check if the joints are valid. For example, when we request the Inverse kinematics and there is no solution the joints will not be valid.
    /// (for example, an invalid result after calling class: IItem::SolveIK returns a non valid joints)
    /// \return true if it has 1 degree of freedom or more
    bool Valid();

    /// \brief GetValues
    /// \param joints joint values in deg or mm
    /// \return returns the number of degrees of freedom
    int GetValues(double *joints);

    /// \brief Set the joint values in deg or mm. You can also important provide the number of degrees of freedom (6 for a 6 axis robot).
    /// \param joints joint values in deg or mm
    /// \param ndofs number of degrees of freedom (number of axes or joints)
    void SetValues(const double *joints, int ndofs = -1);

    /// \brief Set the joint values in deg or mm (floats). You can also important provide the number of degrees of freedom (6 for a 6 axis robot).
    /// \param joints joint values in deg or mm
    /// \param ndofs number of degrees of freedom (number of axes or joints)
    void SetValues(const float *joints, int ndofs = -1);

#ifdef QT_GUI_LIB
    /// To String operator (use with qDebug() << Joints;
    inline operator QString() const { return ToString(); }

    /// \brief Retrieve a string representation of the joint values.
    /// \param separator String to add between consecutive joint values
    /// \param precision Number of decimals
    /// \return string as a QString
    QString ToString(
        const QString& separator = QLatin1String(", "),
        int precision = 3) const;

    /// \brief Set the joint values given a comma-separated string. Tabs and spaces are also allowed.
    /// \param str string. Such as "10, 20, 30, 40, 50, 60"
    /// \return false if parsing the string failed. True otherwise.
    bool FromString(const QString& str);
#endif

public:
    static constexpr int MaximumJoints = 12;

    /// number of degrees of freedom
    int _dofCount;

    /// joint values (doubles, used to store the joint values)
    double _joints[MaximumJoints];

    /// joint values (floats, used to return a copy as a float pointer)
    mutable float _jointsFloat[MaximumJoints];
};


} // namespace robodk


#endif // ROBODK_JOINTS_H
