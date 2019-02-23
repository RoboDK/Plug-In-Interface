#ifndef OPCUA_CLIENT_H
#define OPCUA_CLIENT_H

#include <QObject>

class PluginOPCUA;

class opcua_client : public QObject
{
    Q_OBJECT

public:
    explicit opcua_client(PluginOPCUA *plugin);
    ~opcua_client();

public:
    /// Start the OPC-UA Client
    void Start();

    /// Stop the OPC-UA Client
    void Stop();

    /// Retrieve the status of the OPC-UA server
    QString Status();

    /// Use the OPC-UA client to connect to the server and retrieve the server variables as RoboDK station variables
    int QuickBrowse();

    QStringList ListEndpoints();

public:
    /// End Point URL: It contains the IP and port (for example: "opc.tcp://localhost:4840")
    QString EndpointUrl;

    /// Start the OPC-UA server on startup
    int AutoStart;

public:

    /// Pointer to the RoboDK plugin interface
    PluginOPCUA *pPlugin;

};

#endif // OPCUA_CLIENT_H
