#include "pluginexample.h"
#include "robodktools.h"
#include "irobodk.h"
#include "iitem.h"

#include "formrobotpilot.h"

#include <QMainWindow>
#include <QToolBar>
#include <QDebug>
#include <QAction>
#include <QKeySequence>
#include <QStatusBar>
#include <QMenuBar>
#include <QTextEdit>
#include <QDateTime>
#include <QIcon>
#include <QDesktopServices>
#include <QElapsedTimer>
#include <QApplication>

//------------------------------- RoboDK Plug-in commands ------------------------------


QString PluginExample::PluginName() {
    return "Example Plugin";
}


QString PluginExample::PluginLoad(QMainWindow *mw, QMenuBar *menubar, QStatusBar *statusbar, RoboDK *rdk, const QString &settings) {
    RDK = rdk;
    MainWindow = mw;
    StatusBar = statusbar;
    qDebug() << "Loading plugin " << PluginName();
    qDebug() << "Using settings: " << settings; // reserved for future compatibility

    // it is highly recommended to use the statusbar for debugging purposes (pass /DEBUG as an argument to see debug result in RoboDK)
    qDebug() << "Setting up the status bar";
    StatusBar->showMessage(tr("RoboDK Plugin %1 is being loaded").arg(PluginName()));

    // initialize resources for the plugin (if required):
    Q_INIT_RESOURCE(resources1);

    // Here you can add all the "Actions": these actions are callbacks from buttons selected from the menu or the toolbar
    action_information = new QAction(QIcon(":/resources/information.png"), tr("Plugin Speed Information"));
    action_information->setShortcut(QKeySequence("Ctrl+I"));
    action_robotpilot = new QAction(QIcon(":/resources/code.png"), tr("Robot Pilot Form"));
    action_help = new QAction(QIcon(":/resources/help.png"), tr("RoboDK Plugins - Help"));
    // Make sure to connect the action to your callback (slot)
    connect(action_information, SIGNAL(triggered()), this, SLOT(callback_benchmarkInfo()), Qt::QueuedConnection);
    connect(action_robotpilot, SIGNAL(triggered()), this, SLOT(callback_robotpilot()), Qt::QueuedConnection);
    connect(action_help, SIGNAL(triggered()), this, SLOT(callback_help()), Qt::QueuedConnection);

    // Here you can add one or more actions in the menu
    menu1 = menubar->addMenu("Plugin Example Menu");
    qDebug() << "Setting up the menu bar";
    menu1->addAction(action_information);
    menu1->addAction(action_robotpilot);
    menu1->addAction(action_help);

    // Important: reset the robot pilot dock/form pointer so that it is created the first time
    dock_robotpilot = nullptr;
    form_robotpilot = nullptr;

    // return string is reserved for future compatibility
    return "";
}


void PluginExample::PluginUnload() {
    // Cleanup the plugin
    qDebug() << "Unloading plugin " << PluginName();

    // remove the menu
    menu1->deleteLater();
    menu1 = nullptr;
    // remove the toolbar
    toolbar1->deleteLater();
    toolbar1 = nullptr;

    // remove the actions (not owned by the menu/toolbar, so they are not deleted automatically)
    action_information->deleteLater();
    action_information = nullptr;
    action_robotpilot->deleteLater();
    action_robotpilot = nullptr;
    action_help->deleteLater();
    action_help = nullptr;

    if (dock_robotpilot != nullptr) {
        dock_robotpilot->close();
        dock_robotpilot = nullptr;
        form_robotpilot = nullptr;
    }

    // remove resources
    Q_CLEANUP_RESOURCE(resources1);
}

void PluginExample::PluginLoadToolbar(QMainWindow *mw, int icon_size) {
    // Create a new toolbar:
    toolbar1 = mw->addToolBar("Plugin Example Toolbar");
    toolbar1->setIconSize(QSize(icon_size, icon_size));

    // Important: It is highly recommended to set an object name on toolbars. This allows saving the preferred location of the toolbar by the user
    toolbar1->setObjectName(PluginName() + "-Toolbar1");

    // Add a new button to the toolbar
    toolbar1->addAction(action_information);
    toolbar1->addAction(action_robotpilot);
    toolbar1->addAction(action_help);
}


bool PluginExample::PluginItemClick(Item item, QMenu *menu, TypeClick click_type) {
    qDebug() << "Selected item: " << item->Name() << " of type " << item->Type() << " click type: " << click_type;

    if (item->Type() == IItem::ITEM_TYPE_OBJECT) {
        //menu->actions().insert(0, action_btn1); // add action at the beginning
        menu->addAction(action_information); // add action at the end
        qDebug() << "Done";
        return false;
    } else if (item->Type() == IItem::ITEM_TYPE_ROBOT) {
        //menu->actions().insert(0, action_robotpilot); // add action at the beginning
        menu->addAction(action_robotpilot); // add action at the end
        qDebug() << "Done";
        return false;
    }
    return false;
}

QString PluginExample::PluginCommand(const QString &command, const QString &value) {
    qDebug() << "Sent command: " << command << "    With value: " << value;
    if (command.compare("Information", Qt::CaseInsensitive) == 0) {
        callback_benchmarkInfo();
        return "Done";
    } else if (command.compare("RobotPilot", Qt::CaseInsensitive) == 0) {
        callback_robotpilot();
        return "Done";
    }

    return "";
}

void PluginExample::PluginEvent(TypeEvent event_type) {
    switch (event_type)
    {
    case EventRender:
        /// Display/Render the 3D scene.
        /// At this moment we can call RDK->DrawGeometry to customize the displayed scene
        /// qDebug() << "==== EventRender ====";
        break;

    case EventMoved:
        /// qDebug() << "Something has moved, such as a robot, reference frame, object or tool.
        /// It is very likely that an EventRender will be triggered immediately after this event
        /// qDebug() << "==== EventMoved ====";
        break;

    case EventChanged:
        /// qDebug() << "An item has been added or deleted. Current station: " << RDK->getActiveStation()->Name();
        /// If we added a new item (for example, a reference frame) it is very likely that an EventMoved will follow with the updated position of the newly added item(s)
        /// This event is also triggered when we change the active station and a new station gains focus.

        /// Example to check if the station changed and to load settings
        //if (RDK->getActiveStation() != STATION){
        //    SetDefaultSettings();
        //    STATION = RDK->getActiveStation();
        //    LoadSettings(); // will select the robot if there are settings.
        //}
        qDebug() << "==== EventChanged ====";
        if (form_robotpilot != nullptr) {
            form_robotpilot->SelectRobot();
        }
        break;

    case EventChangedStation:
        qDebug() << "==== EventChangedStation ====";

        if (dock_robotpilot) {
            dock_robotpilot->close();
            dock_robotpilot = nullptr;
        }
        break;

    case EventAbout2Save:
        qDebug() << "==== EventAbout2Save ====";
        /// The user requested to save the project and the RDK file will be saved to disk. It is recommended to save all station-specific settings at this moment.
        /// For example, you can use RDK.setParam("ParameterName", "ParameterValue") or RDK.setData("ParameterName", bytearray)
        //SaveSettings();
        break;

    case EventAbout2ChangeStation:
        /// The user requested to open a new RoboDK station (RDK file) or the user is navigating among different stations. This event is triggered before the current station looses focus.
        qDebug() << "==== EventAbout2ChangeStation ====";
        //SaveSettings();
        if (dock_robotpilot) {
            dock_robotpilot->close();
            dock_robotpilot = nullptr;
        }
        break;

    case EventAbout2CloseStation:
        /// The user requested to close the currently open RoboDK station (RDK file). The RDK file may be saved if the user and the corresponding event will be triggered.
        qDebug() << "==== EventAbout2CloseStation ====";
        //SaveSettings();
        //ROBOT = nullptr;
        if (dock_robotpilot) {
            dock_robotpilot->close();
            dock_robotpilot = nullptr;
        }
        break;

    case EventTrajectoryStep:
        qDebug() << "==== EventTrajectoryStep ====";
        break;

    default:
        if (event_type < EventApiMask) {
            qDebug() << "Unknown/future event: " << event_type;
            return;
        }
        break;
    }

    if (event_type < EventApiMask) {
        return;
    }

    int apiEvent = event_type & (EventApiMask - 1);

    // API Events
    switch (apiEvent)
    {
    case EVENT_SELECTIONTREE_CHANGED:
        qDebug() << "EVENT_SELECTIONTREE_CHANGED";
        break;

    case EVENT_ITEM_MOVED:
        qDebug() << "EVENT_ITEM_MOVED";
        break;

    case EVENT_REFERENCE_PICKED:
        qDebug() << "EVENT_REFERENCE_PICKED";
        break;

    case EVENT_REFERENCE_RELEASED:
        qDebug() << "EVENT_REFERENCE_RELEASED";
        break;

    case EVENT_TOOL_MODIFIED:
        qDebug() << "EVENT_TOOL_MODIFIED";
        break;

    case EVENT_CREATED_ISOCUBE:
        qDebug() << "EVENT_CREATED_ISOCUBE";
        break;

    case EVENT_SELECTION3D_CHANGED:
        qDebug() << "EVENT_SELECTION3D_CHANGED";
        break;

    case EVENT_VIEWPOSE_CHANGED:
        qDebug() << "EVENT_VIEWPOSE_CHANGED";
        break;

    case EVENT_ROBOT_MOVED:
        qDebug() << "EVENT_ROBOT_MOVED";
        break;

    case EVENT_KEY:
        qDebug() << "EVENT_KEY";
        break;

    case EVENT_ITEM_MOVED_POSE:
        qDebug() << "EVENT_ITEM_MOVED_POSE";
        break;

    case EVENT_COLLISIONMAP_RESET:
        qDebug() << "EVENT_COLLISIONMAP_RESET";
        break;

    case EVENT_COLLISIONMAP_TOO_LARGE:
        qDebug() << "EVENT_COLLISIONMAP_TOO_LARGE";
        break;

    case EVENT_CALIB_MEASUREMENT:
        qDebug() << "EVENT_CALIB_MEASUREMENT";
        break;

    case EVENT_SELECTION3D_CLICK:
        qDebug() << "EVENT_SELECTION3D_CLICK";
        break;

    case EVENT_CHANGED:
        qDebug() << "EVENT_CHANGED";
        break;

    case EVENT_RENAME:
        qDebug() << "EVENT_RENAME";
        break;

    case EVENT_SETVISIBLE:
        qDebug() << "EVENT_SETVISIBLE";
        break;

    case EVENT_STATIONCHANGED:
        qDebug() << "EVENT_STATIONCHANGED";
        break;

    case EVENT_PROGSLIDER_CHANGED:
        qDebug() << "EVENT_PROGSLIDER_CHANGED";
        break;

    case EVENT_PROGSLIDER_SET:
        qDebug() << "EVENT_PROGSLIDER_SET";
        break;

    default:
        qDebug() << "Unknown/future API event: " << apiEvent;
        break;
    }
}

//----------------------------------------------------------------------------------
// Define your own button callbacks here

// Formats one row of the benchmark table (metric name + measured value)
static QString BenchmarkRowHtml(const QString &metric, const QString &value) {
    return QString("<tr><td style=\"padding:4px 12px 4px 4px;\">%1</td>"
                    "<td style=\"padding:4px;font-family:monospace;text-align:right;\">%2</td></tr>")
            .arg(metric.toHtmlEscaped(), value.toHtmlEscaped());
}

// Wraps a set of BenchmarkRowHtml() rows into a complete Metric/Value table
static QString BenchmarkTableHtml(const QString &rows) {
    return QString("<table cellspacing=\"0\" style=\"border-collapse:collapse;\">"
                    "<tr>"
                    "<th style=\"padding:4px;text-align:left;font-weight:bold;\">Metric</th>"
                    "<th style=\"padding:4px;text-align:right;font-weight:bold;\">Value</th></tr>")
            + rows + "</table>";
}

void PluginExample::callback_benchmarkInfo() {
    static QDockWidget *dockedInfo = nullptr;
    if (dockedInfo != nullptr) {
        dockedInfo->deleteLater();
        QApplication::processEvents(); // force the dock widget to be removed
    }

    // Perform some timing tests using the RoboDK API
    RDK->ShowMessage("Starting timing tests", false);

    QString text_message_html;
    text_message_html += "<h2 style=\"margin-bottom:2px;\">Plugin Timing Tests Summary</h2>";
    text_message_html += QString("<p style=\"margin-top:0;font-weight:bold;\">%1</p>").arg(QDateTime::currentDateTime().toString());

    // Create the report widget now: this lets us show partial results while the (potentially slow) collision checks run below
    QTextEdit *text_editor = new QTextEdit();
    text_editor->setReadOnly(true);
    text_editor->setHtml(text_message_html);

    dockedInfo = AddDockWidget(MainWindow, text_editor, "Dock Plugin timing summary");

    const int ntests = 10000;
    Item robot = RDK->ItemUserPick("Select a robot arm", IItem::ITEM_TYPE_ROBOT_ARM);
    if (ItemValid(robot)) {
        Mat pose_fk;
        tJoints joints_ik;
        QList<tJoints> joints_ik_all;
        QElapsedTimer timer;

        QString benchmark_rows;
        benchmark_rows += BenchmarkRowHtml("Robot", robot->Name());

        // TODO: Add cpu information, frequency, RAM and OS info in 1 or 2 lines

        // Test Forward Kinematics (QElapsedTimer gives nanosecond resolution, unlike QDateTime's millisecond ticks)
        timer.start();
        for (int i = 0; i < ntests; i++) {
            pose_fk = robot->SolveFK(robot->Joints());
        }
        benchmark_rows += BenchmarkRowHtml("Forward Kinematics", QString("%1 microseconds").arg((1e-3 * timer.nsecsElapsed()) / ntests, 0, 'f', 2));

        // Test Inverse Kinematics
        timer.start();
        for (int i = 0; i < ntests; i++) {
            joints_ik = robot->SolveIK(pose_fk);
        }
        benchmark_rows += BenchmarkRowHtml("Inverse Kinematics", QString("%1 microseconds").arg((1e-3 * timer.nsecsElapsed()) / ntests, 0, 'f', 2));

        // Test Inverse Kinematics (all solutions)
        timer.start();
        for (int i = 0; i < ntests; i++) {
            joints_ik_all = robot->SolveIK_All(pose_fk);
        }
        benchmark_rows += BenchmarkRowHtml("Inverse Kinematics (all solutions)", QString("%1 microseconds").arg((1e-3 * timer.nsecsElapsed()) / ntests, 0, 'f', 2));

        // Test collisions for each inverse kinematics solution: fewer samples, but a more accurate timer (nanosecond accuracy)
        RDK->Collisions(); // Run once first: the first call needs extra bookkeeping for all loaded objects if collision checking was not already on
        timer.start();
        int nJoints = joints_ik_all.length();
        int nWithCollisions = 0;
        int nWithoutCollisions = 0;
        for (int i = 0; i < nJoints; i++) {
            robot->setJoints(joints_ik_all.at(i));
            RDK->Render(IRoboDK::RenderUpdateOnly);
            int nCollisions = RDK->Collisions();
            if (nCollisions > 0) {
                nWithCollisions++;
            } else {
                nWithoutCollisions++;
            }
        }
        double ms_collisions = (1e-6 * timer.nsecsElapsed()) / nJoints;
        double samples_x_sec = 1000.0 / ms_collisions;
        qDebug() << "ms per collision: " << ms_collisions;
        qDebug() << "Collision samples per second: " << samples_x_sec;

        benchmark_rows += BenchmarkRowHtml(QString("Collision check (%1 samples)").arg(nJoints), QString("%1 ms/sample").arg(ms_collisions, 0, 'f', 2));
        benchmark_rows += BenchmarkRowHtml("Collision check rate", QString("%1 samples/sec").arg(samples_x_sec, 0, 'f', 2));
        benchmark_rows += BenchmarkRowHtml("Points with collisions", QString::number(nWithCollisions));
        benchmark_rows += BenchmarkRowHtml("Points without collisions", QString::number(nWithoutCollisions));

        // Show the table now: the program collision check below can take a while for long programs
        text_message_html += BenchmarkTableHtml(benchmark_rows);
        text_editor->setHtml(text_message_html);
        QApplication::processEvents(); // force the dock widget to repaint now, before the (possibly slow) program collision check below

        // Test collisions along the joint list of a full program, using the same metrics as above (optional: the user can cancel this step)
        Item program = RDK->getItem("Main", IItem::ITEM_TYPE_PROGRAM);
        if (!ItemValid(program)) {
            program = RDK->ItemUserPick("Select a program to check for collisions (optional)", IItem::ITEM_TYPE_PROGRAM);
            QApplication::processEvents(); // hides the popup right away as we are doing heavy processing afterwards
        }
        if (ItemValid(program)) {
            // Header for this section, only added if the program is valid
            text_message_html += QString("<h3 style=\"margin-bottom:2px;\">Program Collision Check: %1</h3>").arg(program->Name().toHtmlEscaped());

            RDK->ShowMessage("Calculating collisions for program: " + program->Name() + " ...", false);
            tMatrix2D *list_joints = Matrix2D_Create();
            QString err_msg;
            int result = program->InstructionListJoints(err_msg, list_joints, 1, 1, IRoboDK::COLLISION_OFF);

            QString program_rows;
            if (result >= 0) {
                int nDOFs = robot->Joints().Length();
                int nSteps = Matrix2D_Get_ncols(list_joints);
                int nProgWithCollisions = 0;
                int nProgWithoutCollisions = 0;

                timer.start();
                for (int col = 0; col < nSteps; col++) {
                    // Each column of the matrix holds one step: [J1..Jn, ERROR, MM_STEP, DEG_STEP, MOVE_ID]
                    tJoints step_joints(list_joints, col, nDOFs);
                    robot->setJoints(step_joints);
                    RDK->Render(IRoboDK::RenderUpdateOnly);
                    int nCollisions = RDK->Collisions();
                    if (nCollisions > 0) {
                        nProgWithCollisions++;
                    } else {
                        nProgWithoutCollisions++;
                    }
                    // Update the progress from time to time:
                    if (col % 100 == 0){
                        RDK->Command("ProgressBar", QString("%1").arg(100.0*col/nSteps));
                    }
                }
                RDK->Command("ProgressBar", "-1");
                double ms_prog_collisions = (1e-6 * timer.nsecsElapsed()) / nSteps;
                double prog_samples_x_sec = 1000.0 / ms_prog_collisions;

                program_rows += BenchmarkRowHtml(QString("Collision check (%1 steps)").arg(nSteps), QString("%1 ms/step").arg(ms_prog_collisions, 0, 'f', 2));
                program_rows += BenchmarkRowHtml("Collision check rate", QString("%1 samples/sec").arg(prog_samples_x_sec, 0, 'f', 2));
                program_rows += BenchmarkRowHtml("Points with collisions", QString::number(nProgWithCollisions));
                program_rows += BenchmarkRowHtml("Points without collisions", QString::number(nProgWithoutCollisions));
            } else {
                qDebug() << "InstructionListJoints failed: " << err_msg;
                program_rows += BenchmarkRowHtml("Collision check", tr("Failed: %1").arg(err_msg));
            }

            ::Matrix2D_Delete(&list_joints);

            text_message_html += BenchmarkTableHtml(program_rows);

            // Update the report now that the program collision check is done
            text_editor->setHtml(text_message_html);
        }

    } else {
        text_message_html += "<p><i>No robot available to run Kinematic tests</i></p>";
        text_editor->setHtml(text_message_html);
    }

    RDK->ShowMessage("Done with benchmark calculation", false);
}

void PluginExample::callback_robotpilot() {
    if (dock_robotpilot != nullptr) {
        // prevent opening more than 1 form
        RDK->ShowMessage("Robot pilot form is already open", false);
        return;
    }
    RDK->ShowMessage("Opening robot pilot form...", false);
    form_robotpilot = new FormRobotPilot(RDK, MainWindow);
    dock_robotpilot = AddDockWidget(MainWindow, form_robotpilot, "Robot Pilot");
    connect(form_robotpilot, SIGNAL(destroyed()), this, SLOT(callback_robotpilot_closed()));
}

void PluginExample::callback_robotpilot_closed() {
    // it is important to reset pointers when the form is closed (deleted)
    dock_robotpilot = nullptr;
    form_robotpilot = nullptr;
    RDK->ShowMessage("Closed robot pilot", false);
}

void PluginExample::callback_help() {
    QDesktopServices::openUrl(QUrl("https://robodk.com/CreatePlugin"));
}
