# This file builds all plugins from the public repository RoboDK/Plug-In-Interface

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
SUBDIRS += PluginRoboUI/PluginRoboUI.pro
}
SUBDIRS += PluginRealTime/PluginRealTime.pro
SUBDIRS += PluginRobotPilot/PluginRobotPilot.pro
SUBDIRS += PluginCollisionSensor/PluginCollisionSensor.pro
SUBDIRS += PluginEmbedding/PluginEmbedding.pro
