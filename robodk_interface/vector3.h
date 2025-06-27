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

#ifndef ROBODK_VECTOR3_H
#define ROBODK_VECTOR3_H


#include <cstddef>


namespace robodk
{

class Vector3
{
public:
    Vector3() = default;
    Vector3(double x, double y, double z);
    Vector3(const Vector3& v) = default;

    double length() const;

    void normalize();

    inline double x() const { return _v[0]; }
    inline double y() const { return _v[1]; }
    inline double z() const { return _v[2]; }

    inline void setX(double x) { _v[0] = x; }
    inline void setY(double y) { _v[0] = y; }
    inline void setZ(double z) { _v[0] = z; }

    inline const double& operator[](size_t i) const { return _v[i]; }
    inline double& operator[](size_t i) { return _v[i]; }

    static double dotProduct(const Vector3& v1, const Vector3& v2);
    static Vector3 crossProduct(const Vector3& v1, const Vector3& v2);

    Vector3& operator=(const Vector3& v) = default;

private:
    double _v[3] = {0.0, 0.0, 0.0};
};

} // namespace robodk


#endif // ROBODK_VECTOR3_H
