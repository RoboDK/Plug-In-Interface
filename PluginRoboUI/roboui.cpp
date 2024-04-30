#include "roboui.h"

#include <QMainWindow>
#include <QMenuBar>
#include <QMenu>
#include <QBuffer>
#include <QMouseEvent>
#include <QtOpenGL/QtOpenGL>

#include <imgui_impl_opengl2.h>


RoboUI::RoboUI(QObject* parent)
    : QObject(parent)
    , _mainWindow(nullptr)
    , _menuBar(nullptr)
    , _statusBar(nullptr)
    , _rdk(nullptr)
    , _renderWindow(nullptr)
{
}

RoboUI::~RoboUI()
{
}

QString RoboUI::PluginName()
{
    return QStringLiteral("RoboUI");
}

QString RoboUI::PluginLoad(QMainWindow* mainWindow, QMenuBar* menuBar, QStatusBar* statusBar,
                                 IRoboDK* rdk, const QString& settings)
{
    Q_UNUSED(settings)

    _mainWindow = mainWindow;
    _menuBar = menuBar;
    _statusBar = statusBar;
    _rdk = rdk;

    auto ch = _mainWindow->children();
    for (auto c : ch) {
        qDebug() << c;
    }

    _renderWindow = _mainWindow->findChild<QWidget*>(QStringLiteral("MainGL"));
    if (_renderWindow)
    {
        _renderWindow->installEventFilter(this);
        _renderWindow->setMouseTracking(true);
    }

    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGui::StyleColorsDark();
    ImGui_ImplOpenGL2_Init();

    return QString();
}

void RoboUI::PluginUnload()
{
    ImGui_ImplOpenGL2_Shutdown();
    ImGui::DestroyContext();

    if (_renderWindow)
    {
        _renderWindow->removeEventFilter(this);
        _renderWindow = nullptr;
    }
}

void RoboUI::PluginLoadToolbar(QMainWindow* mainWindow, int iconSize)
{
    Q_UNUSED(mainWindow)
    Q_UNUSED(iconSize)
}

bool RoboUI::PluginItemClick(Item item, QMenu* menu, TypeClick clickType)
{
    Q_UNUSED(item)
    Q_UNUSED(menu)
    Q_UNUSED(clickType)
    return false;
}

QString RoboUI::PluginCommand(const QString& command, const QString& value)
{
    Q_UNUSED(command)
    Q_UNUSED(value)
    return QString();
}

void RoboUI::PluginEvent(TypeEvent eventType)
{
    switch (eventType)
    {
    case IAppRoboDK::EventRender:
    {
        ImGui_ImplOpenGL2_NewFrame();
        ImGuiIO& io = ImGui::GetIO();
        if (_renderWindow)
            io.DisplaySize = ImVec2(_renderWindow->width(), _renderWindow->height());
        ImGui::NewFrame();
        ImGui::ShowDemoWindow(nullptr);
        bool show_another_window = true;
        ImGui::Begin("Another Window", &show_another_window);   // Pass a pointer to our bool variable (the window will have a closing button that will clear the bool when clicked)
        ImGui::Text("Hello from another window!");
        if (ImGui::Button("Close Me"))
            show_another_window = false;
        ImGui::End();
        ImGui::Render();
        ImGui_ImplOpenGL2_RenderDrawData(ImGui::GetDrawData());
        break;
    }

    default:
        break;
    }
}

bool RoboUI::PluginItemClickMulti(QList<Item>& itemList, QMenu* menu, TypeClick clickType)
{
    Q_UNUSED(itemList)
    Q_UNUSED(menu)
    Q_UNUSED(clickType)
    return false;
}

bool RoboUI::eventFilter(QObject* object, QEvent* event)
{
    Q_UNUSED(object)

    ImGuiIO& io = ImGui::GetIO();
    if (event->type() == QEvent::MouseMove)
    {
        QMouseEvent *mouseEvent = static_cast<QMouseEvent *>(event);
        QPointF pos = mouseEvent->localPos();
        io.AddMousePosEvent(pos.x(), pos.y());
        _rdk->Render(IRoboDK::RenderScreen);
        //ImGui::UpdateInputEvents()
        if (io.WantCaptureMouse)
        {
            return true;
        }
    }
    else if (event->type() == QEvent::MouseButtonPress ||
             event->type() == QEvent::MouseButtonRelease)
    {
        QMouseEvent *mouseEvent = static_cast<QMouseEvent *>(event);
        QPointF pos = mouseEvent->localPos();
        io.AddMousePosEvent(pos.x(), pos.y());
        int button = -1;
        switch (mouseEvent->button())
        {
        case Qt::LeftButton:
            button = 0;
            break;
        case Qt::RightButton:
            button = 1;
            break;
        case Qt::MiddleButton:
            button = 2;
            break;
        default:
            break;
        }
        io.AddMouseButtonEvent(button, event->type() == QEvent::MouseButtonPress);
        _rdk->Render(IRoboDK::RenderScreen);
        if (io.WantCaptureMouse)
        {
            return true;
        }
    }
    return false;
}
