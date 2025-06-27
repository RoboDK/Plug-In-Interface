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

#include "vector3.h"

#include <cmath>


namespace robodk
{

Vector3::Vector3(double x, double y, double z)
{
    _v[0] = x;
    _v[1] = y;
    _v[2] = z;
}

double Vector3::length() const
{
    return std::sqrt(_v[0] * _v[0] + _v[1] * _v[1] + _v[2] * _v[2]);
}

void Vector3::normalize()
{
    double len = length();
    _v[0] /= len;
    _v[1] /= len;
    _v[2] /= len;
}

double Vector3::dotProduct(const Vector3& v1, const Vector3& v2)
{
    return v1._v[0] * v2._v[0] + v1._v[1] * v2._v[1] + v1._v[2] * v2._v[2];
}

Vector3 Vector3::crossProduct(const Vector3& v1, const Vector3& v2)
{
    return Vector3(
        v1._v[1] * v2._v[2] - v1._v[2] * v2._v[1],
        v1._v[2] * v2._v[0] - v1._v[0] * v2._v[2],
        v1._v[0] * v2._v[1] - v1._v[1] * v2._v[0]);
}


} // namespace robodk
