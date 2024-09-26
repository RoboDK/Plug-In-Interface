#ifndef PLUGINFORM_H
#define PLUGINFORM_H


#include "ui_pluginform.h"


class QMainWindow;
class IRoboDK;


class PluginForm : public QWidget, private Ui::PluginForm
{
    Q_OBJECT

public:
    explicit PluginForm(QMainWindow* mainWindow, IRoboDK* rdk, QWidget* parent = nullptr);

protected:
    void changeEvent(QEvent* event);

private:
    QMainWindow* _mainWindow;
    IRoboDK* _rdk;
};


#endif // PLUGINFORM_H
