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

    /// App double clicked
    void onCellDoubleClicked( int a, int b);

    /// Stop actions started by apps
    void on_btnStopAppActions_clicked();

    /// Scan for app changes and reload all
    void on_btnReload_clicked();

private:
    AppLoader *pAppLoader;
    Ui::DialogAppList *ui;
};

#endif // FORMPLUGINMANAGER_H
