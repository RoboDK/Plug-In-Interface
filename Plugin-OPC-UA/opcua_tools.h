#ifndef OPCUA_TOOLS_H
#define OPCUA_TOOLS_H


#include <QString>
#include "robodktools.h"

#include "open62541.h"



/// Convert an OPC-UA Variant to an item pointer
bool Var_2_Item(const UA_Variant *var, IItem **item, RoboDK *rdk);

/// Convert an OPC-UA variant to an int
bool Var_2_Int(const UA_Variant *var, UA_Int64 *num);

/// Convert an OPC-UA variant to a double
bool Var_2_Double(const UA_Variant *var, UA_Double *value);

/// Convert an OPC-UA variant to a QString
bool Var_2_Str(const UA_Variant *var, QString &str);

/// Convert an OPC-UA variant to a double array
bool Var_2_DoubleArray(const UA_Variant *var, double *values, UA_UInt32 maxlen);


//-------------------------------------------------------------------------
/// Helper function to convert a pointer to an OPC-UA pointer

/// Convert a RoboDK item pointer to a OPC-UA variant
bool Item_2_Var(const UA_UInt64 item, UA_Variant *var);

/// Convert an int to a OPC-UA variant
bool Int_2_Var(const UA_Int64 num, UA_Variant *var);

/// Convert a double variable to a OPC-UA variant
bool Double_2_Var(const UA_Double value, UA_Variant *var);

/// Convert a double array to an OPC-UA variant
bool DoubleArray_2_Var(const double *values, unsigned long long numel, UA_Variant *var);

/// Convert a QString to a OPC-UA variant
bool Str_2_Var(const QString &str, UA_Variant *var);


#endif // OPCUA_TOOLS_H
