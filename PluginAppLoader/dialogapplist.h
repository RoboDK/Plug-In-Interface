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
    void on_btnOk_clicked();
    void onCellDoubleClicked( int a, int b);

    void on_btnStopAppActions_clicked();

private:
    AppLoader *pAppLoader;
    Ui::DialogAppList *ui;
};

#endif // FORMPLUGINMANAGER_H
