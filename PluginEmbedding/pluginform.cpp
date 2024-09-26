#include "pluginform.h"


PluginForm::PluginForm(QMainWindow* mainWindow, IRoboDK* rdk, QWidget* parent)
    : QWidget(parent)
    , _mainWindow(mainWindow)
    , _rdk(rdk)
{
    setupUi(this);
}

void PluginForm::changeEvent(QEvent* event)
{
    QWidget::changeEvent(event);

    switch (event->type())
    {
    case QEvent::LanguageChange:
        retranslateUi(this);
        break;

    default:
        break;
    }
}
