#include "pluginform.h"

#include <QMainWindow>
#include <QMenuBar>
#include <QStatusBar>
#include <QToolBar>
#include <QCloseEvent>


PluginForm::PluginForm(QMainWindow* mainWindow, IRoboDK* rdk, QWidget* parent)
    : QWidget(parent)
    , _mainWindow(mainWindow)
    , _rdk(rdk)
{
    setupUi(this);
    setWindowFlag(Qt::WindowStaysOnTopHint);

    auto paletteLabel = _labelDetached->palette();
    auto brushBase = paletteLabel.window();
    auto brushText = paletteLabel.windowText();
    paletteLabel.setBrush(QPalette::Window, brushText);
    paletteLabel.setBrush(QPalette::WindowText, brushBase);
    _labelDetached->setPalette(paletteLabel);

    auto fontLabel = _labelDetached->font();
    fontLabel.setBold(true);
    if (fontLabel.pointSizeF() > 0.0)
    {
        fontLabel.setPointSizeF(fontLabel.pointSizeF() * 2.0);
    }
    else if (fontLabel.pixelSize() > 0)
    {
        fontLabel.setPixelSize(fontLabel.pixelSize() * 2);
    }
    _labelDetached->setFont(fontLabel);

    connect(_buttonAttach, &QAbstractButton::clicked, this, &PluginForm::attachRoboDK);
    connect(_buttonDetach, &QAbstractButton::clicked, this, &PluginForm::detachRoboDK);
    connect(_buttonMinimize, &QAbstractButton::clicked, this, &PluginForm::minimizeRoboDK);
    connect(_buttonMaximize, &QAbstractButton::clicked, this, &PluginForm::maximizeRoboDK);
    connect(_buttonRestore, &QAbstractButton::clicked, this, &PluginForm::restoreRoboDK);
    connect(_buttonHideMenu, &QAbstractButton::clicked, this, &PluginForm::hideRoboDKMenu);
    connect(_buttonShowMenu, &QAbstractButton::clicked, this, &PluginForm::showRoboDKMenu);
    connect(_buttonHideToolBar, &QAbstractButton::clicked, this, &PluginForm::hideRoboDKToolBar);
    connect(_buttonShowToolBar, &QAbstractButton::clicked, this, &PluginForm::showRoboDKToolBar);
    connect(_buttonHideStatusBar, &QAbstractButton::clicked, this, &PluginForm::hideRoboDKStatusBar);
    connect(_buttonShowStatusBar, &QAbstractButton::clicked, this, &PluginForm::showRoboDKStatusBar);
}

bool PluginForm::isAttached() const
{
    return (_mainWindow && _mainWindow->parentWidget() == _groupEmbedded);
}

void PluginForm::attachRoboDK()
{
    if (!_mainWindow || _mainWindow->parentWidget())
        return;

    auto state = _mainWindow->windowState();
    if (state.testFlag(Qt::WindowMinimized))
    {
        state.setFlag(Qt::WindowMinimized, false);
        _mainWindow->setWindowState(state);
    }

    _savedGeometry = _mainWindow->saveGeometry();
    _savedState = _mainWindow->saveState();

    _labelDetached->hide();
    _mainWindow->setParent(_groupEmbedded);
    _layoutEmbedded->addWidget(_mainWindow);
    _mainWindow->show();

    emit attachmentChanged(true);
}

void PluginForm::detachRoboDK()
{
    if (!_mainWindow || _mainWindow->parentWidget() != _groupEmbedded)
        return;

    _layoutEmbedded->removeWidget(_mainWindow);
    _mainWindow->setParent(nullptr);

    _mainWindow->restoreGeometry(_savedGeometry);
    _mainWindow->restoreState(_savedState);

    _mainWindow->show();
    _labelDetached->show();

    emit attachmentChanged(false);
}

void PluginForm::minimizeRoboDK()
{
    if (!_mainWindow)
        return;

    _mainWindow->showMinimized();
    activateWindow();
}

void PluginForm::maximizeRoboDK()
{
    if (!_mainWindow)
        return;

    _mainWindow->showMaximized();
    activateWindow();
}

void PluginForm::restoreRoboDK()
{
    if (!_mainWindow)
        return;

    auto state = _mainWindow->windowState();
    state.setFlag(Qt::WindowMinimized, false);
    state.setFlag(Qt::WindowMaximized, false);
    _mainWindow->setWindowState(state);
    _mainWindow->show();
    activateWindow();
}

void PluginForm::hideRoboDKMenu()
{
    if (!_mainWindow || !_mainWindow->menuBar())
        return;

    _mainWindow->menuBar()->hide();
}

void PluginForm::showRoboDKMenu()
{
    if (!_mainWindow || !_mainWindow->menuBar())
        return;

    _mainWindow->menuBar()->show();
}

void PluginForm::hideRoboDKToolBar()
{
    if (!_mainWindow)
        return;

    for (const auto& toolBar : _mainWindow->findChildren<QToolBar*>())
    {
        if (toolBar->isVisible())
        {
            toolBar->setProperty("hidden_by_plugin", true);
            toolBar->setHidden(true);
        }
    }
}

void PluginForm::showRoboDKToolBar()
{
    if (!_mainWindow)
        return;

    for (const auto& toolBar : _mainWindow->findChildren<QToolBar*>())
    {
        if (toolBar->isHidden() && toolBar->property("hidden_by_plugin").toBool())
            toolBar->setVisible(true);
    }
}

void PluginForm::hideRoboDKStatusBar()
{
    if (!_mainWindow || !_mainWindow->statusBar())
        return;

    _mainWindow->statusBar()->hide();
}

void PluginForm::showRoboDKStatusBar()
{
    if (!_mainWindow || !_mainWindow->statusBar())
        return;

    _mainWindow->statusBar()->show();
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

void PluginForm::showEvent(QShowEvent*)
{
    emit visibilityChanged(true);
}

void PluginForm::closeEvent(QCloseEvent*)
{
    detachRoboDK();
    showRoboDKMenu();
    showRoboDKToolBar();
    showRoboDKStatusBar();
    emit visibilityChanged(false);
}
