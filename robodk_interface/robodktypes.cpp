#include "robodktypes.h"

#include <QtMath>
#include <QDebug>


//----------------------------------- Mat class -----------------------
Mat transl(double x, double y, double z)
{
    return Mat::transl(x,y,z);
}

Mat rotx(double rx)
{
    return Mat::rotx(rx);
}

Mat roty(double ry)
{
    return Mat::roty(ry);
}

Mat rotz(double rz)
{
    return Mat::rotz(rz);
}
//---------------------------------------------------------------------


//----------------------------------- 2D matrix functions -------------
void emxInit_real_T(tMatrix2D **pEmxArray, int numDimensions)
{
    tMatrix2D *emxArray;
    int i;
    *pEmxArray = (tMatrix2D *)malloc(sizeof(tMatrix2D));
    emxArray = *pEmxArray;
    emxArray->data = (double *)NULL;
    emxArray->numDimensions = numDimensions;
    emxArray->size = (int *)malloc((unsigned int)(sizeof(int) * numDimensions));
    emxArray->allocatedSize = 0;
    emxArray->canFreeData = true;
    for (i = 0; i < numDimensions; i++)
    {
        emxArray->size[i] = 0;
    }
}

tMatrix2D* Matrix2D_Create()
{
    tMatrix2D *matrix;
    emxInit_real_T((tMatrix2D**)(&matrix), 2);
    return matrix;
}

void emxFree_real_T(tMatrix2D **pEmxArray)
{
    if (*pEmxArray != (tMatrix2D *)NULL)
    {
        if (((*pEmxArray)->data != (double *)NULL) && (*pEmxArray)->canFreeData)
        {
            free((void *)(*pEmxArray)->data);
        }
        free((void *)(*pEmxArray)->size);
        free((void *)*pEmxArray);
        *pEmxArray = (tMatrix2D *)NULL;
    }
}

void Matrix2D_Delete(tMatrix2D **mat)
{
    emxFree_real_T((tMatrix2D**)(mat));
}

void emxEnsureCapacity(tMatrix2D *emxArray, int oldNumel, unsigned int elementSize)
{
    int newNumel;
    int i;
    double *newData;
    if (oldNumel < 0)
    {
        oldNumel = 0;
    }
    newNumel = 1;
    for (i = 0; i < emxArray->numDimensions; i++)
    {
        newNumel *= emxArray->size[i];
    }

    if (newNumel > emxArray->allocatedSize)
    {
        i = emxArray->allocatedSize;
        if (i < 16)
        {
            i = 16;
        }
        while (i < newNumel)
        {
            if (i > 1073741823)
            {
                i =(2147483647);//MAX_int32_T;
            }
            else
            {
                i <<= 1;
            }
        }

        newData = (double*) calloc((unsigned int)i, elementSize);
        if (emxArray->data != NULL)
        {
            memcpy(newData, emxArray->data, elementSize * oldNumel);
            if (emxArray->canFreeData)
            {
                free(emxArray->data);
            }
        }
        emxArray->data = newData;
        emxArray->allocatedSize = i;
        emxArray->canFreeData = true;
    }
}

void Matrix2D_Set_Size(tMatrix2D *mat, int rows, int cols)
{
    int old_numel;
    old_numel = mat->size[0] * mat->size[1];
    mat->size[0] = rows;
    mat->size[1] = cols;
    emxEnsureCapacity(mat, old_numel, sizeof(double));
}

int Matrix2D_Size(const tMatrix2D *var, int dim)
{
    // ONE BASED!!
    if (var->numDimensions >= dim)
    {
        return var->size[dim - 1];
    }
    else
    {
        return 0;
    }
}

int Matrix2D_Get_ncols(const tMatrix2D *var)
{
    return Matrix2D_Size(var, 2);
}

int Matrix2D_Get_nrows(const tMatrix2D *var)
{
    return Matrix2D_Size(var, 1);
}

double Matrix2D_Get_ij(const tMatrix2D *var, int i, int j)
{
    // ZERO BASED!!
    return var->data[var->size[0] * j + i];
}

void Matrix2D_Set_ij(const tMatrix2D *var, int i, int j, double value)
{
    // ZERO BASED!!
    var->data[var->size[0] * j + i] = value;
}

double *Matrix2D_Get_col(const tMatrix2D *var, int col)
{
    // ZERO BASED!!
    return (var->data + var->size[0] * col);
}

bool Matrix2D_Copy(const tMatrix2D *from, tMatrix2D *to)
{
    if (from->numDimensions != 2 || to->numDimensions != 2)
    {
        Matrix2D_Set_Size(to, 0,0);
        return false;
    }

    int sz1 = Matrix2D_Size(from,1);
    int sz2 = Matrix2D_Size(from,2);
    Matrix2D_Set_Size(to, sz1, sz2);
    int numel = sz1*sz2;
    for (int i = 0; i < numel; i++)
    {
        to->data[i] = from->data[i];
    }

    return true;
}


void Matrix2D_Add(tMatrix2D *var, const double *array, int numel)
{
    int oldnumel;
    int size1 = var->size[0];
    int size2 = var->size[1];
    oldnumel = size1*size2;
    var->size[1] = size2 + 1;
    emxEnsureCapacity(var, oldnumel, (int)sizeof(double));
    numel = qMin(numel, size1);
    for (int i=0; i<numel; i++){
        var->data[size1*size2 + i] = array[i];
    }
}

void Matrix2D_Add(tMatrix2D *var, const tMatrix2D *varadd)
{
    int oldnumel;
    int size1 = var->size[0];
    int size2 = var->size[1];
    int size1_ap = varadd->size[0];
    int size2_ap = varadd->size[1];
    int numel = size1_ap*size2_ap;
    if (size1 != size1_ap)
    {
        return;
    }
    oldnumel = size1*size2;
    var->size[1] = size2 + size2_ap;
    emxEnsureCapacity(var, oldnumel, (int)sizeof(double));
    for (int i=0; i<numel; i++)
    {
        var->data[size1*size2 + i] = varadd->data[i];
    }
}

void Debug_Array(const double *array, int arraysize)
{
    int i;
    QString strout;
    for (i = 0; i < arraysize; i++) {
        strout.append(QString::number(array[i], 'f', 3));
        if (i < arraysize - 1) {
            strout.append(" , ");
        }
    }
    qDebug().noquote() << strout;
}

void Debug_Matrix2D(const tMatrix2D *emx)
{
    int size1;
    int size2;
    int j;
    double *column;
    size1 = Matrix2D_Get_nrows(emx);
    size2 = Matrix2D_Get_ncols(emx);
    qDebug().noquote() << "Matrix size = " << size1 << " x " << size2;
    if (size1*size2 == 0)
    {
        return;
    }
    for (j = 0; j<size2; j++)
    {
        column = Matrix2D_Get_col(emx, j);
        Debug_Array(column, size1);
    }
}

void Matrix2D_Save(QDataStream *st, tMatrix2D *emx)
{
    int i;
    *st << emx->numDimensions;
    int size_values = 1;
    for (i = 0; i < emx->numDimensions; i++)
    {
        qint32 sizei = emx->size[i];
        size_values = size_values * sizei;
        *st << sizei;
    }
    for (i = 0; i < size_values; i++)
    {
        *st << emx->data[i];
    }
}

void Matrix2D_Save(QTextStream *st, tMatrix2D *emx, bool csv)
{
    int size1;
    int size2;
    int j;
    double *column;
    size1 = Matrix2D_Get_nrows(emx);
    size2 = Matrix2D_Get_ncols(emx);
    //*st << "% Matrix size = " << size1 << " x " << size2;
    if (size1 * size2 == 0)
    {
        return;
    }

    if (csv)
    {
        for (j = 0; j<size2; j++)
        {
            column = Matrix2D_Get_col(emx, j);
            for (int i = 0; i < size1; i++)
            {
                *st << QString::number(column[i], 'f', 8) << ", ";
            }
            *st << "\n";
        }
    }
    else
    {
        for (j = 0; j<size2; j++)
        {
            column = Matrix2D_Get_col(emx, j);
            *st << "[";
            for (int i = 0; i < size1; i++)
            {
                *st << QString::number(column[i], 'f', 8) << " ";
            }
            *st << "];\n";
        }
    }
}

void Matrix2D_Load(QDataStream *st, tMatrix2D **emx)
{
    if (st->atEnd())
    {
        qDebug() << "No data to read";
        return;
    }

    if (*emx != nullptr)
    {
        Matrix2D_Delete(emx);
    }

    int i;
    qint32 ndim;
    qint32 sizei;    
    *st >> ndim;
    qDebug() << "Loading matrix of dimensions: " << ndim;
    emxInit_real_T(emx, ndim);
    int size_values = 1;
    for (i = 0; i < ndim; i++)
    {
        *st >> sizei;
        size_values = size_values * sizei;
        (*emx)->size[i] = sizei;
    }
    //emxEnsureCapacity((emxArray__common *) *emx, 0, (int32_T)sizeof(real_T));
    emxEnsureCapacity(*emx, 0, sizeof(double));
    double value;
    for (i = 0; i < size_values; i++)
    {
        *st >> value;
        (*emx)->data[i] = value;
    }
}
