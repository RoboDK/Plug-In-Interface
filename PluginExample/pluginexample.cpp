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
#include <QSysInfo>
#include <QThread>
#include <QVector>

// Platform-specific headers used only to read the CPU model/frequency and total RAM
// (Qt does not expose this information through a cross-platform API)
#if defined(Q_OS_WIN)
#include <QSettings>
#include <windows.h>
#elif defined(Q_OS_MACOS)
#include <sys/sysctl.h>
#elif defined(Q_OS_LINUX)
#include <QFile>
#include <unistd.h>
#endif

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
    action_benchmarkInfo = new QAction(QIcon(":/resources/information.png"), tr("Plugin Speed Information"));
    action_benchmarkInfo->setShortcut(QKeySequence("Ctrl+I"));
    action_benchmarkInfo->setObjectName("actionBenchmarkInfo");
    action_robotpilot = new QAction(QIcon(":/resources/code.png"), tr("Robot Pilot Form"));
    action_help = new QAction(QIcon(":/resources/help.png"), tr("RoboDK Plugins - Help"));
    // Make sure to connect the action to your callback (slot)
    connect(action_benchmarkInfo, SIGNAL(triggered()), this, SLOT(callback_benchmarkInfo()), Qt::QueuedConnection);
    connect(action_robotpilot, SIGNAL(triggered()), this, SLOT(callback_robotpilot()), Qt::QueuedConnection);
    connect(action_help, SIGNAL(triggered()), this, SLOT(callback_help()), Qt::QueuedConnection);

    // Here you can add one or more actions in the menu
    menu1 = menubar->addMenu("Plugin Example Menu");
    qDebug() << "Setting up the menu bar";
    menu1->addAction(action_benchmarkInfo);
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
    action_benchmarkInfo->deleteLater();
    action_benchmarkInfo = nullptr;
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
    toolbar1->addAction(action_benchmarkInfo);
    toolbar1->addAction(action_robotpilot);
    toolbar1->addAction(action_help);
}


bool PluginExample::PluginItemClick(Item item, QMenu *menu, TypeClick click_type) {
    qDebug() << "Selected item: " << item->Name() << " of type " << item->Type() << " click type: " << click_type;

    if (item->Type() == IItem::ITEM_TYPE_OBJECT) {
        //menu->actions().insert(0, action_btn1); // add action at the beginning
        menu->addAction(action_benchmarkInfo); // add action at the end
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

// One row of the benchmark report: either a plain metric/value pair, or (if is_section is set)
// a full-width section title. Kept as data so the same rows can be rendered both as an HTML
// table (for the dock widget) and as an aligned plain-text table (for the console).
struct BenchmarkRow {
    QString metric;
    QString value;
    bool is_section = false;
};

// Formats one row of the benchmark table (metric name + measured value)
static QString BenchmarkRowHtml(const QString &metric, const QString &value) {
    return QString("<tr><td style=\"padding:4px 12px 4px 4px;\">%1</td>"
                    "<td style=\"padding:4px;font-family:monospace;text-align:right;\">%2</td></tr>")
            .arg(metric.toHtmlEscaped(), value.toHtmlEscaped());
}

// Returns 2-3 benchmark rows describing the System (OS), CPU (model, cores, frequency) and RAM of this computer.
// The CPU model/frequency and total RAM require a few OS-specific calls since Qt does not
// expose them directly; any piece that is not available on this platform (e.g. CPU frequency
// on Apple Silicon Macs) is simply left out instead of failing.
static QVector<BenchmarkRow> HardwareInfoRows() {
    QString cpu_model;
    QString cpu_freq;
    QString ram_total;

#if defined(Q_OS_WIN)
    QSettings cpu_key(R"(HKEY_LOCAL_MACHINE\HARDWARE\DESCRIPTION\System\CentralProcessor\0)", QSettings::NativeFormat);
    cpu_model = cpu_key.value("ProcessorNameString").toString().trimmed();
    int mhz = cpu_key.value("~MHz").toInt();
    if (mhz > 0) {
        cpu_freq = QString("%1 GHz").arg(mhz / 1000.0, 0, 'f', 2);
    }

    MEMORYSTATUSEX mem_status;
    mem_status.dwLength = sizeof(mem_status);
    if (GlobalMemoryStatusEx(&mem_status)) {
        ram_total = QString("%1 GB").arg(mem_status.ullTotalPhys / (1024.0 * 1024.0 * 1024.0), 0, 'f', 1);
    }

#elif defined(Q_OS_MACOS)
    char cpu_brand[256] = {};
    size_t cpu_brand_size = sizeof(cpu_brand);
    if (sysctlbyname("machdep.cpu.brand_string", cpu_brand, &cpu_brand_size, nullptr, 0) == 0) {
        cpu_model = QString::fromLocal8Bit(cpu_brand);
    }

    qint64 freq_hz = 0;
    size_t freq_size = sizeof(freq_hz);
    // Not available on Apple Silicon Macs: sysctlbyname() fails here and cpu_freq stays empty
    if (sysctlbyname("hw.cpufrequency", &freq_hz, &freq_size, nullptr, 0) == 0 && freq_hz > 0) {
        cpu_freq = QString("%1 GHz").arg(freq_hz / 1.0e9, 0, 'f', 2);
    }

    qint64 ram_bytes = 0;
    size_t ram_size = sizeof(ram_bytes);
    if (sysctlbyname("hw.memsize", &ram_bytes, &ram_size, nullptr, 0) == 0) {
        ram_total = QString("%1 GB").arg(ram_bytes / (1024.0 * 1024.0 * 1024.0), 0, 'f', 1);
    }

#elif defined(Q_OS_LINUX)
    QFile cpuinfo("/proc/cpuinfo");
    if (cpuinfo.open(QIODevice::ReadOnly | QIODevice::Text)) {
        const QStringList lines = QString::fromLocal8Bit(cpuinfo.readAll()).split('\n');
        for (const QString &line : lines) {
            if (cpu_model.isEmpty() && line.startsWith("model name")) {
                cpu_model = line.section(':', 1).trimmed();
            } else if (cpu_freq.isEmpty() && line.startsWith("cpu MHz")) {
                cpu_freq = QString("%1 GHz").arg(line.section(':', 1).trimmed().toDouble() / 1000.0, 0, 'f', 2);
            }
        }
    }

    long n_pages = sysconf(_SC_PHYS_PAGES);
    long page_size = sysconf(_SC_PAGE_SIZE);
    if (n_pages > 0 && page_size > 0) {
        ram_total = QString("%1 GB").arg((double(n_pages) * page_size) / (1024.0 * 1024.0 * 1024.0), 0, 'f', 1);
    }
#endif

    if (cpu_model.isEmpty()) {
        cpu_model = QSysInfo::currentCpuArchitecture();
    }

    QString cpu_value = QString("%1, %2 cores").arg(cpu_model, QString::number(QThread::idealThreadCount()));
    if (!cpu_freq.isEmpty()) {
        cpu_value += QString(" @ %1").arg(cpu_freq);
    }

    QVector<BenchmarkRow> rows;
    rows.append({"System", QSysInfo::prettyProductName()});
    rows.append({"CPU", cpu_value});
    if (!ram_total.isEmpty()) {
        rows.append({"RAM", ram_total});
    }
    return rows;
}

// Formats a full-width section header row inside the benchmark table (keeps everything in one
// table so both columns stay the same width instead of each table sizing itself independently)
static QString BenchmarkSectionRowHtml(const QString &title) {
    return QString("<tr><td colspan=\"2\" style=\"padding:10px 4px 4px 4px;font-weight:bold;border-top:1px solid #999;\">%1</td></tr>")
            .arg(title.toHtmlEscaped());
}

// Wraps the accumulated rows into a complete Metric/Value HTML table (for the dock widget)
static QString BenchmarkTableHtml(const QVector<BenchmarkRow> &rows) {
    QString html_rows;
    for (const BenchmarkRow &row : rows) {
        html_rows += row.is_section ? BenchmarkSectionRowHtml(row.metric) : BenchmarkRowHtml(row.metric, row.value);
    }
    return QString("<table cellspacing=\"0\" style=\"border-collapse:collapse;\">"
                    "<tr>"
                    "<th style=\"padding:4px;text-align:left;font-weight:bold;\">Metric</th>"
                    "<th style=\"padding:4px;text-align:right;font-weight:bold;\">Value</th></tr>")
            + html_rows + "</table>";
}

// Formats the accumulated rows as an aligned, human-readable plain-text table (for console output)
static QString BenchmarkTableText(const QVector<BenchmarkRow> &rows) {
    const int metric_width = 40;
    QString text = QString("%1  Value\n").arg(QString("Metric").leftJustified(metric_width));
    text += QString(metric_width + 10, QChar('-')) + "\n";
    for (const BenchmarkRow &row : rows) {
        if (row.is_section) {
            text += QString("\n-- %1 --\n").arg(row.metric);
        } else {
            text += QString("%1  %2\n").arg(row.metric.leftJustified(metric_width), row.value);
        }
    }
    return text;
}

void PluginExample::callback_benchmarkInfo() {
    static QDockWidget *dockedInfo = nullptr;
    if (dockedInfo != nullptr) {
        dockedInfo->close();
        QApplication::processEvents(); // force the dock widget to be removed
    }

    // Perform some timing tests using the RoboDK API
    RDK->ShowMessage("Starting timing tests", false);

    QString header_html;
    header_html += "<h2 style=\"margin-bottom:2px;\">Plugin Timing Tests Summary</h2>";
    header_html += QString("<p style=\"margin-top:0;font-weight:bold;\">%1</p>").arg(QDateTime::currentDateTime().toString());

    QString text_message_html = header_html;

    // Create the report widget now: this lets us show partial results while the (potentially slow) collision checks run below
    QTextEdit *text_editor = new QTextEdit();
    text_editor->setReadOnly(true);
    text_editor->setHtml(text_message_html);

    dockedInfo = AddDockWidget(MainWindow, text_editor, "Dock Plugin timing summary");

    // Declared here (rather than inside the if-block below) so the rows collected so far are still
    // available afterwards to print the plain-text console report
    QVector<BenchmarkRow> benchmark_rows;

    const int ntests = 10000;
    Item robot = RDK->ItemUserPick("Select a robot arm", IItem::ITEM_TYPE_ROBOT_ARM);
    if (ItemValid(robot)) {
        Mat pose_fk;
        tJoints joints_ik;
        QList<tJoints> joints_ik_all;
        QElapsedTimer timer;

        benchmark_rows.append({"Robot", robot->Name()});
        benchmark_rows += HardwareInfoRows();

        // Test Forward Kinematics (QElapsedTimer gives nanosecond resolution, unlike QDateTime's millisecond ticks)
        timer.start();
        for (int i = 0; i < ntests; i++) {
            pose_fk = robot->SolveFK(robot->Joints());
        }
        benchmark_rows.append({"Forward Kinematics", QString("%1 microseconds").arg((1e-3 * timer.nsecsElapsed()) / ntests, 0, 'f', 2)});

        // Test Inverse Kinematics
        timer.start();
        for (int i = 0; i < ntests; i++) {
            joints_ik = robot->SolveIK(pose_fk);
        }
        benchmark_rows.append({"Inverse Kinematics", QString("%1 microseconds").arg((1e-3 * timer.nsecsElapsed()) / ntests, 0, 'f', 2)});

        // Test Inverse Kinematics (all solutions)
        timer.start();
        for (int i = 0; i < ntests; i++) {
            joints_ik_all = robot->SolveIK_All(pose_fk);
        }
        benchmark_rows.append({"Inverse Kinematics (all solutions)", QString("%1 microseconds").arg((1e-3 * timer.nsecsElapsed()) / ntests, 0, 'f', 2)});

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

        benchmark_rows.append({QString("Collision check (%1 samples)").arg(nJoints), QString("%1 ms/sample").arg(ms_collisions, 0, 'f', 2)});
        benchmark_rows.append({"Collision check rate", QString("%1 samples/sec").arg(samples_x_sec, 0, 'f', 2)});
        benchmark_rows.append({"Points with collisions", QString::number(nWithCollisions)});
        benchmark_rows.append({"Points without collisions", QString::number(nWithoutCollisions)});

        // Show the table now: the program collision check below can take a while for long programs
        text_message_html = header_html + BenchmarkTableHtml(benchmark_rows);
        text_editor->setHtml(text_message_html);
        QApplication::processEvents(); // force the dock widget to repaint now, before the (possibly slow) program collision check below

        // Test collisions along the joint list of a full program, using the same metrics as above (optional: the user can cancel this step)
        Item program = RDK->getItem("Main", IItem::ITEM_TYPE_PROGRAM);
        if (!ItemValid(program)) {
            program = RDK->ItemUserPick("Select a program to check for collisions (optional)", IItem::ITEM_TYPE_PROGRAM);
            QApplication::processEvents(); // hides the popup right away as we are doing heavy processing afterwards
        }
        if (ItemValid(program)) {
            // Section header row for the program results, added to the same table so both columns stay the same width
            benchmark_rows.append({QString("Program Collision Check: %1").arg(program->Name()), QString(), true});

            RDK->ShowMessage("Calculating collisions for program: " + program->Name() + " ...", false);
            tMatrix2D *list_joints = Matrix2D_Create();
            QString err_msg;
            int result = program->InstructionListJoints(err_msg, list_joints, 1, 1, IRoboDK::COLLISION_OFF);

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

                benchmark_rows.append({QString("Collision check (%1 steps)").arg(nSteps), QString("%1 ms/step").arg(ms_prog_collisions, 0, 'f', 2)});
                benchmark_rows.append({"Collision check rate", QString("%1 samples/sec").arg(prog_samples_x_sec, 0, 'f', 2)});
                benchmark_rows.append({"Points with collisions", QString::number(nProgWithCollisions)});
                benchmark_rows.append({"Points without collisions", QString::number(nProgWithoutCollisions)});
            } else {
                qDebug() << "InstructionListJoints failed: " << err_msg;
                benchmark_rows.append({"Collision check", tr("Failed: %1").arg(err_msg)});
            }

            ::Matrix2D_Delete(&list_joints);

            // Update the report now that the program collision check is done (same table, so columns stay aligned)
            text_message_html = header_html + BenchmarkTableHtml(benchmark_rows);
            text_editor->setHtml(text_message_html);
        }

    } else {
        text_message_html = header_html + "<p><i>No robot available to run Kinematic tests</i></p>";
        text_editor->setHtml(text_message_html);
    }

    // Print the same results as an aligned, human-readable plain-text table in the console
    if (!benchmark_rows.isEmpty()) {
        qDebug().noquote() << "\n" + BenchmarkTableText(benchmark_rows);
    } else {
        qDebug() << "No robot available to run Kinematic tests";
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
