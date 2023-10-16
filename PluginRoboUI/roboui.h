#ifndef ADDINMANAGER_H
#define ADDINMANAGER_H


#define APP_NAME                "RoboDK RoboUI"
#define APP_INTERNALNAME        "ROBOUI"

#define APP_VERSION_MAJOR       1
#define APP_VERSION_MINOR       0
#define APP_VERSION_PATCH       9
#define APP_VERSION_BUILD       0

#define APP_COMPANY             "RoboDK Inc."
#define APP_COPYRIGHT           "Copyright (c) 2023, RoboDK Inc."
#define APP_DOMAIN              "robodk.com"
#define APP_FILENAME            APP_INTERNALNAME ".DLL"

#define APP_STR_HELPER(x)       #x
#define APP_STR(x)              APP_STR_HELPER(x)

#define APP_VERSION_STRING      APP_STR(APP_VERSION_MAJOR) "." \
                                APP_STR(APP_VERSION_MINOR) "." \
                                APP_STR(APP_VERSION_PATCH) "." \
                                APP_STR(APP_VERSION_BUILD)


#ifndef RC_INVOKED

#include <QObject>
#include <QtPlugin>

#include "iapprobodk.h"


class RoboUI : public QObject, public IAppRoboDK
{
    Q_OBJECT
    Q_PLUGIN_METADATA(IID "RoboDK.IAppRoboDK")
    Q_INTERFACES(IAppRoboDK)

public:
    explicit RoboUI(QObject* parent = nullptr);
    virtual ~RoboUI();

    virtual QString PluginName();
    virtual QString PluginLoad(QMainWindow* mainWindow, QMenuBar* menuBar, QStatusBar* statusBar,
                               IRoboDK* rdk, const QString& settings = "");
    virtual void PluginUnload();
    virtual void PluginLoadToolbar(QMainWindow* mainWindow, int iconSize);
    virtual bool PluginItemClick(Item item, QMenu* menu, TypeClick clickType);
    virtual QString PluginCommand(const QString& command, const QString& value);
    virtual void PluginEvent(TypeEvent eventType);
    virtual bool PluginItemClickMulti(QList<Item>& itemList, QMenu* menu, TypeClick clickType);

    virtual bool eventFilter(QObject* object, QEvent* event);

private:
    QMainWindow* _mainWindow;
    QMenuBar* _menuBar;
    QStatusBar* _statusBar;
    IRoboDK* _rdk;
    QWidget* _renderWindow;
};

#endif // RC_INVOKED


#endif // ADDINMANAGER_H
