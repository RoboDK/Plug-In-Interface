#ifndef PLUGINEMBEDDING_H
#define PLUGINEMBEDDING_H


#define APP_INTERNALNAME        "PLUGINEMBEDDING"
#define APP_FILENAME            APP_INTERNALNAME ".DLL"

#define APP_NAME                "RoboDK Plugin Embedding Example"

#define APP_VERSION_MAJOR       1
#define APP_VERSION_MINOR       0
#define APP_VERSION_PATCH       0

#ifdef BUILD_NUMBER
#define APP_VERSION_BUILD       BUILD_NUMBER
#else
#define APP_VERSION_BUILD       0
#endif // BUILD_NUMBER

#define APP_COMPANY             "RoboDK Inc."
#define APP_COPYRIGHT           "Copyright (c) 2024, RoboDK Inc."
#define APP_DOMAIN              "robodk.com"

#define APP_STR_HELPER(x)       #x
#define APP_STR(x)              APP_STR_HELPER(x)

#define APP_VERSION_STRING      APP_STR(APP_VERSION_MAJOR) "." \
                                APP_STR(APP_VERSION_MINOR) "." \
                                APP_STR(APP_VERSION_PATCH) "." \
                                APP_STR(APP_VERSION_BUILD)


#ifndef RC_INVOKED

#include <iapprobodk.h>

#include <QObjectCleanupHandler>
#include <QPointer>


class PluginForm;


class PluginEmbedding : public QObject, public IAppRoboDK
{
    Q_OBJECT
    Q_PLUGIN_METADATA(IID "RoboDK.IAppRoboDK")
    Q_INTERFACES(IAppRoboDK)

public:
    explicit PluginEmbedding(QObject* parent = nullptr);
    virtual ~PluginEmbedding();

    QString PluginName() override;
    QString PluginLoad(QMainWindow* mainWindow, QMenuBar* menuBar, QStatusBar* statusBar,
        IRoboDK* rdk, const QString& settings = "") override;
    void PluginUnload() override;

private:
    void createMenu();

private:
    QObjectCleanupHandler _objectCleaner;

    QMainWindow* _mainWindow;
    QMenuBar* _menuBar;
    QStatusBar* _statusBar;
    IRoboDK* _rdk;

    QPointer<PluginForm> _form;
};

#endif // RC_INVOKED


#endif // PLUGINEMBEDDING_H
