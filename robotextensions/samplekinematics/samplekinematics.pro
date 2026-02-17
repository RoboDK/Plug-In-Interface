#--------------------------------
# This is a sample project that shows how to customize the robot kinematics in RoboDK by creating a custom DLL
# To load your custom DLL: Double click on your robot, select Parameters, click on Options under Robot Kinematics, click on Select Library.
# This is supported since RoboDK v6
#--------------------------------

CONFIG -= qt
QT -= core
QT -= gui

TEMPLATE = lib
CONFIG += c++17

# --------------------------
# Default rules for deployment and debugging
## Windows default:
CONFIG(release, debug|release) {
DESTDIR_ROBOTEXTENSIONS = "C:/RoboDK/bin/robotextensions"
} else {
DESTDIR_ROBOTEXTENSIONS = "C:/RoboDK/bind/robotextensions"
}
## Mac default:
macx {
CONFIG -= app_bundle
DESTDIR_ROBOTEXTENSIONS = "~/RoboDK/RoboDK.app/Contents/MacOS/robotextensions"
}
## Linux default:
linux {
DESTDIR_ROBOTEXTENSIONS = "~/RoboDK/bin/robotextensions"
}

message("Placing kinematics DLL in the folder:")
message($$DESTDIR_ROBOTEXTENSIONS)

# target.path = /usr/lib
# INSTALLS += target
DESTDIR = $$DESTDIR_ROBOTEXTENSIONS
# --------------------------





# -----------------------------------
# Required files:
SOURCES += \
    samplekinematics.cpp

HEADERS += \
    samplekinematics.h

