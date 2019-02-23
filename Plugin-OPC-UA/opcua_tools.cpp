#include "opcua_tools.h"
#include "irobodk.h"

///////////////////////////////////////////////////////////////7
bool Var_2_Item(const UA_Variant *var, IItem **item, RoboDK *rdk){
    if (var->type->typeId.identifier.numeric != UA_TYPES[UA_TYPES_UINT64].typeId.identifier.numeric){
        qDebug()<<"Invalid item type: " << var->type;
        return false;
    }
    *item = (IItem*) ((UA_UInt64*)var->data)[0];
    if (!rdk->Valid(*item)){
        qDebug()<<"Item ID does not exist: " << *item;
        *item = nullptr;
        return false;
    }
    return true;
}
bool Var_2_Int(const UA_Variant *var, UA_Int64 *num){
    if (var->type->typeId.identifier.numeric != UA_TYPES[UA_TYPES_INT64].typeId.identifier.numeric){
        qDebug()<<"Invalid int type: " << var->type;
        return false;
    }
    *num = ((UA_Int64*)var->data)[0];
    return true;
}
bool Var_2_Double(const UA_Variant *var, UA_Double *value){
    if (var->type->typeId.identifier.numeric != UA_TYPES[UA_TYPES_DOUBLE].typeId.identifier.numeric){
        qDebug()<<"Invalid double type: " << var->type;
        return false;
    }
    *value = ((UA_Double*)var->data)[0];
    return true;
}
bool Var_2_Str(const UA_Variant *var, QString &str){
    if (var->type->typeId.identifier.numeric != UA_TYPES[UA_TYPES_STRING].typeId.identifier.numeric){
        qDebug()<<"Invalid string type: " << var->type;
        return false;
    }
    UA_String *name = (UA_String*) var->data;
    //QString str(name->data, name->length);
    str = QString::fromUtf8((const char*)name->data, name->length);
    qDebug() << "Received array: " << str;
    return true;
}
bool Var_2_DoubleArray(const UA_Variant *var, double *values, UA_UInt32 maxlen){
    if (var->type->typeId.identifier.numeric != UA_TYPES[UA_TYPES_DOUBLE].typeId.identifier.numeric){
        //qDebug()<<"Invalid array type or dimension: " << var->type;
        return false;
    }
    unsigned int size = qMin(maxlen, var->arrayDimensions[0]);
    for (unsigned int i=0; i<size; i++){
        values[i] = ((UA_Double*) var->data)[i];
    }
    //qDebug() << "Received number: " << str;
    return true;
}

//-------------------------------------------------------------------------
/// Helper function to convert a pointer to an OPC-UA pointer
bool Item_2_Var(const UA_UInt64 item, UA_Variant *var){
    UA_Variant_setScalarCopy(var, &item, &UA_TYPES[UA_TYPES_UINT64]);
    return true;
}
bool Int_2_Var(const UA_Int64 num, UA_Variant *var){
    UA_Variant_setScalarCopy(var, &num, &UA_TYPES[UA_TYPES_INT64]);
    return true;
}
bool Double_2_Var(const UA_Double value, UA_Variant *var){
    UA_Variant_setScalarCopy(var, &value, &UA_TYPES[UA_TYPES_DOUBLE]);
    return true;
}
bool DoubleArray_2_Var(const double *values, unsigned long long numel, UA_Variant *var){
    UA_Variant_setArrayCopy(var, values, numel, &UA_TYPES[UA_TYPES_DOUBLE]);
    return true;
}
bool Str_2_Var(const QString &str, UA_Variant *var){
    UA_String str_UA = UA_STRING((const char*)str.toUtf8().constData());
    UA_Variant_setScalarCopy(var, &str_UA, &UA_TYPES[UA_TYPES_STRING]);
    return true;
}
//-------------------------------------------------------------------------
