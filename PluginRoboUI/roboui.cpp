#include "roboui.h"

#include <QMainWindow>
#include <QMenuBar>
#include <QMenu>
#include <QBuffer>
#include <QMouseEvent>
#include <QKeyEvent>
#include <QtOpenGL/QtOpenGL>

#include <imgui_impl_opengl2.h>


static ImGuiKey qtKeyToImGuiKey(const QKeyEvent* keyEvent)
{
    bool keypad = keyEvent->modifiers().testFlag(Qt::KeypadModifier);

    switch (keyEvent->key())
    {
    case Qt::Key_Tab: return ImGuiKey_Tab;
    case Qt::Key_Left: return ImGuiKey_LeftArrow;
    case Qt::Key_Right: return ImGuiKey_RightArrow;
    case Qt::Key_Up: return ImGuiKey_UpArrow;
    case Qt::Key_Down: return ImGuiKey_DownArrow;
    case Qt::Key_PageUp: return ImGuiKey_PageUp;
    case Qt::Key_PageDown: return ImGuiKey_PageDown;
    case Qt::Key_Home: return ImGuiKey_Home;
    case Qt::Key_End: return ImGuiKey_End;
    case Qt::Key_Insert: return ImGuiKey_Insert;
    case Qt::Key_Delete: return ImGuiKey_Delete;
    case Qt::Key_Backspace: return ImGuiKey_Backspace;
    case Qt::Key_Space: return ImGuiKey_Space;
    case Qt::Key_Return: return keypad ? ImGuiKey_KeypadEnter : ImGuiKey_Enter;
    case Qt::Key_Escape: return ImGuiKey_Escape;
    case Qt::Key_Apostrophe: return ImGuiKey_Apostrophe;
    case Qt::Key_Comma: return ImGuiKey_Comma;
    case Qt::Key_Minus: return keypad ? ImGuiKey_KeypadSubtract : ImGuiKey_Minus;
    case Qt::Key_Period: return ImGuiKey_Period;
    case Qt::Key_Slash: return keypad ? ImGuiKey_KeypadDivide : ImGuiKey_Slash;
    case Qt::Key_Semicolon: return ImGuiKey_Semicolon;
    case Qt::Key_Equal: return ImGuiKey_Equal;
    case Qt::Key_BracketLeft: return ImGuiKey_LeftBracket;
    case Qt::Key_Backslash: return ImGuiKey_Backslash;
    case Qt::Key_BracketRight: return ImGuiKey_RightBracket;
    case Qt::Key_Agrave: return ImGuiKey_GraveAccent;
    case Qt::Key_CapsLock: return ImGuiKey_CapsLock;
    case Qt::Key_ScrollLock: return ImGuiKey_ScrollLock;
    case Qt::Key_NumLock: return ImGuiKey_NumLock;
    case Qt::Key_Print: return ImGuiKey_PrintScreen;
    case Qt::Key_Pause: return ImGuiKey_Pause;
    case Qt::Key_0: return keypad ? ImGuiKey_Keypad0 : ImGuiKey_0;
    case Qt::Key_1: return keypad ? ImGuiKey_Keypad1 : ImGuiKey_1;
    case Qt::Key_2: return keypad ? ImGuiKey_Keypad2 : ImGuiKey_2;
    case Qt::Key_3: return keypad ? ImGuiKey_Keypad3 : ImGuiKey_3;
    case Qt::Key_4: return keypad ? ImGuiKey_Keypad4 : ImGuiKey_4;
    case Qt::Key_5: return keypad ? ImGuiKey_Keypad5 : ImGuiKey_5;
    case Qt::Key_6: return keypad ? ImGuiKey_Keypad6 : ImGuiKey_6;
    case Qt::Key_7: return keypad ? ImGuiKey_Keypad7 : ImGuiKey_7;
    case Qt::Key_8: return keypad ? ImGuiKey_Keypad8 : ImGuiKey_8;
    case Qt::Key_9: return keypad ? ImGuiKey_Keypad9 : ImGuiKey_9;
    case Qt::Key_Asterisk: return keypad ? ImGuiKey_KeypadMultiply : ImGuiKey_None;
    case Qt::Key_Plus: return keypad ? ImGuiKey_KeypadAdd : ImGuiKey_None;
    case Qt::Key_Shift: return ImGuiKey_LeftShift;
    case Qt::Key_Control: return ImGuiKey_LeftCtrl;
    case Qt::Key_Menu: return ImGuiKey_LeftAlt;
    case Qt::Key_Meta: return ImGuiKey_LeftSuper;
    case Qt::Key_A: return ImGuiKey_A;
    case Qt::Key_B: return ImGuiKey_B;
    case Qt::Key_C: return ImGuiKey_C;
    case Qt::Key_D: return ImGuiKey_D;
    case Qt::Key_E: return ImGuiKey_E;
    case Qt::Key_F: return ImGuiKey_F;
    case Qt::Key_G: return ImGuiKey_G;
    case Qt::Key_H: return ImGuiKey_H;
    case Qt::Key_I: return ImGuiKey_I;
    case Qt::Key_J: return ImGuiKey_J;
    case Qt::Key_K: return ImGuiKey_K;
    case Qt::Key_L: return ImGuiKey_L;
    case Qt::Key_M: return ImGuiKey_M;
    case Qt::Key_N: return ImGuiKey_N;
    case Qt::Key_O: return ImGuiKey_O;
    case Qt::Key_P: return ImGuiKey_P;
    case Qt::Key_Q: return ImGuiKey_Q;
    case Qt::Key_R: return ImGuiKey_R;
    case Qt::Key_S: return ImGuiKey_S;
    case Qt::Key_T: return ImGuiKey_T;
    case Qt::Key_U: return ImGuiKey_U;
    case Qt::Key_V: return ImGuiKey_V;
    case Qt::Key_W: return ImGuiKey_W;
    case Qt::Key_X: return ImGuiKey_X;
    case Qt::Key_Y: return ImGuiKey_Y;
    case Qt::Key_Z: return ImGuiKey_Z;
    case Qt::Key_F1: return ImGuiKey_F1;
    case Qt::Key_F2: return ImGuiKey_F2;
    case Qt::Key_F3: return ImGuiKey_F3;
    case Qt::Key_F4: return ImGuiKey_F4;
    case Qt::Key_F5: return ImGuiKey_F5;
    case Qt::Key_F6: return ImGuiKey_F6;
    case Qt::Key_F7: return ImGuiKey_F7;
    case Qt::Key_F8: return ImGuiKey_F8;
    case Qt::Key_F9: return ImGuiKey_F9;
    case Qt::Key_F10: return ImGuiKey_F10;
    case Qt::Key_F11: return ImGuiKey_F11;
    case Qt::Key_F12: return ImGuiKey_F12;
    default: return ImGuiKey_None;
    }
}


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

    _mainWindow->installEventFilter(this);
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
    ImGuiIO& io = ImGui::GetIO();
    if (object == _renderWindow && event->type() == QEvent::MouseMove)
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
    else if (object == _renderWindow &&
        (event->type() == QEvent::MouseButtonPress ||
        event->type() == QEvent::MouseButtonRelease))
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
    else if (object == _mainWindow &&
        (event->type() == QEvent::KeyPress ||
        event->type() == QEvent::KeyRelease))
    {
        QKeyEvent* keyEvent = static_cast<QKeyEvent*>(event);

        bool down = event->type() == QEvent::KeyPress;

        const QString text = keyEvent->text();
        bool hasText = down && !text.isEmpty();
        if (hasText)
        {
            for (int i = 0; i < text.size(); ++i)
                io.AddInputCharacterUTF16(text[i].unicode());
        }

        // Update Key Modifiers
        Qt::KeyboardModifiers modifiers = keyEvent->modifiers();
        io.AddKeyEvent(ImGuiMod_Ctrl, modifiers.testFlag(Qt::ControlModifier));
        io.AddKeyEvent(ImGuiMod_Shift, modifiers.testFlag(Qt::ShiftModifier));
        io.AddKeyEvent(ImGuiMod_Alt, modifiers.testFlag(Qt::AltModifier));
        io.AddKeyEvent(ImGuiMod_Super, modifiers.testFlag(Qt::MetaModifier));

        ImGuiKey key = qtKeyToImGuiKey(keyEvent);
        io.AddKeyEvent(key, down);
        io.SetKeyEventNativeData(key, keyEvent->nativeVirtualKey(), keyEvent->nativeScanCode());

        _rdk->Render(IRoboDK::RenderScreen);
        return true;
    }
    return false;
}
