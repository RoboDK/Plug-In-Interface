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

/*!
    \class Vector3
    \brief The Vector3 class represents a vector or vertex in 3D space.

    Vectors are one of the main building blocks of 3D representation and
    drawing.  They consist of three coordinates, traditionally called
    x, y, and z.
*/
class Vector3
{
public:
    /*!
        Constructs a null vector, i.e. with coordinates (0, 0, 0).
    */
    Vector3() = default;

    /*!
        Constructs a vector with coordinates (\a x, \a y, \a z).
    */
    Vector3(double x, double y, double z);

    /*!
        Constructs a vector object as a copy of \a v.
    */
    Vector3(const Vector3& v) = default;

    /*!
        Returns the length of the vector from the origin.
    */
    double Length() const;

    /*!
        Normalizes the currect vector in place. Nothing happens if this
        vector is a null vector or the length of the vector is very close to 1.
    */
    void Normalize();

    /*!
        Returns the x coordinate of this vector.
    */
    inline double X() const { return _v[0]; }

    /*!
        Returns the y coordinate of this vector.
    */
    inline double Y() const { return _v[1]; }

    /*!
        Returns the z coordinate of this vector.
    */
    inline double Z() const { return _v[2]; }

    /*!
        Sets the x coordinate of this vector to the given \a x coordinate.
    */
    inline void SetX(double x) { _v[0] = x; }

    /*!
        Sets the y coordinate of this vector to the given \a y coordinate.
    */
    inline void SetY(double y) { _v[0] = y; }

    /*!
        Sets the z coordinate of this vector to the given \a z coordinate.
    */
    inline void SetZ(double z) { _v[0] = z; }

    /*!
        Returns the component of the vector at index position \a i.
    */
    inline const double& operator[](size_t i) const { return _v[i]; }

    /*!
        Returns the component of the vector at index position \a i
        as a modifiable reference.
    */
    inline double& operator[](size_t i) { return _v[i]; }

    /*!
        Returns the dot product of \a v1 and \a v2.
    */
    static double DotProduct(const Vector3& v1, const Vector3& v2);

    /*!
        Returns the cross-product of vectors \a v1 and \a v2, which corresponds
        to the normal vector of a plane defined by \a v1 and \a v2.
    */
    static Vector3 CrossProduct(const Vector3& v1, const Vector3& v2);

    /*!
        Sets this Vector3 object as a copy of \a v.
    */
    Vector3& operator=(const Vector3& v) = default;

private:
    /*! \cond */

    double _v[3] = {0.0, 0.0, 0.0};

    /*! \endcond */
};

} // namespace robodk


#endif // ROBODK_VECTOR3_H
