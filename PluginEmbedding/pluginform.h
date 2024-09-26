#ifndef PLUGINFORM_H
#define PLUGINFORM_H


#include "ui_pluginform.h"

#include <QByteArray>


class QMainWindow;
class IRoboDK;


class PluginForm : public QWidget, private Ui::PluginForm
{
    Q_OBJECT

public:
    explicit PluginForm(QMainWindow* mainWindow, IRoboDK* rdk, QWidget* parent = nullptr);

public slots:
    void attachRoboDK();
    void detachRoboDK();
    void minimizeRoboDK();
    void maximizeRoboDK();
    void restoreRoboDK();
    void hideRoboDKMenu();
    void showRoboDKMenu();
    void hideRoboDKToolBar();
    void showRoboDKToolBar();
    void hideRoboDKStatusBar();
    void showRoboDKStatusBar();

signals:
    void visibilityChanged(bool visible);

protected:
    void changeEvent(QEvent* event) override;
    void showEvent(QShowEvent*) override;
    void closeEvent(QCloseEvent*) override;

private:
    QMainWindow* _mainWindow;
    IRoboDK* _rdk;

    QByteArray _savedGeometry;
    QByteArray _savedState;
};


#endif // PLUGINFORM_H
