#include "dialogusernamepassword.h"
#include "ui_dialogusernamepassword.h"

dialogUsernamePassword::dialogUsernamePassword(QString username,QString password,QWidget *parent) :
    QDialog(parent),
    ui(new Ui::dialogUsernamePassword)
{
    ui->setupUi(this);
    ui->leUsername->setText(username);
    ui->lePassword->setText(password);
    connect(ui->btnClose, &QPushButton::pressed, this, [this]() {
        this->close();
    });
}

QString dialogUsernamePassword::getUsername() {
    return ui->leUsername->text();
}

QString dialogUsernamePassword::getPassword() {
    return ui->lePassword->text();
}

dialogUsernamePassword::~dialogUsernamePassword()
{
    delete ui;
}
