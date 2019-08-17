#include "robodktools.h"
#include <QDebug>


bool ItemValid(const Item item){
    return item != nullptr;
}



QDockWidget* AddDockWidget(QMainWindow *mw, QWidget *widget, const QString &strtitle, Qt::DockWidgetAreas allowed, Qt::DockWidgetArea add_where, bool closable, bool delete_on_close){
    QDockWidget *dockwidget = new QDockWidget(strtitle, mw);//"Robot properties view"
    dockwidget->setObjectName(strtitle); // added on 2018-08-24
    if (closable){
        dockwidget->setFeatures(QDockWidget::AllDockWidgetFeatures);//{ DockWidgetClosable, DockWidgetMovable, DockWidgetFloatable, DockWidgetVerticalTitleBar, AllDockWidgetFeatures, NoDockWidgetFeatures }
    } else {
        dockwidget->setFeatures(QDockWidget::DockWidgetMovable|QDockWidget::DockWidgetFloatable);
    }

    dockwidget->setWidget(widget);
    if (delete_on_close){
        dockwidget->setAttribute(Qt::WA_DeleteOnClose);
    }
    dockwidget->setAllowedAreas(allowed);
    qDebug() << "Adding new docked window: " << strtitle; //<< add_where;
    mw->addDockWidget(add_where, dockwidget);
    if (add_where == Qt::NoDockWidgetArea){
        dockwidget->setFloating(true);
        dockwidget->show();
    }
    dockwidget->setVisible(true);
    return dockwidget;
}

void string_2_doubles(const QString &str, double *values, int *size_inout, const QString &separator){
    bool isok;
    QString line;
    QString strnum;
    QRegExp rx(separator);
    line = str.trimmed();
    QStringList strfloats = line.split(rx,QString::SkipEmptyParts);
    *size_inout = qMin(strfloats.size(), *size_inout);
    int countok = 0;
    for (int i=0; i<strfloats.size(); i++){
        strnum = strfloats.at(i);
        strnum = strnum.trimmed();
        double aux = strnum.toDouble(&isok);
        if (isok){
            values[countok] = aux;
            countok = countok + 1;
        }
        if (countok >= *size_inout){
            *size_inout = countok;
            return;
        }
    }
    *size_inout = countok;
}

QString doubles_2_string(const double *array, int size, int precision, const QString &separator){
    QString txt;
    for (int i=0; i<size-1; i++){
        QString num_str = QString::number(array[i],'f',precision);
        txt.append(num_str);
        txt.append(separator);
    }
    QString num_str = QString::number(array[size-1],'f',precision);
    txt.append(num_str);
    return txt;
}


