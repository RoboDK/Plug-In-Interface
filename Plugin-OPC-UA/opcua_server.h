#ifndef OPCUA_SERVER_H
#define OPCUA_SERVER_H

#include <QObject>

class PluginOPCUA;

/// This class creates an instance of an OPC-UA server to interface with RoboDK
class opcua_server : public QObject
{
    Q_OBJECT

public:
    explicit opcua_server(PluginOPCUA *plugin);
    ~opcua_server();

public:
    /// Start the OPC-UA Server
    void Start();

    /// Stop the OPC-UA Server
    void Stop();

    /// Returns true if the server is stopped. If the server is shutting down it will return false
    bool IsStopped();

    /// Retrieve the status of the OPC-UA server
    QString Status();

public slots:

    /// Update status action
    void CheckStatus();

public:
    /// OPC-UA server port
    unsigned short Port;

    /// Start the OPC-UA server on startup
    bool AutoStart;

public:

    /// Pointer to the RoboDK plugin interface
    PluginOPCUA *pPlugin;

};

#endif // OPCUA_SERVER_H
