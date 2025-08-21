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

#ifndef ROBODK_LEGACY_MATRIX2D_H
#define ROBODK_LEGACY_MATRIX2D_H


#ifdef QT_GUI_LIB
class QTextStream;
class QDataStream;
#endif // QT_GUI_LIB


namespace robodk
{

namespace legacy
{

/*!
    \struct Matrix2D
    \brief The Matrix2D struct represents a variable size 2D matrix.

    Use the Matrix2D_... functions to operate on this variable sized matrix.
    This type of data can be used to get/set a program as a list.
    This is also useful for backwards compatibility functions related to RoKiSim.
*/
struct Matrix2D
{
    /*!
        Pointer to the data.
    */
    double* data;

    /*!
        Pointer to the size array.
    */
    int* size;

    /*!
        Allocated size.
    */
    int allocatedSize;

    /*!
        Number of dimensions (usually 2).
    */
    int numDimensions;

    bool canFreeData;
};

/*!
    Creates a new \ref Matrix2D object with no dimensions.

    \returns pointer to the Matrix2D object if no allocation errors occurred; nullptr otherwise.

    \sa Matrix2D_Delete()
*/
Matrix2D* Matrix2D_Create();

/*!
    Deletes an existing \ref Matrix2D object.

    \param matrix pointer of the pointer variable to the matrix object.

    \sa Matrix2D_Create()
*/
void Matrix2D_Delete(Matrix2D** matrix);

/*!
    Sets new dimensions for existing matrix object.

    \param matrix pointer to the matrix object.
    \param rows number of rows.
    \param columns number of columns.

    \sa Matrix2D_GetDimension()
*/
void Matrix2D_SetDimensions(Matrix2D* matrix, int rows, int columns);

/*!
    Returns \a dimension (number of rows or columns) of \a matrix.

    \param matrix pointer to the matrix object.
    \param dimension may have a value of 1 or 2 to retrieve number of
        rows or columns respectively.

    \sa Matrix2D_SetDimensions(), Matrix2D_ColumnCount(), Matrix2D_RowCount()
*/
int Matrix2D_GetDimension(const Matrix2D* matrix, int dimension);

/*!
    Returns the total number of columns in the \a matrix.

    \sa Matrix2D_SetDimensions(), Matrix2D_RowCount()
*/
int Matrix2D_ColumnCount(const Matrix2D* matrix);

/*!
    Returns the total number of rows in the \a matrix.

    \sa Matrix2D_SetDimensions(), Matrix2D_RowCount()
*/
int Matrix2D_RowCount(const Matrix2D* matrix);

/*!
    Returns the value of the element at position (\a row, \a column) in the \a matrix.
*/
double Matrix2D_Get(const Matrix2D* matrix, int row, int column);

/*!
    Sets a new \a value to the element at position (\a row, \a column) in the \a matrix.
*/
void Matrix2D_Set(const Matrix2D* matrix, int row, int column, double value);

/*!
    Returns the elements of \a column as a pointer to its values in the \a matrix.
*/
double* Matrix2D_GetColumn(const Matrix2D* matrix, int column);

/*!
    \brief Copies the matrix \a source to the \a destination.

    Both matrices must be initialized and have the same size.

    \returns true if successful; otherwise returns false.
*/
bool Matrix2D_Copy(const Matrix2D* source, Matrix2D* destination);

#ifdef QT_GUI_LIB
/*!
    Writes the contents of the \a array with \a size elements using qDebug().
*/
void Matrix2D_DebugArray(const double* array, int size);

/*!
    Writes the contents of the \a matrix using qDebug().
*/
void Matrix2D_Debug(const Matrix2D* matrix);

/*!
    \brief Writes the contents of the \a matrix into text \a stream.

    The values can be written in the CSV format.
*/
void Matrix2D_Save(QTextStream* stream, Matrix2D* matrix, bool csv = false);

/*!
    Writes the contents of the \a matrix into binary \a stream.
*/
void Matrix2D_Save(QDataStream* stream, Matrix2D* matrix);

/*!
    Creates a new \ref Matrix2D object by loading its contents from a binary \a stream.
*/
void Matrix2D_Load(QDataStream* stream, Matrix2D** matrix);
#endif // QT_GUI_LIB

} // namespace legacy

} // namespace robodk


#endif // ROBODK_LEGACY_MATRIX2D_H
