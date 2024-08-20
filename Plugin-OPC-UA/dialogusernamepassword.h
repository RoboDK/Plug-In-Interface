#ifndef DIALOGUSERNAMEPASSWORD_H
#define DIALOGUSERNAMEPASSWORD_H

#include <QWidget>
#include <QDialog>

namespace Ui {
class dialogUsernamePassword;
}

class dialogUsernamePassword : public QDialog
{
    Q_OBJECT

public:
    explicit dialogUsernamePassword(QString username,QString password,QWidget *parent = nullptr);
    ~dialogUsernamePassword();

    QString getUsername();
    QString getPassword();
private:
    Ui::dialogUsernamePassword *ui;
};

#endif // DIALOGUSERNAMEPASSWORD_H
