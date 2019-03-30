#ifndef ROBODKTOOLS_H
#define ROBODKTOOLS_H

#include <QTreeWidgetItem>
#include <QString>
#include <QMainWindow>
#include <QDockWidget>

#include "robodktypes.h"

/// \brief Check if an item is valid. Contrary to the default RoboDK API where we have a Item.Valid() function, we can just check if the item is valid by checking if the item is a null pointer.
/// We can also use class: IRoboDK::Valid to check if an item has been deleted.
/// It is recommended to use the plugin event callback class: IAppRoboDK::PluginEvent to check if the item still exists. If not, force the Item pointer to be nullptr.
bool ItemValid(const Item item);

/// \brief Add a Widget to the Main Window as a Docked Widget. Docked widgets can be moved and "docked" inside the main window of RoboDK.
QDockWidget* AddDockWidget(QMainWindow *mw, QWidget *widget, const QString &strtitle, Qt::DockWidgetAreas allowed = Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea, Qt::DockWidgetArea add_where = Qt::LeftDockWidgetArea, bool closable = true, bool delete_on_close = true);

/// Convert a string given to a double array given the size of the array (in/out) and the value separator
void string_2_doubles(const QString &str, double *values, int *size_inout, const QString &separator=",");

/// Convert a double array to a string given the size of the array, the number of decimals and the value separator
QString doubles_2_string(const double *values, int size, int precision=3, const QString &separator=",");


#endif // ROBODKTOOLS_H
