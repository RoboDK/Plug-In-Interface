PROJECT_ROOT = $${PWD}

QT += widgets network svg opengl

TEMPLATE = lib
CONFIG += plugin

TARGET = RoboUI

CONFIG += c++17

#DEFINES += QT_ASCII_CAST_WARNINGS QT_NO_CAST_FROM_ASCII

win32 {
    RC_FILE = roboui.rc
    LIBS += opengl32.lib
}

exists( "$$PWD/../../destdir_rdk_plugins.pri" ) {
    include("$$PWD/../../destdir_rdk_plugins.pri")
    DESTDIR = $$DESTDIR_RDK_PLUGINS
} else {
    CONFIG(release, debug|release) {
        message("Using release binaries.")
        message("Select Projects-Run-Executable and set to C:/RoboDK/bin/RoboDK.exe")
        win32 {
            #Default path on Windows
            DESTDIR  = C:/RoboDK/bin/plugins
        } else {
            macx {
                # Default path on MacOS
                DESTDIR  = ~/RoboDK/RoboDK.app/Contents/MacOS/plugins
            } else {
                #Default path on Linux
                DESTDIR  = ~/RoboDK/bin/plugins
            }
        }
    } else {
        message("Using debug binaries: Make sure you start the debug version of RoboDK ( C:/RoboDK/bind/ ). ")
        message("Select Projects-Run-Executable and set to C:/RoboDK/bind/RoboDK.exe ")
        message("(send us an email at info@robodk.com to obtain debug binaries that should go to the bind directory)")
        win32{
            #Default path on Windows (debug)
            DESTDIR  = C:/RoboDK/bind/plugins
        } else {
            macx {
                # Default path on MacOS (debug)
                DESTDIR  = ~/RoboDK-Dev/Deploy/RoboDK.app/Contents/MacOS/plugins
            } else {
                #Default path on Linux (debug)
                DESTDIR  = ~/RoboDK/bind/plugins
            }
        }
    }
}


INCLUDEPATH += \
    $${PROJECT_ROOT}/imgui \
    $${PROJECT_ROOT}/../robodk_interface

SOURCES += \
    imgui/imgui.cpp \
    imgui/imgui_demo.cpp \
    imgui/imgui_draw.cpp \
    imgui/imgui_impl_opengl2.cpp \
    imgui/imgui_tables.cpp \
    imgui/imgui_widgets.cpp \
    ../robodk_interface/robodktools.cpp \
    ../robodk_interface/robodktypes.cpp \
    roboui.cpp

HEADERS += \
    imgui/imconfig.h \
    imgui/imgui.h \
    imgui/imgui_impl_opengl2.h \
    imgui/imgui_internal.h \
    imgui/imstb_rectpack.h \
    imgui/imstb_textedit.h \
    imgui/imstb_truetype.h \
    ../robodk_interface/iapprobodk.h \
    ../robodk_interface/iitem.h \
    ../robodk_interface/irobodk.h \
    ../robodk_interface/robodk_interface.h \
    ../robodk_interface/robodktools.h \
    ../robodk_interface/robodktypes.h \
    roboui.h

RESOURCES += \
    roboui.qrc
