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

#include "matrix4x4.h"

#include <cmath>

#include "vector3.h"
#include "constants.h"


namespace robodk
{

Matrix4x4::Matrix4x4()
    : QMatrix4x4()
    , _valid(true)
{
    setToIdentity();
}

Matrix4x4::Matrix4x4(bool valid)
    : QMatrix4x4()
    , _valid(valid ? 1.0 : 0.0)
{
    setToIdentity();
}

Matrix4x4::Matrix4x4(const Matrix4x4 &matrix)
    : QMatrix4x4(matrix)
    , _valid(matrix._valid)
{
}

Matrix4x4::Matrix4x4(const double* values)
    : QMatrix4x4(
          values[0], values[4], values[8],  values[12],
          values[1], values[5], values[9],  values[13],
          values[2], values[6], values[10], values[14],
          values[3], values[7], values[11], values[15])
    , _valid(1.0)
{
}

Matrix4x4::Matrix4x4(const float* values)
    : QMatrix4x4(
          values[0], values[4], values[8],  values[12],
          values[1], values[5], values[9],  values[13],
          values[2], values[6], values[10], values[14],
          values[3], values[7], values[11], values[15])
    , _valid(1.0)
{
}

Matrix4x4::Matrix4x4(double x, double y, double z)
    : QMatrix4x4(
          1.0f, 0.0f, 0.0f, x,
          0.0f, 1.0f, 0.0f, y,
          0.0f, 0.0f, 1.0f, z,
          0.0f, 0.0f, 0.0f, 1.0f)
    , _valid(1.0)
{
    setToIdentity();
    (*this)(0, 3) = x;
    (*this)(1, 3) = y;
    (*this)(2, 3) = z;
}


Matrix4x4::Matrix4x4(
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
    double tz)
    : QMatrix4x4(
          nx,   ox,   ax,   tx,
          ny,   oy,   ay,   ty,
          nz,   oz,   az,   tz,
          0.0f, 0.0f, 0.0f, 1.0f)
    , _valid(1.0)
{
}

void Matrix4x4::setVX(const Vector3& n)
{
    (*this)(0, 0) = n.x();
    (*this)(1, 0) = n.y();
    (*this)(2, 0) = n.z();
}

void Matrix4x4::setVY(const Vector3& o)
{
    (*this)(0, 1) = o.x();
    (*this)(1, 1) = o.y();
    (*this)(2, 1) = o.z();
}

void Matrix4x4::setVZ(const Vector3& a)
{
    (*this)(0, 2) = a.x();
    (*this)(1, 2) = a.y();
    (*this)(2, 2) = a.z();
}

void Matrix4x4::setVX(double x, double y, double z)
{
    Set(0,0, x);
    Set(1,0, y);
    Set(2,0, z);
}

void Matrix4x4::setVY(double x, double y, double z)
{
    Set(0,1, x);
    Set(1,1, y);
    Set(2,1, z);
}

void Matrix4x4::setVZ(double x, double y, double z)
{
    Set(0,2, x);
    Set(1,2, y);
    Set(2,2, z);
}

void Matrix4x4::setPos(double x, double y, double z)
{
    Set(0,3, x);
    Set(1,3, y);
    Set(2,3, z);
}

void Matrix4x4::setVX(const double* xyz)
{
    Set(0,0, xyz[0]);
    Set(1,0, xyz[1]);
    Set(2,0, xyz[2]);
}

void Matrix4x4::setVY(const double* xyz)
{
    Set(0,1, xyz[0]);
    Set(1,1, xyz[1]);
    Set(2,1, xyz[2]);
}

void Matrix4x4::setVZ(const double* xyz)
{
    Set(0,2, xyz[0]);
    Set(1,2, xyz[1]);
    Set(2,2, xyz[2]);
}

void Matrix4x4::setPos(const double* xyz)
{
    Set(0,3, xyz[0]);
    Set(1,3, xyz[1]);
    Set(2,3, xyz[2]);
}

Vector3 Matrix4x4::vx() const
{
    return Vector3(
        (*this)(0, 0),
        (*this)(1, 0),
        (*this)(2, 0));
}

Vector3 Matrix4x4::vy() const
{
    return Vector3(
        (*this)(0, 1),
        (*this)(1, 1),
        (*this)(2, 1));
}

Vector3 Matrix4x4::vz() const
{
    return Vector3(
        (*this)(0, 2),
        (*this)(1, 2),
        (*this)(2, 2));
}

void Matrix4x4::VX(double* xyz) const
{
    xyz[0] = Get(0, 0);
    xyz[1] = Get(1, 0);
    xyz[2] = Get(2, 0);
}

void Matrix4x4::VY(double* xyz) const
{
    xyz[0] = Get(0, 1);
    xyz[1] = Get(1, 1);
    xyz[2] = Get(2, 1);
}

void Matrix4x4::VZ(double* xyz) const
{
    xyz[0] = Get(0, 2);
    xyz[1] = Get(1, 2);
    xyz[2] = Get(2, 2);
}

void Matrix4x4::Pos(double* xyz) const
{
    xyz[0] = Get(0, 3);
    xyz[1] = Get(1, 3);
    xyz[2] = Get(2, 3);
}

void Matrix4x4::setValues(const double* values)
{
    Set(0,0, values[0]);
    Set(1,0, values[1]);
    Set(2,0, values[2]);
    Set(3,0, values[3]);

    Set(0,1, values[4]);
    Set(1,1, values[5]);
    Set(2,1, values[6]);
    Set(3,1, values[7]);

    Set(0,2, values[8]);
    Set(1,2, values[9]);
    Set(2,2, values[10]);
    Set(3,2, values[11]);

    Set(0,3, values[12]);
    Set(1,3, values[13]);
    Set(2,3, values[14]);
    Set(3,3, values[15]);
}

void Matrix4x4::Set(int i, int j, double value)
{
    QVector4D rw(this->row(i));
    rw[j] = value;
    setRow(i, rw);
}

double Matrix4x4::Get(int i, int j) const
{
    return row(i)[j];
}

Matrix4x4 Matrix4x4::inv() const
{
    return this->inverted();
}

bool Matrix4x4::isHomogeneous() const
{
    auto tx = vx();
    auto ty = vy();
    auto tz = vz();

    const double tol = 1e-7;

    if (std::fabs(Vector3::dotProduct(tx, ty)) > tol)
    {
        return false;
    }
    else if (std::fabs(Vector3::dotProduct(tx, tz)) > tol)
    {
        return false;
    }
    else if (std::fabs(Vector3::dotProduct(ty, tz)) > tol)
    {
        return false;
    }
    else if (std::fabs(tx.length() - 1.0) > tol)
    {
        return false;
    }
    else if (std::fabs(ty.length() - 1.0) > tol)
    {
        return false;
    }
    else if (std::fabs(tz.length() - 1.0) > tol)
    {
        return false;
    }

    return true;
}

bool Matrix4x4::MakeHomogeneous()
{
    auto tx = vx();
    auto ty = vy();
    auto tz = vz();

    bool result = isHomogeneous();

    tx.normalize();
    tz = Vector3::crossProduct(tx, ty);
    tz.normalize();
    ty = Vector3::crossProduct(tz, tx);
    ty.normalize();

    setVX(tx);
    setVY(ty);
    setVZ(tz);

    (*this)(3, 0) = 0.0f;
    (*this)(3, 1) = 0.0f;
    (*this)(3, 2) = 0.0f;
    (*this)(3, 3) = 1.0f;

    return !result;
}

void Matrix4x4::ToXYZRPW(double* xyzwpr) const
{
    double x = Get(0,3);
    double y = Get(1,3);
    double z = Get(2,3);
    double w, p, r;

    if (Get(2,0) > (1.0 - 1e-6))
    {
        p = -constants::pi * 0.5;
        r = 0;
        w = atan2(-Get(1,2), Get(1,1));
    }
    else if (Get(2,0) < -1.0 + 1e-6)
    {
        p = 0.5 * constants::pi;
        r = 0;
        w = atan2(Get(1,2),Get(1,1));
    }
    else
    {
        p = atan2(-Get(2, 0), sqrt(Get(0, 0) * Get(0, 0) + Get(1, 0) * Get(1, 0)));
        w = atan2(Get(1, 0), Get(0, 0));
        r = atan2(Get(2, 1), Get(2, 2));
    }

    xyzwpr[0] = x;
    xyzwpr[1] = y;
    xyzwpr[2] = z;
    xyzwpr[3] = r * 180.0 / constants::pi;
    xyzwpr[4] = p * 180.0 / constants::pi;
    xyzwpr[5] = w * 180.0 / constants::pi;
}

Matrix4x4 Matrix4x4::XYZRPW_2_Mat(double x, double y, double z, double r, double p, double w)
{
    double a = r * constants::pi / 180.0;
    double b = p * constants::pi / 180.0;
    double c = w * constants::pi / 180.0;
    double ca = cos(a);
    double sa = sin(a);
    double cb = cos(b);
    double sb = sin(b);
    double cc = cos(c);
    double sc = sin(c);
    return Matrix4x4(cb * cc, cc * sa * sb - ca * sc, sa * sc + ca * cc * sb, x,
               cb * sc, ca * cc + sa * sb * sc, ca * sb * sc - cc * sa, y,
               -sb, cb * sa, ca * cb, z);
}

Matrix4x4 Matrix4x4::XYZRPW_2_Mat(const double* xyzwpr)
{
    return XYZRPW_2_Mat(xyzwpr[0], xyzwpr[1], xyzwpr[2], xyzwpr[3], xyzwpr[4], xyzwpr[5]);
}

void Matrix4x4::FromXYZRPW(const double* xyzwpr)
{
    Matrix4x4 newmat = Matrix4x4::XYZRPW_2_Mat(xyzwpr[0], xyzwpr[1], xyzwpr[2],
                                   xyzwpr[3], xyzwpr[4], xyzwpr[5]);

    for (int i = 0; i < 4; i++)
    {
        for (int j = 0; j < 4; j++)
        {
            this->Set(i, j, newmat.Get(i, j));
        }
    }
}

const double* Matrix4x4::ValuesD() const
{
    for(int i = 0; i < 16; ++i)
    {
        _md[i] = constData()[i];
    }
    return _md;
}

const float* Matrix4x4::ValuesF() const
{
    return constData();
}

#ifdef ROBODK_API_FLOATS
const float* Matrix4x4::Values() const
{
    return constData();
}
#else
const double* Matrix4x4::Values() const
{
    return ValuesD();
}
#endif

void Matrix4x4::Values(double data[16]) const
{
    for(int i = 0; i < 16; ++i)
    {
        data[i] = constData()[i];
    }
}

void Matrix4x4::Values(float data[16]) const
{
    for(int i = 0; i < 16; ++i)
    {
        data[i] = constData()[i];
    }
}

bool Matrix4x4::Valid() const
{
    return _valid;
}

Matrix4x4& Matrix4x4::operator=(const Matrix4x4& matrix)
{
    QMatrix4x4::operator=(matrix);
    _valid = 1.0;
    return *this;
}

Matrix4x4 Matrix4x4::transl(double x, double y, double z)
{
    Matrix4x4 mat;
    mat.setToIdentity();
    mat.setPos(x, y, z);
    return mat;
}

Matrix4x4 Matrix4x4::rotx(double rx)
{
    double cx = cos(rx);
    double sx = sin(rx);
    return Matrix4x4(1, 0, 0, 0, 0, cx, -sx, 0, 0, sx, cx, 0);
}

Matrix4x4 Matrix4x4::roty(double ry)
{
    double cy = cos(ry);
    double sy = sin(ry);
    return Matrix4x4(cy, 0, sy, 0, 0, 1, 0, 0, -sy, 0, cy, 0);
}

Matrix4x4 Matrix4x4::rotz(double rz)
{
    double cz = cos(rz);
    double sz = sin(rz);
    return Matrix4x4(cz, -sz, 0, 0, sz, cz, 0, 0, 0, 0, 1, 0);
}

#ifdef QT_GUI_LIB
Matrix4x4::Matrix4x4(const QMatrix4x4 &matrix)
    : QMatrix4x4(matrix)
    , _valid(1.0)
{
}

bool Matrix4x4::FromString(const QString &pose_str)
{
    QString pose_str2 = pose_str.trimmed();

    const Qt::CaseSensitivity cs = Qt::CaseInsensitive;
    if (pose_str2.startsWith("Mat(", cs))
    {
        pose_str2.remove(0, 4);
        pose_str2 = pose_str2.trimmed();
    }

    if (pose_str2.startsWith("XYZRPW_2_Mat(", cs))
    {
        pose_str2.remove(0, 13);
        pose_str2 = pose_str2.trimmed();
    }

    while (pose_str2.endsWith(')'))
    {
        pose_str2.chop(1);
    }

    const QLatin1Char separator(',');
    pose_str2.replace(QLatin1Char(';'), separator);
    pose_str2.replace(QLatin1Char('\t'), separator);

#if (QT_VERSION < QT_VERSION_CHECK(5, 14, 0))
    const QString::SplitBehavior behavior = QString::SkipEmptyParts;
#else
    const Qt::SplitBehavior behavior = Qt::SkipEmptyParts;
#endif

    QStringList values_list = pose_str2.split(separator, behavior);
    double xyzwpr[6] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};

    if (values_list.length() < 6)
    {
        FromXYZRPW(xyzwpr);
        return false;
    }

    for (int i = 0; i < 6; i++)
    {
        xyzwpr[i] = values_list[i].trimmed().toDouble();
    }

    FromXYZRPW(xyzwpr);
    return true;
}

QString Matrix4x4::ToString(const QString &separator, int precision, bool xyzwpr_only) const
{
    if (!Valid())
    {
        return "Mat(Invalid)";
    }

    QString str;
    if (!isHomogeneous())
    {
        str.append("Warning!! Pose is not homogeneous! Use Matrix4x4::MakeHomogeneous() to make this matrix homogeneous\n");
    }

    str.append("Mat(XYZRPW_2_Mat(");

    double xyzwpr[6];
    ToXYZRPW(xyzwpr);

    for (int i = 0; i < 6; i++)
    {
        if (i > 0)
        {
            str.append(separator);
        }
        str.append(QString::number(xyzwpr[i], 'f', precision));
    }
    str.append("))");

    if (xyzwpr_only)
    {
        return str;
    }

    str.append("\n");

    for (int i = 0; i < 4; i++)
    {
        str.append("[");
        for (int j = 0; j < 4; j++)
        {
            str.append(QString::number(row(i)[j], 'f', precision));
            if (j < 3)
            {
                str.append(separator);
            }
        }
        str.append("];\n");
    }
    return str;
}

Matrix4x4& Matrix4x4::operator=(const QMatrix4x4& matrix)
{
    QMatrix4x4::operator=(matrix);
    _valid = 1.0;
    return *this;
}
#endif // QT_GUI_LIB

} // namespace robodk
