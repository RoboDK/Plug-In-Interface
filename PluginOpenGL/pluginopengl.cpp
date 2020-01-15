#include "pluginopengl.h".h"
#include "robodktools.h"
#include "irobodk.h"
#include "iitem.h"


#include <QMainWindow>
#include <QToolBar>
#include <QDebug>
#include <QAction>
#include <QStatusBar>
#include <QMenuBar>
#include <QTextEdit>
#include <QDateTime>
#include <QIcon>
#include <QDesktopServices>
#include <QElapsedTimer>

#include <QtOpenGL/QtOpenGL>

//------------------------------- RoboDK Plug-in commands ------------------------------


QString PluginExample::PluginName(){
    return "OpenGL Plugin";
}


QString PluginExample::PluginLoad(QMainWindow *mw, QMenuBar *menubar, QStatusBar *statusbar, RoboDK *rdk, const QString &settings){
    RDK = rdk;
    MainWindow = mw;
    StatusBar = statusbar;
    qDebug() << "Loading plugin " << PluginName();
    qDebug() << "Using settings: " << settings; // reserved for future compatibility

    // it is highly recommended to use the statusbar for debugging purposes (pass /DEBUG as an argument to see debug result in RoboDK)
    qDebug() << "Setting up the status bar";
    StatusBar->showMessage(tr("RoboDK Plugin %1 is being loaded").arg(PluginName()));

    // Here you can add all the "Actions": these actions are callbacks from buttons selected from the menu or the toolbar
    action_display = new QAction(tr("Display"));
    action_display->setCheckable(true);

    timer_Update.setInterval(0);
    //Robot = nullptr;
    connect(&timer_Update, SIGNAL(timeout()), this, SLOT(UpdateRoboDK()));

    // Make sure to connect the action to your callback (slot)
    connect(action_display, SIGNAL(triggered(bool)), this, SLOT(callback_display(bool)), Qt::QueuedConnection);

    // Here you can add one or more actions in the menu
    menu1 = menubar->addMenu("OpenGL");
    qDebug() << "Setting up the menu bar";
    menu1->addAction(action_display);

    // If desired, trigger the real time operation here:
    action_display->setChecked(true);
    DisplayActive = true;
    timer_Update.start();

    // return string is reserverd for future compatibility
    return "";
};


void PluginExample::PluginUnload(){
    // Cleanup the plugin
    qDebug() << "Unloading plugin " << PluginName();

    // remove the menu
    menu1->deleteLater();
    menu1 = nullptr;
    // remove the toolbar
    toolbar1->deleteLater();
    toolbar1 = nullptr;

}

void PluginExample::PluginLoadToolbar(QMainWindow *mw, int icon_size){
    // Create a new toolbar:
    toolbar1 = mw->addToolBar("OpenGL Display");
    toolbar1->setIconSize(QSize(icon_size, icon_size));

    // Important: It is highly recommended to set an object name on toolbars. This allows saving the preferred location of the toolbar by the user
    toolbar1->setObjectName(PluginName() + "-Display");

    // Add a new button to the toolbar
    toolbar1->addAction(action_display);
}


bool PluginExample::PluginItemClick(Item item, QMenu *menu, TypeClick click_type){
    qDebug() << "Selected item: " << item->Name() << " of type " << item->Type() << " click type: " << click_type;
    return false;
}

QString PluginExample::PluginCommand(const QString &command, const QString &value){
    qDebug() << "Received command: " << command << "    With value: " << value;
    if (command.compare("Information", Qt::CaseInsensitive) == 0){
        return "Done";
    }

    return "";
}

// Render your own graphics here. This function is called every time the OpenGL window is displayed. The RoboDK OpenGL context is active at this moment.
// Make sure to make this code as fast as possible to not provoke render lags
void PluginExample::PluginEvent(TypeEvent event_type){
    switch (event_type) {
    case EventChanged:        
        //qDebug() << "An item has been added or deleted. Current station: " << RDK->getActiveStation()->Name();
        // Use: RDK->getActiveStation() to get the open station. This call always returns a valid pointer
        // Use: RDK->Valid(item ) to check if an item exists (it could have been deleted! Therefore, provoke a crash when using a method)
        /*if (!RDK->Valid(Robot)){
            Robot = nullptr;
        }*/

        /*if (!RDK->Valid(Robot)) {
            Robot = nullptr;
        }*/
        break;
    case EventMoved:
        break;
    case EventRender:
        //qDebug() << "Render event";
        RenderOpenGL();
        break;
    default:
        qDebug() << "Unknown/future event: " << event_type;

    }
}

//----------------------------------------------------------------------------------
// Define your own button callbacks here

void PluginExample::callback_display(bool display_on){
    DisplayActive = display_on;
    qDebug() << "Display active: " << DisplayActive;
    if (DisplayActive) {
        timer_Update.start();
    } else {
        timer_Update.stop();
    }
}

void PluginExample::UpdateRoboDK(){
    // provoke full RoboDK screen update
    RDK->Render();
}


void PluginExample::RenderOpenGL(){
    // This function is called with the current OpenGL context active
    if (!DisplayActive){
        qDebug() << "Skipping custom OpenGL render";
        return;
    }
    qDebug() << "Customized OpenGL display...";

    qint64 time_ms = QDateTime::currentDateTime().toMSecsSinceEpoch();
    //double robodk_time_ms = RDK->Command("SimulationTime").toDouble();

    // Turn at 20 degrees per second with ms accuracy
    float rotation_deg = 0.001*(((20)*time_ms) % 360000);
    qDebug() << "Rotation angle: " << rotation_deg << " deg";

    // Apply model view transformation
    // The origin is the station coordinate system (WCS)
    glPushMatrix();
    glRotated(rotation_deg, 0,0,1);

    // Display a purple triangle
    glColor3f(1.0f, 0.0f, 1.0f); // set color to purple
    glBegin(GL_TRIANGLES); // draw one signle triangle
    glVertex3f(0.0f, 0.0f, 0.0f);
    glVertex3f(0.0f, 5000.0f, 0.0f);
    glVertex3f(0.0f, 0.0f, 5000.0f);
    glEnd();

    // Release the transformation
    glPopMatrix(); // Important

    qDebug() << "Done";
}






