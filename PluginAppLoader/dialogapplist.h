#ifndef FORMPLUGINMANAGER_H
#define FORMPLUGINMANAGER_H

#include <QDialog>

class AppLoader;

namespace Ui {
class DialogAppList;
}

class DialogAppList : public QDialog
{

    Q_OBJECT

public:
    explicit DialogAppList(AppLoader *apploader, QWidget *parent = nullptr);
    ~DialogAppList();

    void UpdateForm();



private slots:
    /// OK button selected
    void on_btnOk_clicked();

    /// Stop actions started by apps
    void on_btnStopAppActions_clicked();

    /// Scan for app changes and reload all
    void on_btnReload_clicked();

    /// Enable/Disable application
    void onButtonActionClicked();

private:
    AppLoader *pAppLoader;
    Ui::DialogAppList *ui;
};

#endif // FORMPLUGINMANAGER_H
