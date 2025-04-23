#include "opcua_server.h"

#include "pluginopcua.h"
#include "robodktypes.h"
#include "irobodk.h"
#include "iitem.h"

#include "robodktools.h"
#include "opcua_tools.h"

#include <thread>
#include <signal.h>
#include <errno.h> // errno, EINTR
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


#include <QFile>
#include <QTimer>


#ifdef _MSC_VER
#define _CRT_SECURE_NO_WARNINGS //disable fopen deprecation warning in msvs
#endif


//----------------------------
#include <QDebug>
#include <QString>
#include <QAction>

#include <QStatusBar>
#include <QDateTime>


#define nDOFs_MAX 12



UA_Logger logger = UA_Log_Stdout;

QString ActiveStationParameter;


/// Turns on when the server started running. We can set this flag to false to stop the server
UA_Boolean SERVER_RUNNING;

/// True when the server stopped and we free memory
int SERVER_RUNNING_PORT;

QTimer TimerStatus;

int opc_server_thread(PluginOPCUA *pPlugin, unsigned short port);


// Important: We need to trigger messages as a Queued signal because we are running different threads!
void ShowMessage(PluginOPCUA *pPlugin, const QString &msg){
    qDebug() << msg;
    if (pPlugin != nullptr){
        pPlugin->EmitShowMessage(msg);
    }
}


opcua_server::opcua_server(PluginOPCUA *plugin) : QObject(NULL){
    SERVER_RUNNING = UA_FALSE;
    SERVER_RUNNING_PORT = -1;
    Port = 4840;
    AutoStart = false;
    pPlugin = plugin;

    // Keep an eye on the status flag to make sure we are running the server
    connect(&TimerStatus, SIGNAL(timeout()), this, SLOT(CheckStatus()));
    TimerStatus.setInterval(200); // in msec
    TimerStatus.start();
}
opcua_server::~opcua_server(){
    pPlugin = nullptr; // prevent using the plugin interface when we are closing the plugin
    Stop();
}

void opcua_server::Start(){
    int port = pPlugin->Server->Port;
    if (SERVER_RUNNING == UA_TRUE){
        ShowMessage(pPlugin, tr("The OPC UA server is already running"));
        return;
    }
    if (SERVER_RUNNING_PORT >= 0){
        ShowMessage(pPlugin, tr("The OPC UA server is shutting down. Try again"));
        return;
    }

    pPlugin->action_StartServer->setChecked(true);

    std::thread opc_thread(opc_server_thread, pPlugin, port);
    opc_thread.detach();
    //Thread->start();
}
void opcua_server::Stop(){
    if (pPlugin != nullptr){
        // Make sure that we don't use the plugin interface when we are closing the plugin (otherwise it crashes)
        pPlugin->action_StartServer->setChecked(false);
        ShowMessage(pPlugin, tr("Stopping OPC UA server..."));
        if (SERVER_RUNNING == UA_FALSE){
            ShowMessage(pPlugin, tr("OPC Server already stopped"));
        }        
    }
    SERVER_RUNNING = UA_FALSE;
}

bool opcua_server::IsStopped(){
    return SERVER_RUNNING_PORT < 0 && SERVER_RUNNING == UA_FALSE;
}

void opcua_server::CheckStatus(){
    pPlugin->action_StartServer->setChecked(SERVER_RUNNING);
}



QString opcua_server::Status(){
    if (SERVER_RUNNING == UA_TRUE){
        return tr("Server Running on port %1").arg(SERVER_RUNNING_PORT);
    } else if (SERVER_RUNNING_PORT >= 0){
        return tr("Stopping Server...");
    }
    return tr("Server Stopped");
}


static UA_ByteString loadCertificate(void) {
    UA_ByteString certificate = UA_STRING_NULL;
    FILE *fp = nullptr;
    //FIXME: a potiential bug of locating the certificate, we need to get the path from the server's config
    fp=fopen("server_cert.der", "rb");

    if(!fp) {
        errno = 0; // we read errno also from the tcp layer...
        return certificate;
    }

    fseek(fp, 0, SEEK_END);
    certificate.length = (size_t)ftell(fp);
    certificate.data = (UA_Byte*) malloc(certificate.length*sizeof(UA_Byte));
    if(!certificate.data)
        return certificate;

    fseek(fp, 0, SEEK_SET);
    if(fread(certificate.data, sizeof(UA_Byte), certificate.length, fp) < (size_t)certificate.length)
        UA_ByteString_deleteMembers(&certificate); // error reading the cert
    fclose(fp);

    return certificate;
}

// Handle the server stopping
static void stopHandler(int sign) {
    UA_LOG_INFO(logger, UA_LOGCATEGORY_SERVER, "Stopping RoboDK OPC UA server");
    SERVER_RUNNING = UA_FALSE;

}

// Get time according to RoboDK's computer
static UA_StatusCode read_Time(void *h, const UA_NodeId nodeId, UA_Boolean sourceTimeStamp, const UA_NumericRange *range, UA_DataValue *value) {
    Q_UNUSED(h)
    if(range) {
        value->hasStatus = true;
        value->status = UA_STATUSCODE_BADINDEXRANGEINVALID;
        return UA_STATUSCODE_GOOD;
    }
    UA_DateTime currentTime = UA_DateTime_now();
    UA_Variant_setScalarCopy(&value->value, &currentTime, &UA_TYPES[UA_TYPES_DATETIME]);
    value->hasValue = true;
    if(sourceTimeStamp) {
        value->hasSourceTimestamp = true;
        value->sourceTimestamp = currentTime;
    }
    return UA_STATUSCODE_GOOD;
}

static UA_StatusCode read_SimRatio(void *h, const UA_NodeId nodeId, UA_Boolean sourceTimeStamp, const UA_NumericRange *range, UA_DataValue *value) {
    PluginOPCUA *plugin = (PluginOPCUA*)h;
    if(range) {
        value->hasStatus = true;
        value->status = UA_STATUSCODE_BADINDEXRANGEINVALID;
        return UA_STATUSCODE_GOOD;
    }
    double ratio = plugin->RDK->SimulationSpeed();
    UA_Variant_setScalarCopy(&value->value, &ratio, &UA_TYPES[UA_TYPES_DOUBLE]);
    value->hasValue = true;
    if(sourceTimeStamp) {
        value->hasSourceTimestamp = true;
        value->sourceTimestamp = UA_DateTime_now();
    }
    return UA_STATUSCODE_GOOD;
}

UA_StatusCode write_SimRatio(void *h, const UA_NodeId nodeid, const UA_Variant *data, const UA_NumericRange *range) {
    PluginOPCUA *plugin = (PluginOPCUA*)h;
    UA_Double simulation_ratio;
    simulation_ratio = ((UA_Double*) (data->data))[0];
    plugin->RDK->setSimulationSpeed(simulation_ratio);
    ShowMessage(plugin, QObject::tr("New RoboDK simulation speed set to %1").arg(simulation_ratio));
    return UA_STATUSCODE_GOOD;
}

static UA_StatusCode read_OpenStationName(void *h, const UA_NodeId nodeid, UA_Boolean sourceTimeStamp, const UA_NumericRange *range, UA_DataValue *value) {
    PluginOPCUA *plugin = (PluginOPCUA*)h;
    if(range) {
        value->hasStatus = true;
        value->status = UA_STATUSCODE_BADINDEXRANGEINVALID;
        return UA_STATUSCODE_GOOD;
    }
    QString str_stationname = plugin->RDK->getActiveStation()->Name();
    Str_2_Var(str_stationname, &value->value);
    value->hasValue = true;
    if(sourceTimeStamp) {
        value->hasSourceTimestamp = true;
        value->sourceTimestamp = UA_DateTime_now();
    }
    return UA_STATUSCODE_GOOD;
}

UA_StatusCode write_OpenStationName(void *h, const UA_NodeId nodeid, const UA_Variant *data, const UA_NumericRange *range) {
    PluginOPCUA *plugin = (PluginOPCUA*)h;
    QString stationname;
    Var_2_Str(data+0, stationname);
    ShowMessage(plugin, QObject::tr("New station set to %1").arg(stationname));

    bool problems = false;
    if (!stationname.endsWith(".rdk", Qt::CaseInsensitive)){
        ShowMessage(plugin, QObject::tr("File should end with '.rdk': %1").arg(stationname));
        problems = true;
    } else if (!QFile(stationname).exists()){
        ShowMessage(plugin, QObject::tr("File not found: %1").arg(stationname));
        problems = true;
    } else {
        Item station = plugin->RDK->AddFile(stationname);
        if (station == nullptr){
            problems = true;
        }
    }
    if (problems){
        ShowMessage(plugin, QObject::tr("File not valid or not found: %1").arg(stationname));
        ShowMessage(plugin, QObject::tr("Current station: %1").arg(plugin->RDK->getActiveStation()->Name()));
    }
    return UA_STATUSCODE_GOOD;
}
static UA_StatusCode read_StationParameter(void *h, const UA_NodeId nodeid, UA_Boolean sourceTimeStamp, const UA_NumericRange *range, UA_DataValue *value) {
    Q_UNUSED(h)
    if(range) {
        value->hasStatus = true;
        value->status = UA_STATUSCODE_BADINDEXRANGEINVALID;
        return UA_STATUSCODE_GOOD;
    }
    Str_2_Var(ActiveStationParameter, &value->value);
    value->hasValue = true;
    if(sourceTimeStamp) {
        value->hasSourceTimestamp = true;
        value->sourceTimestamp = UA_DateTime_now();
    }
    return UA_STATUSCODE_GOOD;
}

UA_StatusCode write_StationParameter(void *h, const UA_NodeId nodeid, const UA_Variant *data, const UA_NumericRange *range) {
    PluginOPCUA *plugin = (PluginOPCUA*)h;
    Var_2_Str(data+0, ActiveStationParameter);
    ShowMessage(plugin, QObject::tr("Active Station parameter set to %1").arg(ActiveStationParameter));
    return UA_STATUSCODE_GOOD;
}
static UA_StatusCode read_StationValue(void *h, const UA_NodeId nodeid, UA_Boolean sourceTimeStamp, const UA_NumericRange *range, UA_DataValue *value) {
    PluginOPCUA *plugin = (PluginOPCUA*)h;
    if(range) {
        value->hasStatus = true;
        value->status = UA_STATUSCODE_BADINDEXRANGEINVALID;
        return UA_STATUSCODE_GOOD;
    }
    QString station_value = plugin->RDK->getParam(ActiveStationParameter);
    Str_2_Var(station_value, &value->value);
    value->hasValue = true;
    if(sourceTimeStamp) {
        value->hasSourceTimestamp = true;
        value->sourceTimestamp = UA_DateTime_now();
    }
    return UA_STATUSCODE_GOOD;
}

UA_StatusCode write_StationValue(void *h, const UA_NodeId nodeid, const UA_Variant *data, const UA_NumericRange *range) {
    PluginOPCUA *plugin = (PluginOPCUA*)h;
    QString stationvalue;
    Var_2_Str(data+0, stationvalue);
    ShowMessage(plugin, QObject::tr("Active Station value set to %1").arg(stationvalue));
    plugin->RDK->setParam(ActiveStationParameter, stationvalue);
    return UA_STATUSCODE_GOOD;
}

#ifdef UA_ENABLE_METHODCALLS


static UA_StatusCode setJoints(void *h, const UA_NodeId objectId, size_t inputSize, const UA_Variant *input, size_t outputSize, UA_Variant *output) {
    PluginOPCUA *plugin = (PluginOPCUA*)h;
    qDebug()<<"Setting joints";
    if (inputSize < 2){
        qDebug()<<"Input size: " << inputSize << "  Output size: " << outputSize;
        return UA_STATUSCODE_BADARGUMENTSMISSING;
    }
    Item item;
    if (!Var_2_Item(input + 0, &item, plugin->RDK)){
        qDebug()<<"Invalid item";
        return UA_STATUSCODE_BADARGUMENTSMISSING;
    }
    //if (!plugin->RDK->Valid(item)){
    //        ShowMessage(plugin, QObject::tr("setJoints: RoboDK Item provided is not valid"));
    //        return UA_STATUSCODE_BADARGUMENTSMISSING;
    //}

    double joint_values[nDOFs_MAX];

    // Retrieve current robot joints and number of axes
    tJoints current_joints = item->Joints();
    current_joints.GetValues(joint_values);
    int joints_ndofs = current_joints.Length();


    //Var_2_DoubleArray(input+1, joints, nDOFs_MAX);
    if (!Var_2_DoubleArray(input+1, joint_values, nDOFs_MAX)){
        qDebug()<<"Invalid double array";
        return UA_STATUSCODE_BADARGUMENTSMISSING;
    }
    tJoints new_joints(joint_values, joints_ndofs);
    item->setJoints(new_joints);
    plugin->RDK->Render();
    return UA_STATUSCODE_GOOD;
}
static UA_StatusCode setJointsStr(void *h, const UA_NodeId objectId, size_t inputSize, const UA_Variant *input, size_t outputSize, UA_Variant *output) {
    PluginOPCUA *plugin = (PluginOPCUA*)h;
    if (inputSize < 2){
        qDebug()<<"Input size: " << inputSize << "  Output size: " << outputSize;
        return UA_STATUSCODE_BADARGUMENTSMISSING;
    }
    QString str_item;
    QString str_joints;
    if (!Var_2_Str(input+0, str_item)){
        return UA_STATUSCODE_BADARGUMENTSMISSING;
    }
    if (!Var_2_Str(input+1, str_joints)){
        return UA_STATUSCODE_BADARGUMENTSMISSING;
    }
    Item item = plugin->RDK->getItem(str_item);
    if (!plugin->RDK->Valid(item)){ //if (!ItemValid(robot)){
        ShowMessage(plugin, QObject::tr("setJointsStr: RoboDK Item provided is not valid"));
        return UA_STATUSCODE_BADARGUMENTSMISSING;
    }
    double joint_values[nDOFs_MAX];
    tJoints current_joints = item->Joints();
    current_joints.GetValues(joint_values);
    int joints_ndofs = current_joints.Length();
    int numel = nDOFs_MAX;
    string_2_doubles(str_joints, joint_values, &numel);
    if (numel <= 0){
        ShowMessage(plugin, QObject::tr("setJointsStr: Invalid joints string"));
        return UA_STATUSCODE_BADARGUMENTSMISSING;
    }
    tJoints new_joints(joint_values, joints_ndofs);
    item->setJoints(new_joints);
    plugin->RDK->Render();
    return UA_STATUSCODE_GOOD;
}

static UA_StatusCode getJoints(void *h, const UA_NodeId objectId, size_t inputSize, const UA_Variant *input, size_t outputSize, UA_Variant *output) {
    PluginOPCUA *plugin = (PluginOPCUA*)h;
    /* input is a scalar string (checked by the server) */
    if (inputSize < 1 || outputSize < 1){
        return UA_STATUSCODE_BADARGUMENTSMISSING;
    }
    Item item;
    if (!Var_2_Item(input + 0, &item, plugin->RDK)){
        return UA_STATUSCODE_BADARGUMENTSMISSING;
    }
    if (!plugin->RDK->Valid(item)){
        ShowMessage(plugin, QObject::tr("getJoints: RoboDK Item provided is not valid"));
        return UA_STATUSCODE_BADARGUMENTSMISSING;
    }
    double joints[nDOFs_MAX];
    for (int i=0; i<nDOFs_MAX; i++){
        joints[i] = 0;
    }
    DoubleArray_2_Var(item->Joints().Values(), nDOFs_MAX, output + 0);
    return UA_STATUSCODE_GOOD;
}

static UA_StatusCode getJointsStr(void *h, const UA_NodeId objectId, size_t inputSize, const UA_Variant *input, size_t outputSize, UA_Variant *output) {
    PluginOPCUA *plugin = (PluginOPCUA*)h;
    /* input is a scalar string (checked by the server) */
    if (inputSize < 1 || outputSize < 1){
        //plugin->AddLog(QObject::tr("Invalid Input/Output size for getJointsStr: %1/%2").arg(inputSize).arg(outputSize));
        return UA_STATUSCODE_BADARGUMENTSMISSING;
    }
    QString str_item;
    if (!Var_2_Str(input+0, str_item)){
        return UA_STATUSCODE_BADARGUMENTSMISSING;
    }
    Item item = plugin->RDK->getItem(str_item);
    if (!plugin->RDK->Valid(item)){ //if (!ItemValid(item)){
        ShowMessage(plugin, QObject::tr("getJointsStr: RoboDK Item name provided is not valid"));
        return UA_STATUSCODE_BADARGUMENTSMISSING;
    }
    tJoints joints = item->Joints();
    QString str_joints = doubles_2_string(joints.ValuesD(), joints.Length(), 6, ", ");
    Str_2_Var(str_joints, output+0);
    return UA_STATUSCODE_GOOD;
}
static UA_StatusCode getItem(void *h, const UA_NodeId objectId, size_t inputSize, const UA_Variant *input, size_t outputSize, UA_Variant *output) {
    PluginOPCUA *plugin = (PluginOPCUA*)h;
    if (inputSize < 1 || outputSize < 1){
        return UA_STATUSCODE_BADARGUMENTSMISSING;
    }
    QString name;
    if (!Var_2_Str(input + 0, name)){
        return UA_STATUSCODE_BADARGUMENTSMISSING;
    }
    // Retrieve the RoboDK item as a pointer
    Item item = plugin->RDK->getItem(name);
    if (!plugin->RDK->Valid(item)){ //if (item == nullptr){
        ShowMessage(plugin, QObject::tr("getItem: RoboDK Item name provided does not exist"));
    }
    UA_UInt64 item_id = (UA_UInt64)item;
    Item_2_Var(item_id, output+0);
    return UA_STATUSCODE_GOOD;
}
#endif





int opc_server_thread(PluginOPCUA *pPlugin, unsigned short port) {
    SERVER_RUNNING_PORT = port;

    UA_ServerNetworkLayer nl = UA_ServerNetworkLayerTCP(UA_ConnectionConfig_standard, port);
    UA_ServerConfig config = UA_ServerConfig_standard;
    config.networkLayers = &nl;
    config.networkLayersSize = 1;

    // load certificate
    config.serverCertificate = loadCertificate();
    config.usernamePasswordLogins;

    UA_Server *server = UA_Server_new(config);

    // Add the RoboDK version as a static variable node to the server
    QString RoboDKVersion = pPlugin->RDK->Version();
    UA_VariableAttributes rdkver;
    UA_VariableAttributes_init(&rdkver);
    rdkver.description = UA_LOCALIZEDTEXT("en_US", RoboDKVersion.toUtf8().constData());
    rdkver.displayName = UA_LOCALIZEDTEXT("en_US", "RoboDK");
    Str_2_Var(RoboDKVersion, &rdkver.value);
    //myVar.value = UA_STRING(RoboDKVersion.toUtf8().constData());
    rdkver.accessLevel = UA_ACCESSLEVELMASK_READ;// | UA_ACCESSLEVELMASK_WRITE;
    //UA_Int32 myInteger = 0;
    //UA_Variant_setScalarCopy(&rdkver.value, &myInteger, &UA_TYPES[UA_TYPES_INT32]);
    const UA_QualifiedName rdkverName = UA_QUALIFIEDNAME(1, "version");
    const UA_NodeId rdkverNodeId = UA_NODEID_STRING(1, "ver");
    UA_NodeId parentNodeId = UA_NODEID_NUMERIC(0, UA_NS0ID_OBJECTSFOLDER);
    UA_NodeId parentReferenceNodeId = UA_NODEID_NUMERIC(0, UA_NS0ID_ORGANIZES);
    UA_Server_addVariableNode(server, rdkverNodeId, parentNodeId, parentReferenceNodeId, rdkverName, UA_NODEID_NULL, rdkver, NULL, NULL);
    UA_Variant_deleteMembers(&rdkver.value);

    // add a variable with the datetime data source
    UA_DataSource dateDataSource;// = (UA_DataSource) {.handle = NULL, .read = readTimeData, .write = NULL};
    dateDataSource.handle = pPlugin;
    dateDataSource.read = read_Time;
    dateDataSource.write = nullptr;
    UA_VariableAttributes v_attr;
    UA_VariableAttributes_init(&v_attr);
    v_attr.description = UA_LOCALIZEDTEXT("en_US","RoboDK server time");
    v_attr.displayName = UA_LOCALIZEDTEXT("en_US","time");
    v_attr.accessLevel = UA_ACCESSLEVELMASK_READ;// | UA_ACCESSLEVELMASK_WRITE;
    const UA_QualifiedName dateName = UA_QUALIFIEDNAME(1, "time");
    UA_NodeId dataSourceId;
    UA_Server_addDataSourceVariableNode(server, UA_NODEID_STRING(1, "time"), UA_NODEID_NUMERIC(0, UA_NS0ID_OBJECTSFOLDER),
                                        UA_NODEID_NUMERIC(0, UA_NS0ID_ORGANIZES), dateName,
                                        UA_NODEID_NULL, v_attr, dateDataSource, &dataSourceId);

    // Add a variable to represent the simulation speed
    UA_DataSource ds_ratio;// = (UA_DataSource) {.handle = NULL, .read = readTimeData, .write = NULL};
    ds_ratio.handle = pPlugin;
    ds_ratio.read = read_SimRatio;
    ds_ratio.write = write_SimRatio;
    UA_VariableAttributes va_ratio;
    UA_VariableAttributes_init(&va_ratio);
    va_ratio.description = UA_LOCALIZEDTEXT("en_US","Simulation speed ratio");
    va_ratio.displayName = UA_LOCALIZEDTEXT("en_US","SimulationSpeed");
    va_ratio.accessLevel = UA_ACCESSLEVELMASK_READ | UA_ACCESSLEVELMASK_WRITE;
    const UA_QualifiedName simratio_name = UA_QUALIFIEDNAME(1, "Simulation speed ratio");
    UA_NodeId dataSourceId_sim;
    UA_Server_addDataSourceVariableNode(server, UA_NODEID_NUMERIC(1, 3), UA_NODEID_NUMERIC(0, UA_NS0ID_OBJECTSFOLDER),
                                        UA_NODEID_NUMERIC(0, UA_NS0ID_ORGANIZES), simratio_name,
                                        UA_NODEID_NULL, va_ratio, ds_ratio, &dataSourceId_sim);

    // Add a variable to get/set the open station item
    UA_DataSource ds_stationname;
    ds_stationname.handle = pPlugin;
    ds_stationname.read = read_OpenStationName;
    ds_stationname.write = write_OpenStationName;
    UA_VariableAttributes va_station;
    UA_VariableAttributes_init(&va_station);
    va_station.description = UA_LOCALIZEDTEXT("en_US","Open RoboDK Station (RDK)");
    va_station.displayName = UA_LOCALIZEDTEXT("en_US","Station");
    va_station.accessLevel = UA_ACCESSLEVELMASK_READ | UA_ACCESSLEVELMASK_WRITE;
    const UA_QualifiedName openstation_descname = UA_QUALIFIEDNAME(1, "Open station name or path");
    UA_NodeId dataSourceId_rdk;
    UA_Server_addDataSourceVariableNode(server, UA_NODEID_NUMERIC(1, 4), UA_NODEID_NUMERIC(0, UA_NS0ID_OBJECTSFOLDER),
                                        UA_NODEID_NUMERIC(0, UA_NS0ID_ORGANIZES), openstation_descname,
                                        UA_NODEID_NULL, va_station, ds_stationname, &dataSourceId_rdk);

    // Read/write a customized Station parameter that you want to read
    UA_DataSource ds_param;
    ds_param.handle = pPlugin;
    ds_param.read = read_StationParameter;
    ds_param.write = write_StationParameter;
    UA_VariableAttributes va_param;
    UA_VariableAttributes_init(&va_param);
    va_param.description = UA_LOCALIZEDTEXT("en_US","Set the RoboDK Station variable to ready/write");
    va_param.displayName = UA_LOCALIZEDTEXT("en_US","StationParameter");
    va_param.accessLevel = UA_ACCESSLEVELMASK_READ | UA_ACCESSLEVELMASK_WRITE;
    const UA_QualifiedName parameter_descname = UA_QUALIFIEDNAME(1, "RoboDK Station Parameter");
    UA_NodeId dataSourceId_param;
    UA_Server_addDataSourceVariableNode(server, UA_NODEID_NUMERIC(1, 5), UA_NODEID_NUMERIC(0, UA_NS0ID_OBJECTSFOLDER),
                                        UA_NODEID_NUMERIC(0, UA_NS0ID_ORGANIZES), parameter_descname,
                                        UA_NODEID_NULL, va_param, ds_param, &dataSourceId_param);

    // Read/write the value of a customized Station parameter
    UA_DataSource ds_value;
    ds_value.handle = pPlugin;
    ds_value.read = read_StationValue;
    ds_value.write = write_StationValue;
    UA_VariableAttributes va_value;
    UA_VariableAttributes_init(&va_value);
    va_value.description = UA_LOCALIZEDTEXT("en_US","Set the RoboDK Station value to ready/write");
    va_value.displayName = UA_LOCALIZEDTEXT("en_US","StationValue");
    va_value.accessLevel = UA_ACCESSLEVELMASK_READ | UA_ACCESSLEVELMASK_WRITE;
    const UA_QualifiedName value_descname = UA_QUALIFIEDNAME(1, "RoboDK Station Value");
    UA_NodeId dataSourceId_value;
    UA_Server_addDataSourceVariableNode(server, UA_NODEID_NUMERIC(1, 6), UA_NODEID_NUMERIC(0, UA_NS0ID_OBJECTSFOLDER),
                                        UA_NODEID_NUMERIC(0, UA_NS0ID_ORGANIZES), value_descname,
                                        UA_NODEID_NULL, va_value, ds_value, &dataSourceId_value);


#ifdef UA_ENABLE_METHODCALLS

    // Add a method call to set the joints of a robot or a target
    // setJoints
    UA_Argument inArgs[2];
    UA_Argument_init(&inArgs[0]);
    UA_Argument_init(&inArgs[1]);
    inArgs[0].dataType = UA_TYPES[UA_TYPES_UINT64].typeId;
    inArgs[0].description = UA_LOCALIZEDTEXT("en_US", "RoboDK Item ID");
    inArgs[0].name = UA_STRING("Item ID");
    inArgs[0].arrayDimensionsSize = 0;
    inArgs[0].arrayDimensions = nullptr;
    inArgs[0].valueRank = -1;

    inArgs[1].dataType = UA_TYPES[UA_TYPES_DOUBLE].typeId;
    inArgs[1].description = UA_LOCALIZEDTEXT("en_US", "Joint Values (deg)");
    inArgs[1].name = UA_STRING("Joints");
    inArgs[1].arrayDimensionsSize = 1;
    inArgs[1].arrayDimensions = (UA_UInt32*) UA_Array_new(1, &UA_TYPES[UA_TYPES_DOUBLE]);
    inArgs[1].arrayDimensions[0] = nDOFs_MAX;
    inArgs[1].valueRank = -1;

    UA_MethodAttributes addmethodattributes;
    UA_MethodAttributes_init(&addmethodattributes);
    addmethodattributes.displayName = UA_LOCALIZEDTEXT("en_US", "setJoints");
    addmethodattributes.executable = true;
    addmethodattributes.userExecutable = true;
    UA_Server_addMethodNode(server, UA_NODEID_NUMERIC(1, 2001),
        UA_NODEID_NUMERIC(0, UA_NS0ID_OBJECTSFOLDER),
        UA_NODEID_NUMERIC(0, UA_NS0ID_HASCOMPONENT),
        UA_QUALIFIEDNAME(1, "setJoints"), addmethodattributes,
        &setJoints, // callback function
        pPlugin, // plugin handle
        2, inArgs, 0, nullptr, nullptr);

    // Add a method call to set the joints of a robot or a target given the item name
    // setJointsStr
    UA_Argument inSetJointsStr[2];
    UA_Argument_init(&inSetJointsStr[0]);
    UA_Argument_init(&inSetJointsStr[1]);
    inSetJointsStr[0].dataType = UA_TYPES[UA_TYPES_STRING].typeId;
    inSetJointsStr[0].description = UA_LOCALIZEDTEXT("en_US", "Robot name in RoboDK");
    inSetJointsStr[0].name = UA_STRING("Robot name");
    inSetJointsStr[0].arrayDimensionsSize = 0;
    inSetJointsStr[0].arrayDimensions = nullptr;
    inSetJointsStr[0].valueRank = -1;

    inSetJointsStr[1].dataType = UA_TYPES[UA_TYPES_STRING].typeId;
    inSetJointsStr[1].description = UA_LOCALIZEDTEXT("en_US", "Joint Values (deg) as a string");
    inSetJointsStr[1].name = UA_STRING("Joints");
    inSetJointsStr[1].arrayDimensionsSize = 0;
    inSetJointsStr[1].valueRank = -1;

    UA_MethodAttributes methodSetJointsStr;
    UA_MethodAttributes_init(&methodSetJointsStr);
    methodSetJointsStr.displayName = UA_LOCALIZEDTEXT("en_US", "setJointsStr");
    methodSetJointsStr.executable = true;
    methodSetJointsStr.userExecutable = true;
    UA_Server_addMethodNode(server, UA_NODEID_NUMERIC(1, 2002),
        UA_NODEID_NUMERIC(0, UA_NS0ID_OBJECTSFOLDER),
        UA_NODEID_NUMERIC(0, UA_NS0ID_HASCOMPONENT),
        UA_QUALIFIEDNAME(1, "setJointsStr"), methodSetJointsStr,
        &setJointsStr, // callback
        pPlugin, // plugin handle
        2, inSetJointsStr, 0, nullptr, nullptr);


    // Add a method call call to get the joints of a robot or a target
    // getJoints
    UA_Argument ingetJoints[1];
    UA_Argument outgetJoints[1];

    UA_Argument_init(&ingetJoints[0]);
    UA_Argument_init(&outgetJoints[0]);
    ingetJoints[0].dataType = UA_TYPES[UA_TYPES_UINT64].typeId;
    ingetJoints[0].description = UA_LOCALIZEDTEXT("en_US", "RoboDK Item ID");
    ingetJoints[0].name = UA_STRING("Item ID");
    ingetJoints[0].arrayDimensionsSize = 0;
    ingetJoints[0].arrayDimensions = nullptr;
    ingetJoints[0].valueRank = -1;

    outgetJoints[0].dataType = UA_TYPES[UA_TYPES_DOUBLE].typeId;
    outgetJoints[0].description = UA_LOCALIZEDTEXT("en_US", "Joint Values (deg)");
    outgetJoints[0].name = UA_STRING("Joints");
    outgetJoints[0].arrayDimensionsSize = 1;
    outgetJoints[0].arrayDimensions = (UA_UInt32*) UA_Array_new(1, &UA_TYPES[UA_TYPES_DOUBLE]);
    outgetJoints[0].arrayDimensions[0] = nDOFs_MAX;
    outgetJoints[0].valueRank = -1;

    UA_MethodAttributes method_getJoints;
    UA_MethodAttributes_init(&method_getJoints);
    method_getJoints.displayName = UA_LOCALIZEDTEXT("en_US", "getJoints");
    method_getJoints.executable = true;
    method_getJoints.userExecutable = true;
    UA_Server_addMethodNode(server, UA_NODEID_NUMERIC(1, 1001),
        UA_NODEID_NUMERIC(0, UA_NS0ID_OBJECTSFOLDER),
        UA_NODEID_NUMERIC(0, UA_NS0ID_HASCOMPONENT),
        UA_QUALIFIEDNAME(1, "getJoints"), method_getJoints,
        &getJoints, // callback function
        pPlugin, // plugin handle
        1, ingetJoints, 1, outgetJoints, nullptr);



    /////////////////////////////////////////////////////
    /// \brief getJointsStr
    ///
    UA_Argument ingetJointsStr[1];
    UA_Argument outgetJointsStr[1];

    UA_Argument_init(&ingetJointsStr[0]);
    UA_Argument_init(&outgetJointsStr[0]);
    inSetJointsStr[0].dataType = UA_TYPES[UA_TYPES_STRING].typeId;
    inSetJointsStr[0].description = UA_LOCALIZEDTEXT("en_US", "Robot name in RoboDK");
    inSetJointsStr[0].name = UA_STRING("Robot name");
    inSetJointsStr[0].arrayDimensionsSize = 0;
    inSetJointsStr[0].arrayDimensions = nullptr;
    inSetJointsStr[0].valueRank = -1;

    outgetJointsStr[0].dataType = UA_TYPES[UA_TYPES_STRING].typeId;
    outgetJointsStr[0].description = UA_LOCALIZEDTEXT("en_US", "Joint Values (deg) as string");
    outgetJointsStr[0].name = UA_STRING("Joints");
    outgetJointsStr[0].arrayDimensionsSize = 0;
    outgetJointsStr[0].valueRank = -1;

    UA_MethodAttributes methodGetJointsStr;
    UA_MethodAttributes_init(&methodGetJointsStr);
    methodGetJointsStr.displayName = UA_LOCALIZEDTEXT("en_US", "getJointsStr");
    methodGetJointsStr.executable = true;
    methodGetJointsStr.userExecutable = true;
    UA_Server_addMethodNode(server, UA_NODEID_NUMERIC(1, 1002),
        UA_NODEID_NUMERIC(0, UA_NS0ID_OBJECTSFOLDER),
        UA_NODEID_NUMERIC(0, UA_NS0ID_HASCOMPONENT),
        UA_QUALIFIEDNAME(1, "setJointsStr"), methodGetJointsStr,
        &getJointsStr,
        pPlugin,
        1, inSetJointsStr, 1, outgetJointsStr, nullptr);




    //////////////////////////////////////////////////////////////////
    /// \brief getItem
    ///
    UA_Argument inItem;
    UA_Argument_init(&inItem);
    inItem.arrayDimensionsSize = 0;
    inItem.arrayDimensions = nullptr;
    inItem.dataType = UA_TYPES[UA_TYPES_STRING].typeId;
    inItem.description = UA_LOCALIZEDTEXT("en_US", "Item name in the RoboDK station tree");
    inItem.name = UA_STRING("Item Name");
    inItem.valueRank = -1;


    UA_Argument outItem;
    UA_Argument_init(&outItem);
    outItem.arrayDimensionsSize = 0;
    outItem.arrayDimensions = nullptr;
    outItem.dataType = UA_TYPES[UA_TYPES_UINT64].typeId;
    outItem.description = UA_LOCALIZEDTEXT("en_US", "RoboDK Item ID (pointer)");
    outItem.name = UA_STRING("Item ID");
    outItem.valueRank = -1;

    UA_MethodAttributes methodItem;
    UA_MethodAttributes_init(&methodItem);
    methodItem.displayName = UA_LOCALIZEDTEXT("en_US", "getItem");
    methodItem.executable = true;
    methodItem.userExecutable = true;
    UA_Server_addMethodNode(server, UA_NODEID_NUMERIC(1, 1000),
        UA_NODEID_NUMERIC(0, UA_NS0ID_OBJECTSFOLDER),
        UA_NODEID_NUMERIC(0, UA_NS0ID_HASCOMPONENT),
        UA_QUALIFIEDNAME(1, "getItem"), methodItem,
        &getItem, // callback function
        pPlugin, // plugin handle
        1, &inItem, 1, &outItem, nullptr);

#endif

    // Run server until we stop the flag
    SERVER_RUNNING = UA_TRUE;
    ShowMessage(pPlugin, QObject::tr("RoboDK's OPC UA server running on port %1").arg(port));

    // start server and time the duration
    qint64 t_start_ms = QDateTime::currentDateTime().currentMSecsSinceEpoch();
    UA_StatusCode statusCode = UA_Server_run(server, &SERVER_RUNNING);
    qint64 t_duration_ms = QDateTime::currentDateTime().currentMSecsSinceEpoch() - t_start_ms;

    const UA_StatusCodeDescription *statusDesc = UA_StatusCode_description(statusCode);
    //qDebug() << "Server ended. Reason: " << statusDesc << " - " << statusDesc->explanation;

    QString hint_stop;
    if (t_duration_ms < 250){
        hint_stop = QObject::tr("Is the port being used by another application? ");
    }
    // Notify about server stop
    ShowMessage(pPlugin, QObject::tr("OPC-UA server stopped. %1%2").arg(hint_stop).arg(statusDesc->explanation));

    // deallocate certificate's memory
    UA_ByteString_deleteMembers(&config.serverCertificate);

    // cleanup
    UA_Server_delete(server);
    nl.deleteMembers(&nl);

    SERVER_RUNNING_PORT = -1;
    SERVER_RUNNING = UA_FALSE;
    return (int)statusCode;

}





