# This file builds all plugins from the public repository RoboDK/Plug-In-Interface

linux{
#QMAKE_CXXFLAGS_WARN_OFF -= -Wunused-parameter
QMAKE_CXXFLAGS+=-Wno-unused-parameter
QMAKE_CXXFLAGS+=-Wno-unused-variable
QMAKE_CXXFLAGS+=-Wno-comment
}

# CONFIG += ordered

TEMPLATE = subdirs

SUBDIRS += PluginAppLoader/AppLoader.pro
SUBDIRS += PluginAttachObject/PluginAttachObject.pro
SUBDIRS += PluginAttachView/PluginAttachView.pro
SUBDIRS += PluginBallbarTracker/PluginBallbarTracker.pro
SUBDIRS += PluginExample/PluginExample.pro
SUBDIRS += PluginLockTCP/PluginLockTCP.pro
SUBDIRS += PluginLVDT/PluginLVDT.pro
win32 {
SUBDIRS += Plugin-OPC-UA/PluginOPCUA.pro
SUBDIRS += PluginOpenGL/PluginOpengl.pro
SUBDIRS += PluginOpenGL-Shaders/PluginChip8Opengl.pro
SUBDIRS += PluginRoboUI/roboui.pro
}
SUBDIRS += PluginRealTime/PluginRealTime.pro
SUBDIRS += PluginRobotPilot/PluginRobotPilot.pro
SUBDIRS += PluginCollisionSensor/PluginCollisionSensor.pro
SUBDIRS += PluginEmbedding/PluginEmbedding.pro
