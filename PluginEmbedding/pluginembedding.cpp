#include "pluginembedding.h"

#include <QMainWindow>
#include <QMenuBar>
#include <QStatusBar>
#include <QMenu>

#include "pluginform.h"


PluginEmbedding::PluginEmbedding(QObject* parent)
    : QObject(parent)
    , _mainWindow(nullptr)
    , _menuBar(nullptr)
    , _statusBar(nullptr)
    , _rdk(nullptr)
{
}

PluginEmbedding::~PluginEmbedding()
{
}

QString PluginEmbedding::PluginName()
{
    return QLatin1String("Embedding Example");
}

QString PluginEmbedding::PluginLoad(QMainWindow* mainWindow, QMenuBar* menuBar,
    QStatusBar* statusBar, IRoboDK* rdk, const QString& settings)
{
    Q_UNUSED(settings)

    _mainWindow = mainWindow;
    _menuBar = menuBar;
    _statusBar = statusBar;
    _rdk = rdk;

    _form = new PluginForm(mainWindow, rdk);
    _objectCleaner.add(_form);

    createMenu();

    return QString();
}

void PluginEmbedding::PluginUnload()
{
    _objectCleaner.clear();
}

void PluginEmbedding::createMenu()
{
    if (!_form)
        return;

    auto menu = new QMenu(tr("Embedding"));
    if (!menu)
        return;

    _objectCleaner.add(menu);
    _menuBar->addMenu(menu);

    auto actionOpen = menu->addAction(tr("Open Control Panel"), _form.data(), &QWidget::show);
    menu->addAction(tr("Move to Control Panel"), [this]
    {
        if (!_form)
            return;

        _form->show();
        _form->attachRoboDK();
    });
    menu->addSeparator();
    auto actionClose = menu->addAction(tr("Close Control Panel"), _form.data(), &QWidget::close);

    if (actionOpen)
    {
        actionOpen->setDisabled(_form->isVisible());
        connect(_form.data(), &PluginForm::visibilityChanged, actionOpen, &QAction::setDisabled);
    }

    if (actionClose)
    {
        actionClose->setEnabled(_form->isVisible());
        connect(_form.data(), &PluginForm::visibilityChanged, actionClose, &QAction::setEnabled);
    }
}
