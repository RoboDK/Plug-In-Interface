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

#include "joints.h"

#include <cstring>
#include <algorithm>

#include "robodktypes.h"


namespace robodk
{

Joints::Joints()
    : _dofCount(0)
{
    std::memset(_joints, 0, sizeof(_joints));
    std::memset(_jointsFloat, 0, sizeof(_jointsFloat));
}

Joints::Joints(int ndofs)
{
    _dofCount = std::min(ndofs, maximumJoints);
    for (int i = 0; i < _dofCount; i++)
    {
        _joints[i] = 0.0;
    }
}

Joints::Joints(const double *joints, int ndofs)
{
    SetValues(joints, ndofs);
}

Joints::Joints(const float *joints, int ndofs)
{
    int ndofs_ok = std::min(ndofs, maximumJoints);
    double jnts[maximumJoints];

    for (int i=0; i < ndofs_ok; i++)
    {
        jnts[i] = joints[i];
    }
    SetValues(jnts, ndofs_ok);
}

Joints::Joints(const tMatrix2D *mat2d, int column, int ndofs)
{
    if (column >= Matrix2D_Size(mat2d, 2))
    {
        _dofCount = 0;
    }
    if (ndofs < 0)
    {
        ndofs = Matrix2D_Size(mat2d, 1);
    }
    _dofCount = qMin(ndofs, RDK_SIZE_JOINTS_MAX);

    double *ptr = Matrix2D_Get_col(mat2d, column);
    SetValues(ptr, _dofCount);
}

Joints::Joints(const QString &str)
{
    _dofCount = 0;
    FromString(str);
}

const double* Joints::ValuesD() const
{
    return _joints;
}

const float* Joints::ValuesF() const
{
    for (int i = 0; i < RDK_SIZE_JOINTS_MAX; i++)
    {
        _jointsFloat[i] = _joints[i];
    }

    return _jointsFloat;
}

#ifdef ROBODK_API_FLOATS
const float* Joints::Values() const
{
    return ValuesF();
}
#else
const double* Joints::Values() const
{
    return _joints;
}
#endif

double Joints::Compare(const Joints &other) const
{
    double sum_diff = 0.0;
    for (int i = 0; i <qMin(_dofCount, other.Length()); i++)
    {
        sum_diff += qAbs(_joints[i] - other.Values()[i]);
    }
    return sum_diff;
}

double* Joints::Data()
{
    return _joints;
}

int Joints::Length() const
{
    return _dofCount;
}

void Joints::setLength(int new_length)
{
    if (new_length >= 0 && new_length < _dofCount)
    {
        _dofCount = new_length;
    }
}

bool Joints::Valid()
{
    return _dofCount > 0;
}

void Joints::SetValues(const double *values, int ndofs)
{
    if (ndofs >= 0)
    {
        _dofCount = qMin(ndofs, RDK_SIZE_JOINTS_MAX);
    }

    for (int i = 0; i < _dofCount; i++)
    {
        _joints[i] = values[i];
    }
}

void Joints::SetValues(const float *values, int ndofs)
{
    if (ndofs >= 0)
    {
        _dofCount = qMin(ndofs, RDK_SIZE_JOINTS_MAX);
    }

    for (int i = 0; i < _dofCount; i++)
    {
        _joints[i] = values[i];
    }
}

int Joints::GetValues(double *values)
{
    for (int i = 0; i < _dofCount; i++)
    {
        values[i] = _joints[i];
    }

    return _dofCount;
}

#ifdef QT_GUI_LIB
QString Joints::ToString(const QString &separator, int precision) const
{
    QString values;
    for (int i = 0; i < _dofCount; i++)
    {
        if (i > 0)
        {
            values.append(separator);
        }
        values.append(QString::number(_joints[i], 'f', precision));
    }
    return values;
}

bool Joints::FromString(const QString &str)
{
    const QLatin1Char separator(',');

    QString s = str;
    s.replace(QLatin1Char(';'), separator);
    s.replace(QLatin1Char('\t'), separator);

#if (QT_VERSION < QT_VERSION_CHECK(5, 14, 0))
    const QString::SplitBehavior behavior = QString::SkipEmptyParts;
#else
    const Qt::SplitBehavior behavior = Qt::SkipEmptyParts;
#endif

    QStringList jointList = s.split(separator, behavior);
    _dofCount = qMin(jointList.length(), RDK_SIZE_JOINTS_MAX);
    for (int i = 0; i < _dofCount; i++)
    {
        _joints[i] = jointList[i].trimmed().toDouble();
    }
    return true;
}
#endif // QT_GUI_LIB

} // namespace robodk
