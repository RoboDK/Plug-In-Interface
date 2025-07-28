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

#include "legacymatrix2d.h"

#include <cstdlib>

#ifdef QT_GUI_LIB
#include <QTextStream>
#include <QDataStream>
#include <QDebug>
#endif // QT_GUI_LIB


namespace robodk
{

namespace legacy
{

static void emxInit_real_T(Matrix2D** pMatrix, int dimensions)
{
    if (!pMatrix)
        return;

    if (dimensions < 0)
    {
        *pMatrix = nullptr;
        return;
    }

    *pMatrix = (Matrix2D*) malloc(sizeof(Matrix2D));
    Matrix2D* matrix = *pMatrix;
    if (!matrix)
        return;

    matrix->data = nullptr;
    matrix->numDimensions = dimensions;
    matrix->size = (int*) malloc(sizeof(int) * dimensions);
    matrix->allocatedSize = 0;
    matrix->canFreeData = true;

    for (int i = 0; i < dimensions; i++)
        matrix->size[i] = 0;
}

static void emxFree_real_T(Matrix2D** pMatrix)
{
    if (!pMatrix)
        return;

    auto matrix = *pMatrix;
    if (!matrix)
        return;

    if (matrix->canFreeData)
        free(matrix->data);

    free(matrix->size);
    free(matrix);

    *pMatrix = nullptr;
}

static void emxEnsureCapacity(Matrix2D* matrix, int oldNumel, size_t elementSize)
{
    if (!matrix)
        return;

    double *newData;

    if (oldNumel < 0)
        oldNumel = 0;

    int newNumel = 1;
    for (int i = 0; i < matrix->numDimensions; i++)
        newNumel *= matrix->size[i];

    if (newNumel <= matrix->allocatedSize)
        return;

    int newSize = matrix->allocatedSize;
    if (newSize < 16)
        newSize = 16;

    while (newSize < newNumel)
    {
        if (newSize > 1073741823)
        {
            newSize = 2147483647; //MAX_int32_T;
        }
        else
        {
            newSize <<= 1;
        }
    }

    newData = (double*) calloc(newSize, elementSize);
    if (matrix->data)
    {
        memcpy(newData, matrix->data, elementSize * oldNumel);
        if (matrix->canFreeData)
            free(matrix->data);
    }

    matrix->data = newData;
    matrix->allocatedSize = newSize;
    matrix->canFreeData = true;
}

Matrix2D* Matrix2D_Create()
{
    Matrix2D* matrix;
    emxInit_real_T(&matrix, 2);
    return matrix;
}

void Matrix2D_Delete(Matrix2D** matrix)
{
    emxFree_real_T(matrix);
}

void Matrix2D_SetDimensions(Matrix2D* matrix, int rows, int columns)
{
    int size = matrix->size[0] * matrix->size[1];
    matrix->size[0] = rows;
    matrix->size[1] = columns;
    emxEnsureCapacity(matrix, size, sizeof(double));
}

int Matrix2D_GetDimension(const Matrix2D* matrix, int dimension)
{
    // ONE BASED!!
    if (matrix->numDimensions >= dimension)
    {
        return matrix->size[dimension - 1];
    }
    else
    {
        return 0;
    }
}

int Matrix2D_ColumnCount(const Matrix2D* matrix)
{
    return Matrix2D_GetDimension(matrix, 2);
}

int Matrix2D_RowCount(const Matrix2D* matrix)
{
    return Matrix2D_GetDimension(matrix, 1);
}

double Matrix2D_Get(const Matrix2D* matrix, int row, int column)
{
    // ZERO BASED!!
    return matrix->data[matrix->size[0] * column + row];
}

void Matrix2D_Set(const Matrix2D* matrix, int row, int column, double value)
{
    // ZERO BASED!!
    matrix->data[matrix->size[0] * column + row] = value;
}

double* Matrix2D_GetColumn(const Matrix2D* matrix, int column)
{
    // ZERO BASED!!
    return (matrix->data + matrix->size[0] * column);
}

bool Matrix2D_Copy(const Matrix2D* source, Matrix2D* destination)
{
    if (source->numDimensions != 2 || destination->numDimensions != 2)
    {
        Matrix2D_SetDimensions(destination, 0, 0);
        return false;
    }

    int sz1 = Matrix2D_GetDimension(source, 1);
    int sz2 = Matrix2D_GetDimension(source, 2);
    Matrix2D_SetDimensions(destination, sz1, sz2);
    int numel = sz1 * sz2;
    for (int i = 0; i < numel; i++)
    {
        destination->data[i] = source->data[i];
    }

    return true;
}

#ifdef QT_GUI_LIB
void Matrix2D_DebugArray(const double *array, int size)
{
    int i;
    QString strout;
    for (i = 0; i < size; i++) {
        strout.append(QString::number(array[i], 'f', 3));
        if (i < size - 1) {
            strout.append(" , ");
        }
    }
    qDebug().noquote() << strout;
}

void Matrix2D_Debug(const Matrix2D* matrix)
{
    int size1;
    int size2;
    int j;
    double *column;
    size1 = Matrix2D_RowCount(matrix);
    size2 = Matrix2D_ColumnCount(matrix);
    qDebug().noquote() << "Matrix size = " << size1 << " x " << size2;
    if (size1*size2 == 0)
    {
        return;
    }
    for (j = 0; j<size2; j++)
    {
        column = Matrix2D_GetColumn(matrix, j);
        Matrix2D_DebugArray(column, size1);
    }
}

void Matrix2D_Save(QTextStream *stream, Matrix2D* matrix, bool csv)
{
    int size1;
    int size2;
    int j;
    double *column;
    size1 = Matrix2D_RowCount(matrix);
    size2 = Matrix2D_ColumnCount(matrix);
    //*st << "% Matrix size = " << size1 << " x " << size2;
    if (size1 * size2 == 0)
    {
        return;
    }

    if (csv)
    {
        for (j = 0; j<size2; j++)
        {
            column = Matrix2D_GetColumn(matrix, j);
            for (int i = 0; i < size1; i++)
            {
                *stream << QString::number(column[i], 'f', 8) << ", ";
            }
            *stream << "\n";
        }
    }
    else
    {
        for (j = 0; j<size2; j++)
        {
            column = Matrix2D_GetColumn(matrix, j);
            *stream << "[";
            for (int i = 0; i < size1; i++)
            {
                *stream << QString::number(column[i], 'f', 8) << " ";
            }
            *stream << "];\n";
        }
    }
}

void Matrix2D_Save(QDataStream* stream, Matrix2D* matrix)
{
    int i;
    *stream << matrix->numDimensions;
    int size_values = 1;
    for (i = 0; i < matrix->numDimensions; i++)
    {
        qint32 sizei = matrix->size[i];
        size_values = size_values * sizei;
        *stream << sizei;
    }
    for (i = 0; i < size_values; i++)
    {
        *stream << matrix->data[i];
    }
}

void Matrix2D_Load(QDataStream *stream, Matrix2D** matrix)
{
    if (stream->atEnd())
    {
        qDebug() << "No data to read";
        return;
    }

    if (*matrix != nullptr)
    {
        Matrix2D_Delete(matrix);
    }

    int i;
    qint32 ndim;
    qint32 sizei;
    *stream >> ndim;
    qDebug() << "Loading matrix of dimensions: " << ndim;
    emxInit_real_T(matrix, ndim);
    int size_values = 1;
    for (i = 0; i < ndim; i++)
    {
        *stream >> sizei;
        size_values = size_values * sizei;
        (*matrix)->size[i] = sizei;
    }
    //emxEnsureCapacity((emxArray__common *) *emx, 0, (int32_T)sizeof(real_T));
    emxEnsureCapacity(*matrix, 0, sizeof(double));
    double value;
    for (i = 0; i < size_values; i++)
    {
        *stream >> value;
        (*matrix)->data[i] = value;
    }
}
#endif // QT_GUI_LIB


} // namespace legacy

} // namespace robodk
