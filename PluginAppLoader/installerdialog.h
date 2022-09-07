#ifndef INSTALLERDIALOG_H
#define INSTALLERDIALOG_H


#include <QDialog>
#include <QVersionNumber>
#include <QList>


class AppLoader;

namespace Ui {
class InstallerDialog;
}


struct ApplicationRecord
{
    QString name;
    QString path;
    QVersionNumber installedVersion;
    QVersionNumber proposedVersion;
    bool global;

    void clear(){
        name.clear();
        path.clear();
        installedVersion = QVersionNumber();
        proposedVersion = QVersionNumber();
        global = false;
    }
};


class InstallerDialog : public QDialog
{
    Q_OBJECT

public:
    explicit InstallerDialog(AppLoader *apploader, QWidget* parent = nullptr);
    ~InstallerDialog();

    bool processPackage(const QString& package);

private:
    Ui::InstallerDialog* ui;
    AppLoader* pAppLoader;
    QList<ApplicationRecord> records;
};

#endif // INSTALLERDIALOG_H
