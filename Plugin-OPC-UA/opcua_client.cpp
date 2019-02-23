#include "opcua_client.h"


#include "pluginopcua.h"
#include "robodktypes.h"
#include "irobodk.h"
#include "iitem.h"

#include "robodktools.h"
#include "opcua_tools.h"

#include <QObject>

// Hold the pointer to the last client connection
UA_Client *client = nullptr;

opcua_client::opcua_client(PluginOPCUA *plugin) : QObject(NULL){
    pPlugin = plugin;

    EndpointUrl = "opc.tcp://localhost:4840";
    AutoStart = false;
}
opcua_client::~opcua_client(){
    pPlugin = nullptr; // prevent using the plugin interface when we are closing the plugin
    Stop();
}

void opcua_client::Start(){
    QuickBrowse();
}
void opcua_client::Stop(){

}

QString opcua_client::Status(){
    return "";
}

// Retrieve the list of end points
QStringList opcua_client::ListEndpoints(){
    UA_Client *client = UA_Client_new(UA_ClientConfig_standard);
    QStringList endpoints;

    /* Listing endpoints */
    UA_EndpointDescription* endpointArray = NULL;
    size_t endpointArraySize = 0;
    UA_StatusCode retval = UA_Client_getEndpoints(client, "opc.tcp://localhost:4840", &endpointArraySize, &endpointArray);
    if(retval != UA_STATUSCODE_GOOD) {
        UA_Array_delete(endpointArray, endpointArraySize, &UA_TYPES[UA_TYPES_ENDPOINTDESCRIPTION]);
        UA_Client_delete(client);
        pPlugin->LogAdd(tr("Can't connect to end point"));
        return endpoints;
    }
    pPlugin->LogAdd(tr("Found %1 endpoints:").arg(endpointArraySize));
    for(size_t i=0;i<endpointArraySize;i++) {
        QString endpoint_i = QString::fromUtf8((const char*)endpointArray[i].endpointUrl.data, (int)endpointArray[i].endpointUrl.length);
        endpoints.append(endpoint_i);
        pPlugin->LogAdd(tr("Found Endpoint URL: ") + endpoint_i);
    }
    UA_Array_delete(endpointArray, endpointArraySize, &UA_TYPES[UA_TYPES_ENDPOINTDESCRIPTION]);

    UA_Client_disconnect(client);
    UA_Client_delete(client);
    return endpoints;
}

static UA_StatusCode callbackNodeIter(UA_NodeId childId, UA_Boolean isInverse, UA_NodeId referenceTypeId, void *h) {
    PluginOPCUA *plugin = (PluginOPCUA*)h;
    if(isInverse){
        return UA_STATUSCODE_GOOD;
    }

    // Retrieve the identifier
    QString str_identifier;
    if(childId.identifierType == UA_NODEIDTYPE_NUMERIC) {
        str_identifier = QString::number(childId.identifier.numeric);
    } else if (childId.identifierType == UA_NODEIDTYPE_STRING){
        str_identifier = QString::fromUtf8((const char*)childId.identifier.string.data, childId.identifier.string.length);
    } else {
        str_identifier = "Uknown";
    }

    // Read the attribute and the display name
    UA_LocalizedText nodeDisplayName = UA_LOCALIZEDTEXT("en_US","name to read");
    UA_Variant *nodeValue = UA_Variant_new();
    UA_StatusCode retval = UA_Client_readValueAttribute(client, childId, nodeValue);
    UA_StatusCode retval2 = UA_Client_readDisplayNameAttribute(client, childId, &nodeDisplayName);
    if(retval == UA_STATUSCODE_GOOD && retval2 == UA_STATUSCODE_GOOD){
        QString strvalue;
        if (nodeValue->type->typeId.identifier.numeric == UA_TYPES[UA_TYPES_BOOLEAN].typeId.identifier.numeric) {
            UA_Boolean value = *((UA_Boolean*)nodeValue->data);
            strvalue = value ? "1" : "0";
        } else if (nodeValue->type->typeId.identifier.numeric == UA_TYPES[UA_TYPES_DOUBLE].typeId.identifier.numeric) {
            UA_Double value = *((UA_Double*)nodeValue->data);
            strvalue = QString::number(value);
        } else if (nodeValue->type->typeId.identifier.numeric == UA_TYPES[UA_TYPES_INT64].typeId.identifier.numeric) {
            UA_Int64 value = *((UA_Int64*)nodeValue->data);
            strvalue = QString::number(value);
        } else if (nodeValue->type->typeId.identifier.numeric == UA_TYPES[UA_TYPES_INT32].typeId.identifier.numeric) {
            UA_Int32 value = *((UA_Int32*)nodeValue->data);
            strvalue = QString::number(value);
        } else if (nodeValue->type->typeId.identifier.numeric == UA_TYPES[UA_TYPES_INT16].typeId.identifier.numeric) {
            UA_Int16 value = *((UA_Int16*)nodeValue->data);
            strvalue = QString::number(value);
        } else if (nodeValue->type->typeId.identifier.numeric == UA_TYPES[UA_TYPES_STRING].typeId.identifier.numeric) {
            UA_String *value = (UA_String*) nodeValue->data;
            strvalue = QString::fromUtf8((const char*)value->data, value->length);
        } else if (nodeValue->type->typeId.identifier.numeric == UA_TYPES[UA_TYPES_DATETIME].typeId.identifier.numeric) {
            UA_DateTime *value = (UA_DateTime*) nodeValue->data;
            UA_String strval = UA_DateTime_toString(*value);
            //QString str(name->data, name->length);
            strvalue = QString::fromUtf8((const char*)strval.data, strval.length);
        } else {
            strvalue = QObject::tr("Unknown value type %1").arg(nodeValue->type->typeId.identifier.numeric);
        }
        QString displayname = QString::fromUtf8((const char*)nodeDisplayName.text.data, nodeDisplayName.text.length);
        plugin->LogAdd(QString("  %1 (%2): %3").arg(displayname).arg(str_identifier).arg(strvalue));

        QString stationparam(displayname);
        if (stationparam.isEmpty()){
            stationparam = str_identifier;
        }
        if (!str_identifier.isEmpty()){
            plugin->RDK->setParam(displayname, strvalue);
        }
    } else {
        plugin->LogAdd(QObject::tr("  node %1 is not a variable").arg(str_identifier));
    }
    UA_Variant_delete(nodeValue);

    //UA_NodeId *parent = (UA_NodeId *)handle;
    //printf("%d, %d --- %d ---> NodeId %d, %d\n", parent->namespaceIndex, parent->identifier.numeric,
    // referenceTypeId.identifier.numeric, childId.namespaceIndex, childId.identifier.numeric);
    return UA_STATUSCODE_GOOD;
}

int opcua_client::QuickBrowse(){
    client = UA_Client_new(UA_ClientConfig_standard);
    UA_StatusCode retval;

    // Connect to a server
    // anonymous connect would be: retval = UA_Client_connect(client, "opc.tcp://localhost:4840");
    // retval = UA_Client_connect_username(client, "opc.tcp://localhost:4840", "user1", "password");
    pPlugin->LogAdd(tr("Connecting to OPC-UA server %1").arg(EndpointUrl));
    retval = UA_Client_connect(client, EndpointUrl.toUtf8().constData());
    if(retval != UA_STATUSCODE_GOOD) {
        UA_Client_delete(client);
        return (int)retval;
    }

    // Browse objects using the node iterator
    //UA_NodeId *parent = UA_NodeId_new();
    //*parent = UA_NODEID_NUMERIC(0, UA_NS0ID_OBJECTSFOLDER);
    UA_Client_forEachChildNodeCall(client, UA_NODEID_NUMERIC(0, UA_NS0ID_OBJECTSFOLDER), callbackNodeIter, (void *) pPlugin);

    pPlugin->RDK->ShowMessage(tr("Server variables retrieved. Right click the station item and select 'Station parameters' to see the variables"), false);
    // Disconnect from server and free memory
    UA_Client_disconnect(client);
    UA_Client_delete(client);
    client = nullptr;
    return 0;
}



