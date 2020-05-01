#ifndef OPCUA_CLIENT_H
#define OPCUA_CLIENT_H

#include <QObject>
#include <QTimer>

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

    /// Show the list of OPC-UA end points
    QStringList ListEndpoints();

public slots:
    /// Use the OPC-UA client to connect to the server and retrieve the server variables as RoboDK station variables
    int Browse(bool close_connection = false);

public:
    /// End Point URL: It contains the IP and port (for example: "opc.tcp://localhost:4840")
    QString EndpointUrl;

    /// Start the OPC-UA client on startup
    bool AutoStart;
    bool KeepConnected;

    /// Timer to update variables from the server
    QTimer BrowseServer;

public:

    /// Pointer to the RoboDK plugin interface
    PluginOPCUA *pPlugin;

};

#endif // OPCUA_CLIENT_H
