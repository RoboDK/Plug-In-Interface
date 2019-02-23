#include "robodktypes.h"
#include <QtMath>



//----------------------------------- tJoints class ------------------------
tJoints::tJoints(int ndofs){
    _nDOFs = qMin(ndofs, RDK_SIZE_JOINTS_MAX);
    for (int i=0; i<_nDOFs; i++){
        _Values[i] = 0.0;
    }
}
tJoints::tJoints(const tJoints &copy){
    SetValues(copy._Values, copy._nDOFs);
}
tJoints::tJoints(const double *joints, int ndofs){
    SetValues(joints, ndofs);
}
tJoints::tJoints(const float *joints, int ndofs){
    int ndofs_ok = qMin(ndofs, RDK_SIZE_JOINTS_MAX);
    double jnts[RDK_SIZE_JOINTS_MAX];
    for (int i=0; i<ndofs_ok; i++){
        jnts[i] = joints[i];
    }
    SetValues(jnts, ndofs_ok);
}
tJoints::tJoints(const tMatrix2D *mat2d, int column, int ndofs){
    if (Matrix2D_Size(mat2d, 2) >= column){
        _nDOFs = 0;
        qDebug()<<"Warning: tMatrix2D column outside range when creating joints";
    }
    if (ndofs < 0){
        ndofs = Matrix2D_Size(mat2d, 1);
    }
    _nDOFs = qMin(ndofs, RDK_SIZE_JOINTS_MAX);

    double *ptr = Matrix2D_Get_col(mat2d, column);
    SetValues(ptr, _nDOFs);
}
tJoints::tJoints(const QString &str){
    _nDOFs = 0;
    FromString(str);
}

const double* tJoints::ValuesD() const{
    return _Values;
}
const float* tJoints::ValuesF() const{
    for (int i=0; i<RDK_SIZE_JOINTS_MAX; i++){
        ((float*)_ValuesF)[i] = _Values[i];
    }
    return _ValuesF;
}
#ifdef ROBODK_API_FLOATS
const float* tJoints::Values() const{
    return ValuesF();
}
#else
const double* tJoints::Values() const{
    return _Values;
}
#endif

double* tJoints::Data(){
    return _Values;
}


void tJoints::SetValues(const double *values, int ndofs){
    if (ndofs >= 0){
        _nDOFs = qMin(ndofs, RDK_SIZE_JOINTS_MAX);
    }
    for (int i=0; i<_nDOFs; i++){
        _Values[i] = values[i];
    }
}

void tJoints::SetValues(const float *values, int ndofs){
    if (ndofs >= 0){
        _nDOFs = qMin(ndofs, RDK_SIZE_JOINTS_MAX);
    }
    for (int i=0; i<_nDOFs; i++){
        _Values[i] = values[i];
    }
}
int tJoints::GetValues(double *values){
    for (int i=0; i<_nDOFs; i++){
        values[i] = _Values[i];
    }
    return _nDOFs;
}
QString tJoints::ToString(const QString &separator, int precision){
    QString values;
    if (_nDOFs <= 0){
        return values;
    }
    values.append(QString::number(_Values[0],'f',precision));
    for (int i=1; i<_nDOFs; i++){
        values.append(separator);
        values.append(QString::number(_Values[i],'f',precision));
    }
    return values;
}
bool tJoints::FromString(const QString &str){
    QStringList jnts_list = QString(str).replace(";",",").replace("\t",",").split(",", QString::SkipEmptyParts);
    _nDOFs = qMin(jnts_list.length(), RDK_SIZE_JOINTS_MAX);
    for (int i=0; i<_nDOFs; i++){
        QString stri(jnts_list.at(i));
        _Values[i] = stri.trimmed().toDouble();
    }
    return true;
}

int tJoints::Length(){
    return _nDOFs;
}
bool tJoints::Valid(){
    return _nDOFs <= 0;
}
//---------------------------------------------------------------------





//----------------------------------- Mat class ------------------------

Mat transl(double x, double y, double z){
    return Mat::transl(x,y,z);
}

Mat rotx(double rx){
    return Mat::rotx(rx);
}

Mat roty(double ry){
    return Mat::roty(ry);
}

Mat rotz(double rz){
    return Mat::rotz(rz);
}

Mat::Mat() : QMatrix4x4() {
    _valid = true;
    setToIdentity();
}
Mat::Mat(bool valid) : QMatrix4x4() {
    _valid = valid;
    setToIdentity();
}

Mat::Mat(const QMatrix4x4 &matrix) : QMatrix4x4(matrix) {
    // just copy
    _valid = true;
}
Mat::Mat(const Mat &matrix) : QMatrix4x4(matrix) {
    // just copy
    _valid = matrix._valid;
}

Mat::Mat(double nx, double ox, double ax, double tx, double ny, double oy, double ay, double ty, double nz, double oz, double az, double tz) :
    QMatrix4x4(nx, ox, ax, tx, ny, oy, ay, ty, nz, oz, az, tz, 0,0,0,1)
{
    _valid = true;
}
Mat::Mat(const double v[16]) :
    QMatrix4x4(v[0], v[4], v[8], v[12], v[1], v[5], v[9], v[13], v[2], v[6], v[10], v[14], v[3], v[7], v[11], v[15])
{
    _valid = true;
}
Mat::Mat(const float v[16]) :
    QMatrix4x4(v[0], v[4], v[8], v[12], v[1], v[5], v[9], v[13], v[2], v[6], v[10], v[14], v[3], v[7], v[11], v[15])
{
    _valid = true;
}



Mat::~Mat(){

}

void Mat::VX(tXYZ xyz) const{
    xyz[0] = Get(0, 0);
    xyz[1] = Get(1, 0);
    xyz[2] = Get(2, 0);
}
void Mat::VY(tXYZ xyz) const{
    xyz[0] = Get(0, 1);
    xyz[1] = Get(1, 1);
    xyz[2] = Get(2, 1);
}
void Mat::VZ(tXYZ xyz) const{
    xyz[0] = Get(0, 2);
    xyz[1] = Get(1, 2);
    xyz[2] = Get(2, 2);
}
void Mat::Pos(tXYZ xyz) const{
    xyz[0] = Get(0, 3);
    xyz[1] = Get(1, 3);
    xyz[2] = Get(2, 3);
}

void Mat::setVX(double x, double y, double z){
    Set(0,0, x);
    Set(1,0, y);
    Set(2,0, z);
}
void Mat::setVY(double x, double y, double z){
    Set(0,1, x);
    Set(1,1, y);
    Set(2,1, z);
}
void Mat::setVZ(double x, double y, double z){
    Set(0,2, x);
    Set(1,2, y);
    Set(2,2, z);
}
void Mat::setPos(double x, double y, double z){
    Set(0,3, x);
    Set(1,3, y);
    Set(2,3, z);
}

void Mat::setVX(double xyz[3]){
    Set(0,0, xyz[0]);
    Set(1,0, xyz[1]);
    Set(2,0, xyz[2]);
}
void Mat::setVY(double xyz[3]){
    Set(0,1, xyz[0]);
    Set(1,1, xyz[1]);
    Set(2,1, xyz[2]);
}
void Mat::setVZ(double xyz[3]){
    Set(0,2, xyz[0]);
    Set(1,2, xyz[1]);
    Set(2,2, xyz[2]);
}
void Mat::setPos(double xyz[3]){
    Set(0,3, xyz[0]);
    Set(1,3, xyz[1]);
    Set(2,3, xyz[2]);
}



void Mat::Set(int i, int j, double value){
    QVector4D rw(this->row(i));
    rw[j] = value;
    setRow(i, rw);
    // the following should not crash!!
    //float **dt_ok = (float**) data();
    //dt_ok[i][j] = value;
}

double Mat::Get(int i, int j) const{
    return row(i)[j];
    // the following hsould be allowed!!
    //return ((const float**)data())[i][j];
}

Mat Mat::inv() const{
    return this->inverted();
}



//----------------------------------------------------

void Mat::ToXYZRPW(tXYZWPR xyzwpr) const{
    double x = Get(0,3);
    double y = Get(1,3);
    double z = Get(2,3);
    double w, p, r;
    if (Get(2,0) > (1.0 - 1e-6)){
        p = -M_PI*0.5;
        r = 0;
        w = atan2(-Get(1,2), Get(1,1));
    } else if (Get(2,0) < -1.0 + 1e-6){
        p = 0.5*M_PI;
        r = 0;
        w = atan2(Get(1,2),Get(1,1));
    } else {
        p = atan2(-Get(2, 0), sqrt(Get(0, 0) * Get(0, 0) + Get(1, 0) * Get(1, 0)));
        w = atan2(Get(1, 0), Get(0, 0));
        r = atan2(Get(2, 1), Get(2, 2));
    }
    xyzwpr[0] = x;
    xyzwpr[1] = y;
    xyzwpr[2] = z;
    xyzwpr[3] = r*180.0/M_PI;
    xyzwpr[4] = p*180.0/M_PI;
    xyzwpr[5] = w*180.0/M_PI;
}

QString Mat::ToString(const QString &separator, int precision, bool in_xyzrpw) const{
    tXYZWPR xyzwpr;
    ToXYZRPW(xyzwpr);

    QString str;
    str.append(QString::number(xyzwpr[0],'f',precision));
    for (int i=1; i<6; i++){
        str.append(separator);
        str.append(QString::number(xyzwpr[i],'f',precision));
    }
    return str;
}

bool Mat::FromString(const QString &pose_str){
    QStringList values_list = QString(pose_str).replace(";",",").replace("\t",",").split(",", QString::SkipEmptyParts);
    int nvalues = qMin(values_list.length(), 6);
    tXYZWPR xyzwpr;
    for (int i=0; i<6; i++){
        xyzwpr[i] = 0.0;
    }
    if (nvalues < 6){
        FromXYZRPW(xyzwpr);
        return false;
    }
    for (int i=0; i<nvalues; i++){
        QString stri(values_list.at(i));
        xyzwpr[i] = stri.trimmed().toDouble();
    }
    FromXYZRPW(xyzwpr);
    return true;
}

Mat Mat::XYZRPW_2_Mat(double x, double y, double z, double r, double p, double w){
    double a = r * M_PI / 180.0;
    double b = p * M_PI / 180.0;
    double c = w * M_PI / 180.0;
    double ca = cos(a);
    double sa = sin(a);
    double cb = cos(b);
    double sb = sin(b);
    double cc = cos(c);
    double sc = sin(c);
    return Mat(cb * cc, cc * sa * sb - ca * sc, sa * sc + ca * cc * sb, x, cb * sc, ca * cc + sa * sb * sc, ca * sb * sc - cc * sa, y, -sb, cb * sa, ca * cb, z);
}
Mat Mat::XYZRPW_2_Mat(tXYZWPR xyzwpr){
    return XYZRPW_2_Mat(xyzwpr[0], xyzwpr[1], xyzwpr[2], xyzwpr[3], xyzwpr[4], xyzwpr[5]);
}

void Mat::FromXYZRPW(tXYZWPR xyzwpr){
    Mat newmat = Mat::XYZRPW_2_Mat(xyzwpr[0], xyzwpr[1], xyzwpr[2], xyzwpr[3], xyzwpr[4], xyzwpr[5]);
    for (int i=0; i<4; i++){
        for (int j=0; j<4; j++){
            this->Set(i,j, newmat.Get(i,j));
        }
    }
}

const double* Mat::ValuesD() const {
    double* _ddata16_non_const = (double*) _ddata16;
    for(int i=0; i<16; ++i){
        _ddata16_non_const[i] = constData()[i];
    }
    return _ddata16;
}
const float* Mat::ValuesF() const {
    return constData();
}

#ifdef ROBODK_API_FLOATS
const float* Mat::Values() const {
    return constData();
}
#else
const double* Mat::Values() const {
    return ValuesD();
}

#endif



void Mat::Values(double data[16]) const{
    for(int i=0; i<16; ++i){
        data[i] = constData()[i];
    }
}
void Mat::Values(float data[16]) const{
    for(int i=0; i<16; ++i){
        data[i] = constData()[i];
    }
}
bool Mat::Valid() const{
    return _valid;
}

Mat Mat::transl(double x, double y, double z){
    Mat mat;
    mat.setToIdentity();
    mat.setPos(x, y, z);
    return mat;
}

Mat Mat::rotx(double rx){
    double cx = cos(rx);
    double sx = sin(rx);
    return Mat(1, 0, 0, 0, 0, cx, -sx, 0, 0, sx, cx, 0);
}

Mat Mat::roty(double ry){
    double cy = cos(ry);
    double sy = sin(ry);
    return Mat(cy, 0, sy, 0, 0, 1, 0, 0, -sy, 0, cy, 0);
}

Mat Mat::rotz(double rz){
    double cz = cos(rz);
    double sz = sin(rz);
    return Mat(cz, -sz, 0, 0, sz, cz, 0, 0, 0, 0, 1, 0);
}







//---------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------
/////////////////////////////////////
// 2D matrix functions
/////////////////////////////////////
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
    for (i = 0; i < numDimensions; i++) {
        emxArray->size[i] = 0;
    }
}
///
tMatrix2D* Matrix2D_Create() {
    tMatrix2D *matrix;
    emxInit_real_T((tMatrix2D**)(&matrix), 2);
    return matrix;
}


void emxFree_real_T(tMatrix2D **pEmxArray){
    if (*pEmxArray != (tMatrix2D *)NULL) {
        if (((*pEmxArray)->data != (double *)NULL) && (*pEmxArray)->canFreeData) {
            free((void *)(*pEmxArray)->data);
        }
        free((void *)(*pEmxArray)->size);
        free((void *)*pEmxArray);
        *pEmxArray = (tMatrix2D *)NULL;
    }
}

void Matrix2D_Delete(tMatrix2D **mat) {
    emxFree_real_T((tMatrix2D**)(mat));
}



void emxEnsureCapacity(tMatrix2D *emxArray, int oldNumel, unsigned int elementSize){
    int newNumel;
    int i;
    double *newData;
    if (oldNumel < 0) {
        oldNumel = 0;
    }
    newNumel = 1;
    for (i = 0; i < emxArray->numDimensions; i++) {
        newNumel *= emxArray->size[i];
    }
    if (newNumel > emxArray->allocatedSize) {
        i = emxArray->allocatedSize;
        if (i < 16) {
            i = 16;
        }
        while (i < newNumel) {
            if (i > 1073741823) {
                i =(2147483647);//MAX_int32_T;
            } else {
                i <<= 1;
            }
        }
        newData = (double*) calloc((unsigned int)i, elementSize);
        if (emxArray->data != NULL) {
            memcpy(newData, emxArray->data, elementSize * oldNumel);
            if (emxArray->canFreeData) {
                free(emxArray->data);
            }
        }
        emxArray->data = newData;
        emxArray->allocatedSize = i;
        emxArray->canFreeData = true;
    }
}

void Matrix2D_Set_Size(tMatrix2D *mat, int rows, int cols) {
    int old_numel;
    int numbel;
    old_numel = mat->size[0] * mat->size[1];
    mat->size[0] = rows;
    mat->size[1] = cols;
    numbel = rows*cols;
    emxEnsureCapacity(mat, old_numel, sizeof(double));
    /*for (i=0; i<numbel; i++){
    mat->data[i] = 0.0;
    }*/
}

int Matrix2D_Size(const tMatrix2D *var, int dim) { // ONE BASED!!
    if (var->numDimensions >= dim) {
        return var->size[dim - 1];
    }
    else {
        return 0;
    }
}
int Matrix2D_Get_ncols(const tMatrix2D *var) {
    return Matrix2D_Size(var, 2);
}
int Matrix2D_Get_nrows(const tMatrix2D *var) {
    return Matrix2D_Size(var, 1);
}
double Matrix2D_Get_ij(const tMatrix2D *var, int i, int j) { // ZERO BASED!!
    return var->data[var->size[0] * j + i];
}
void Matrix2D_SET_ij(const tMatrix2D *var, int i, int j, double value) { // ZERO BASED!!
    var->data[var->size[0] * j + i] = value;
}

double *Matrix2D_Get_col(const tMatrix2D *var, int col) { // ZERO BASED!!
    return (var->data + var->size[0] * col);
}


void Matrix2D_Add(tMatrix2D *var, const double *array, int numel){
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

void Matrix2D_Add(tMatrix2D *var, const tMatrix2D *varadd){
    int oldnumel;
    int size1 = var->size[0];
    int size2 = var->size[1];
    int size1_ap = varadd->size[0];
    int size2_ap = varadd->size[1];
    int numel = size1_ap*size2_ap;
    if (size1 != size1_ap){
        return;
    }
    oldnumel = size1*size2;
    var->size[1] = size2 + size2_ap;
    emxEnsureCapacity(var, oldnumel, (int)sizeof(double));
    for (int i=0; i<numel; i++){
        var->data[size1*size2 + i] = varadd->data[i];
    }
}

void Debug_Array(const double *array, int arraysize) {
    int i;
    for (i = 0; i < arraysize; i++) {
        //char chararray[500];  // You had better have room for what you are sprintf()ing!
        //sprintf(chararray, "%.3f", array[i]);
        //std::cout << chararray;
        printf("%.3f", array[i]);
        if (i < arraysize - 1) {
            //std::cout << " , ";
            printf(" , ");
        }
    }
}

void Debug_Matrix2D(const tMatrix2D *emx) {
    int size1;
    int size2;
    int j;
    double *column;
    size1 = Matrix2D_Get_nrows(emx);
    size2 = Matrix2D_Get_ncols(emx);
    printf("Matrix size = [%i, %i]\n", size1, size2);
    //std::out << "Matrix size = [%i, %i]" << size1 << " " << size2 << "]\n";
    for (j = 0; j<size2; j++) {
        column = Matrix2D_Get_col(emx, j);
        Debug_Array(column, size1);
        printf("\n");
        //std::cout << "\n";
    }
}
/*
void Debug_Mat(Mat pose, char show_full_pose) {
    tMatrix4x4 pose_tr;
    double xyzwpr[6];
    int j;
    if (show_full_pose > 0) {
        POSE_TR(pose_tr, pose);
        printf("Pose size = [4x4]\n");
        //std::cout << "Pose size = [4x4]\n";
        for (j = 0; j < 4; j++) {
            Debug_Array(pose_tr + j * 4, 4);
            printf("\n");
            //std::cout << "\n";
        }
    }
    else {
        POSE_2_XYZWPR(xyzwpr, pose);
        //std::cout << "XYZWPR = [ ";
        printf("XYZWPR = [ ");
        Debug_Array(xyzwpr, 6);
        printf(" ]\n");
        //std::cout << " ]\n";
    }
}
*/

