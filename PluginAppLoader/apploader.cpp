#include "apploader.h"
#include "dialogapplist.h"

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
#include <QMessageBox>
#include <QApplication>
#include <QDir>
#include <QSettings>
#include <QProcess>
#include <QMessageBox>

// Function to check and sort priority of apps
struct CheckPriority {
    template<typename AppType>
    bool operator()(const AppType *a, const AppType *b) const {
        return a->Priority < b->Priority;
    }
};

//------------------------------- RoboDK Plug-in commands ------------------------------
QString AppLoader::PluginName(){
    return "App Loader";
}

QString AppLoader::PluginLoad(QMainWindow *mw, QMenuBar *menubar, QStatusBar *statusbar, RoboDK *rdk, const QString &settings){
    RDK = rdk;
    MainWindow = mw;
    MenuBar = menubar;
    StatusBar = statusbar;
    qDebug() << "Loading plugin " << PluginName();
    qDebug() << "Using settings: " << settings; // reserved for future compatibility

    // it is highly recommended to use the statusbar for debugging purposes (pass /DEBUG as an argument to see debug result in RoboDK)
    qDebug() << "Setting up the status bar";
    StatusBar->showMessage(tr("RoboDK Plugin %1 is being loaded").arg(PluginName()));


    // ---------------------------------------------------
    // We can get some settings from RoboDK
    //FilePythonExe = RDK->getParam("PYTHON_EXEC"); //python";
    PathApps = RDK->getParam("PATH_ROBODK") + "/Apps";

    // Here you can add all the "Actions": these actions are callbacks from buttons selected from the menu or the toolbar
    action_Apps = new QAction(tr("Apps List"));
    action_Apps->setShortcut(QKeySequence("Shift+A"));

    // Make sure to connect the action to your callback (slot)
    connect(action_Apps, SIGNAL(triggered()), this, SLOT(callback_AppList()), Qt::QueuedConnection);

    // look for apps and load them in the main menu
    AppsSearch();
    AppsLoadMenus();

    // adding the action before the Plug-Ins action in the Tools menu
    QMenu *menuTools = mw->findChild<QMenu *>("menu-Tools");
    QAction *actionPlugins = mw->findChild<QAction *>("action-Plugins");

    if (menuTools != nullptr && actionPlugins != nullptr){
        qDebug() << "Inserting App List menu action";
        menuTools->insertAction(actionPlugins, action_Apps);
    } else {
        qDebug() << "Warning! Plugins action not found: App List action not added to the menu";
    }

    // return string is reserverd for future compatibility
    return "";
}

void AppLoader::PluginUnload(){
    // Cleanup the plugin
    qDebug() << "Unloading plugin " << PluginName();

    // removing action app list
    if (action_Apps != nullptr){
        action_Apps->deleteLater();
        action_Apps = nullptr;
    }

    AppsDelete();
}

void AppLoader::PluginLoadToolbar(QMainWindow *mw, int icon_size){
    // this function may be called more than once, RoboDK may delete all the toolbars when it is reset or the window state changes
    IconSize = icon_size;

    // this function is called when RoboDK clears all toolbars, so all previously allocated toolbars have been deleted
    AllToolbars.clear();    

    // Create a new toolbar
    AppsLoadToolbars();
}

bool AppLoader::PluginItemClick(Item item, QMenu *menu, TypeClick click_type){
    qDebug() << "Selected item: " << item->Name() << " of type " << item->Type() << " click type: " << click_type;
    for (int i=0; i<ListActions.length(); i++){
        if (ListActions[i]->AppMenu != nullptr && !ListActions[i]->AppMenu->Active){
            continue;
        }
        int type_show = ListActions[i]->TypeShowOnContextMenu;
        if (item->Type() == type_show){
            menu->addAction(ListActions[i]->Action); // add action at the end
        }
    }
    return false;
}

QString AppLoader::PluginCommand(const QString &command, const QString &value){
    qDebug() << "Received command: " << command << "    With value: " << value;
    if (command.startsWith("OpenFile", Qt::CaseInsensitive)){
        // Execute the openfile command (provided by RoboDK when a file with the pattern *.apploader.rdkp is opened in RoboDK)
        // Since Qt doesn't have great tools for unzipping files we can run Python code to do so
        const char * python_code_c = R"""(
import os
import zipfile
import sys

def printFlush(msg):
    print(msg)
    #sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()

# Import tkinter
if sys.version_info[0] < 3: # Python 2.X only:
    import Tkinter as tkinter
    import tkMessageBox as messagebox
else: # Python 3.x only
    import tkinter
    from tkinter import messagebox

# Check if the package exists
def ExistingPackage(path_zip, path_extract):
    msg = ''
    with zipfile.ZipFile(path_zip, 'r') as zip_ref:
        zip_folders = []
        for name in zip_ref.namelist():
            dir = name.split('/')[0]
            if dir in zip_folders:
                continue
            zip_folders.append(dir)
            if os.path.isdir(path_extract + '/' + dir):
                msg += '    ' + u"\u2022" + " " + dir + '\n'
    if len(msg) > 0:
        msg = 'The following package(s) already exist:\n\n' + msg + '\nOverride?'
        return True, msg
    return False, msg

# Unzip a zip file
def UnZipDir(path_zip, path_extract):
    with zipfile.ZipFile(path_zip, 'r') as zip_ref:
        zip_ref.extractall(path_extract)

# Ask the user if we should override
def DoOverride(display_message):
    root = tkinter.Tk()
    root.overrideredirect(1)
    root.withdraw()
    result = messagebox.askquestion('Override?', display_message, icon='warning')#, parent=texto)
    if result == 'yes':
        root.destroy()
        return True
    else:
        root.destroy()
        return False

printFlush("Starting application")

exists, msg = ExistingPackage(file_path, apps_path)
if exists:
    if not DoOverride(msg):
        printFlush("App override cancelled")
        exit(0)
    else:
        printFlush("Overriding existing apps")

UnZipDir(file_path, apps_path)
printFlush('Done')
exit(0)
)""";

        QString python_code;
        python_code.append(QString("file_path = r'''" + value + "'''\n"));
        python_code.append(QString("apps_path = r'''" + PathApps + "'''\n"));
        python_code.append(python_code_c);

        if (RunPythonShell(RDK->getParam("PYTHON_EXEC"), python_code)){
            AppsReload();
        } else {
            qDebug() << "Something went wrong executing Python code";
        }
    }
    return "";
}

void AppLoader::PluginEvent(TypeEvent event_type){

}

//----------------------------------------------------------------------------------
void AppLoader::AppsReload(){
    // force reload of apps
    AppsLoadMenus();

    // force reload of the toolbar
    AppsLoadToolbars();
}

void AppLoader::AppsDelete(){
    AppsUnloadMenus();
    AppsUnloadToolbars();

    // delete all actions
    for (int i=AllActions.length()-1; i>=0; i--){
        AllActions.takeLast()->deleteLater();
    }

    // Delete collected lists (QActions, QToolbar and QMenus are deleted later)
    for (int i=ListActions.length()-1; i>=0; i--){
        delete ListActions.takeLast();
    }
    for (int i=ListMenus.length()-1; i>=0; i--){
        delete ListMenus.takeLast();
    }
    for (int i=ListToolbars.length()-1; i>=0; i--){
        delete ListToolbars.takeLast();
    }
}

void AppLoader::AppsSearch(){
    // We keep the list of all toolbars and menus to sort them properly and display the toolbar when required
    // (global variable)
    //QList<tAppMenu*> ListMenus;
    //QList<tAppToolbar*> ListToolbars;

    AppsDelete();

    // Get path to apps folder
    QString dir_apps_path = PathApps;
    QDir dir_apps(dir_apps_path);
    QStringList AppsDirList(dir_apps.entryList(QDir::Dirs));
    foreach (QString dirApp, AppsDirList) {
        // Ignore folders that start with an underscore
        if (dirApp.startsWith("_") || dirApp.startsWith(".")){
            continue;
        }
        qDebug() << "Loading App dir: " << dirApp;

        // Retrieve and/or create the INI file related to this app
        QString dirAppComplete = dir_apps_path + "/" + dirApp;
        QString fileSettings = dirAppComplete + "/Settings.ini";
        qDebug() << "Checking if file does not exist and is not writtable: " + fileSettings;

        // Make sure we can write to the same location if the file does not exist, otherwise, save to app data location
        if (false && !QFile::exists(fileSettings)){
            QFileInfo fileInfo(fileSettings);
            fileInfo.dir().path();

            //QFile(fileSettings).isWritable()
            QString newFileSettings = QStandardPaths::writableLocation(QStandardPaths::AppDataLocation) + "/Apps/" + dirApp + ".ini";
            if (!QFile::exists(newFileSettings)){
                RDK->ShowMessage(tr("Creating settings file for your new App <strong>%1</strong>:<br>%2<br><br>Location %3 is not writable").arg(dirApp).arg(newFileSettings).arg(fileSettings));
            }
            fileSettings = newFileSettings;
        }
        RDK->ShowMessage(tr("Loading App ") + dirApp + tr(". Using settings file: ") + fileSettings, false);

        // Load settings and save them (default settings will be set)
        QSettings settings(fileSettings, QSettings::IniFormat);
        QString menuName = settings.value("MenuName", dirApp).toString();
        bool appEnabled = settings.value("Enabled", true).toBool();
        double menuPriority = settings.value("MenuPriority", 50.0).toDouble();
        int toolbarArea = settings.value("ToolbarArea", 2).toInt();
        double toolbarSize = settings.value("ToolbarSizeRatio", 1.5).toDouble();
        QStringList RunCommands = settings.value("RunCommands", QStringList()).toStringList();

        settings.setValue("MenuName", menuName);
        settings.setValue("Enabled", appEnabled);
        settings.setValue("MenuPriority", menuPriority);
        settings.setValue("ToolbarArea", toolbarArea);
        settings.setValue("ToolbarSizeRatio", toolbarSize);
        settings.setValue("RunCommands", RunCommands);


        // Create a new list for menus and toolbars
        tAppToolbar *appToolbar = new tAppToolbar(menuName, menuPriority, toolbarArea, toolbarSize, appEnabled);
        tAppMenu *appMenu = new tAppMenu(menuName, menuPriority, appEnabled, dirApp, fileSettings);
        appMenu->Toolbar = appToolbar;
        ListMenus.append(appMenu);
        ListToolbars.append(appToolbar);

        // skip if we don't want this app (menu) visible. Toolbar won't be displayed either
        //if (!appEnabled){
        //    continue;
        //}

        // Run commands specified by each app (there could be conflicts/contradictions)
        if (appEnabled){
            foreach (QString command, RunCommands){
                RDK->Command(command);
            }
        }

        // List of actions for the menu
        QList<tAppAction*> menuActions;
        // List of actions for the toolbar
        QList<tAppAction*> toolbarActions;

        // Get the list of files in the folder
        QDir dirAppi(dirAppComplete);
        QStringList filesApp(dirAppi.entryList(QDir::Files));

        // Iterate through each App (folder)
        foreach (QString file, filesApp){
            if (!(file.endsWith(".py", Qt::CaseInsensitive) || file.endsWith(".exe", Qt::CaseInsensitive))){
                continue;
            }
            if (file.startsWith("_")){
                continue;
            }

            // Get the key name for the settings file
            QString keyName(file);
            if (file.endsWith(".py", Qt::CaseInsensitive)){
                keyName.chop(3); // ends with PY
            } else {
                keyName.chop(4); // ends with EXE
            }

            QString name_guess(QString(keyName).replace("_"," "));

            // Read settings from AppSettings if they exist, otherwise, set the default values
            QString displayName = settings.value(keyName + "/DisplayName", name_guess).toString();
            QString comment = settings.value(keyName + "/Description", name_guess).toString();
            bool visible = settings.value(keyName + "/Visible", true).toBool();
            QString shortcutstr = settings.value(keyName + "/Shortcut", "").toString();
            bool checkable = settings.value(keyName + "/Checkable", false).toBool();
            bool addToolBar = settings.value(keyName + "/AddToToolbar", true).toBool();
            double priority = settings.value(keyName + "/Priority", 50.0f).toDouble();
            int type_leftclick = settings.value(keyName + "/TypeOnContextMenu", -1).toInt();

            // Prevent empty names
            if (displayName.isEmpty()){
                displayName = keyName;
            }

            // Save settings to AppSettings file to let the user change them if desired
            settings.setValue(keyName + "/DisplayName", displayName);
            settings.setValue(keyName + "/Description", comment);
            settings.setValue(keyName + "/Visible", visible);
            settings.setValue(keyName + "/Shortcut", shortcutstr);
            settings.setValue(keyName + "/Checkable", checkable);
            settings.setValue(keyName + "/AddToToolbar", addToolBar);
            settings.setValue(keyName + "/Priority", priority);
            settings.setValue(keyName + "/TypeOnContextMenu", type_leftclick);

            // Forget about this action if it is set to non visible
            if (!visible){
                continue;
            }

            // try to find a matching image given the key name:
            QIcon *icon;
            QString fileCompleteNoExt(dirAppComplete + "/" + keyName);
            QString iconfile;
            if (QFile::exists(fileCompleteNoExt + ".svg")){
                iconfile = fileCompleteNoExt + ".svg";
                icon = new QIcon(iconfile);
            } else if (QFile::exists(fileCompleteNoExt + ".png")){
                iconfile = fileCompleteNoExt + ".png";
                icon = new QIcon(iconfile);
            } else if (QFile::exists(fileCompleteNoExt + ".jpg")){
                iconfile = fileCompleteNoExt + ".jpg";
                icon = new QIcon(iconfile);
            } else if (QFile::exists(fileCompleteNoExt + ".ico")){
                iconfile = fileCompleteNoExt + ".ico";
                icon = new QIcon(iconfile);
            } else {
                icon = new QIcon();
            }

            // add icon active
            if (checkable && iconfile.length() > 4){
                QString iconfile_checked = QString(iconfile).insert(iconfile.length()-4,"Checked");
                if (QFile::exists(iconfile_checked)){
                    icon->addFile(iconfile_checked, QSize(), QIcon::Mode::Normal, QIcon::State::On);
                }
            }

            // create the new action
            QAction *action = new QAction(*icon, displayName);

            // apply shortcut, if available
            if (!shortcutstr.isEmpty()){
                action->setShortcut(QKeySequence(shortcutstr));
            }

            delete icon;

            // Add tooltips
            action->setWhatsThis(comment);
            action->setToolTip(comment);
            action->setStatusTip(comment);

            // set checkable
            if (checkable){
                action->setCheckable(true);
            }

            // Add the actions in the global list:
            ListActions.append(new tAppAction(action, priority, appMenu, type_leftclick));

            // Add the actions to the menu and toolbar
            menuActions.append(new tAppAction(action, priority, appMenu));
            if (addToolBar){
                toolbarActions.append(new tAppAction(action, priority, appMenu));
            }

            // Create a slot connection to trigger the script, use the object name to remember the file script that we need to run
            QString fileScript(dirAppComplete + "/" + file);
            action->setObjectName(fileScript);
            connect(action, &QAction::triggered, this, &AppLoader::onRunScript);

            // keep the pointers to delete them when the plugin is unloaded
            AllActions.append(action);
        }

        // Sort actions for the menu and the toolbar
        qSort(menuActions.begin(),    menuActions.end(),    CheckPriority());
        qSort(toolbarActions.begin(), toolbarActions.end(), CheckPriority());

        // Add menu actions to the menu
        for (int i=0; i<menuActions.length(); i++){
            appMenu->Actions.append(menuActions[i]->Action);
        }

        // Add toolbar actions to the toolbar
        for (int i=0; i<toolbarActions.length(); i++){
            appToolbar->Actions.append(toolbarActions[i]->Action);
        }
    }

    // Sort all actions
    if (ListActions.length() > 1){
        qSort(ListActions.begin(), ListActions.end(), CheckPriority());
    }

    // Sort menus
    if (ListMenus.length() > 1){
        qSort(ListMenus.begin(), ListMenus.end(), CheckPriority());
    }

    // Sort toolbars
    if (ListToolbars.length() > 1){
        qSort(ListToolbars.begin(), ListToolbars.end(), CheckPriority());
    }
}

void AppLoader::AppsLoadMenus(){
    AppsUnloadMenus();

    //AppsSearch();

    // Create all menus
    for (int i=0; i<ListMenus.length(); i++){
        tAppMenu *appmenu = ListMenus[i];
        if (!appmenu->Active){
            continue;
        }
        QMenu *menui = MenuBar->addMenu(appmenu->Name);
        menui->addActions(appmenu->Actions);
        AllMenus.append(menui);
    }

    // If we didn't find anything: add a help section
    if (AllMenus.length() <= 0 || AllActions.length() <= 0){
        // actions are callbacks from buttons selected from the menu or the toolbar
        QAction *action_information = new QAction(tr("Help (no RoboDK Apps loaded)"));
        connect(action_information, SIGNAL(triggered()), this, SLOT(callback_help()), Qt::QueuedConnection);
        AllActions.append(action_information);

        // Here you can add one or more actions in the menu
        QMenu *menu_help = MenuBar->addMenu(tr("RoboDK Apps"));
        qDebug() << "Setting up the help menu bar";
        menu_help->addAction(action_Apps); // show list of apps
        menu_help->addAction(action_information);
        AllMenus.append(menu_help);
        qDebug() << "Done";
    }
}

void AppLoader::AppsUnloadMenus(){
    // delete all menus
    for (int i=AllMenus.length()-1; i>=0; i--){
        AllMenus.takeLast()->deleteLater();
    }
}

void AppLoader::AppsUnloadToolbars(){
    // delete all the toolbars
    for (int i=AllToolbars.length()-1; i>=0; i--){
        AllToolbars.takeLast()->deleteLater();
    }
}

void AppLoader::AppsLoadToolbars(){
    AppsUnloadToolbars();

    // load toolbars
    for (int i=0; i<ListToolbars.length(); i++){
        tAppToolbar *appToolbar = ListToolbars[i];
        if (!appToolbar->Active || appToolbar->Actions.length() <= 0){
            continue;
        }
        QToolBar *toolbar_i = new QToolBar(appToolbar->Name);
        toolbar_i->addActions(appToolbar->Actions);
        if (IconSize > 0){
            toolbar_i->setIconSize(QSize(IconSize*appToolbar->SizeRatio, IconSize*appToolbar->SizeRatio));
        }
        toolbar_i->setObjectName(PluginName() + "-" + appToolbar->Name);
        Qt::ToolBarArea area = Qt::ToolBarArea::RightToolBarArea;
        if (appToolbar->ToolbarArea >= 0){
            area = (Qt::ToolBarArea) appToolbar->ToolbarArea;
        }
        MainWindow->addToolBar(area, toolbar_i);
        AllToolbars.append(toolbar_i);
    }
}

bool AppLoader::RunPythonShell(const QString &python_exec, const QString &python_code){
    QProcess *process = new QProcess();
    QStringList arguments;
    arguments.append("-i"); // use standard input as console input
    process->start(python_exec, arguments);//FilePythonExe);
    if (!process->waitForStarted(1000)){
        qDebug() << "Unable to start Python to run the file: " << python_exec;
        qDebug() << process->errorString();
        return false;
    }
    qDebug() << "Starting Python shell: " << python_exec;
    process->setReadChannel(QProcess::StandardOutput);

    // write the python code as if we were typing it on the shell
    process->write(python_code.toUtf8());
    process->waitForBytesWritten(1000);

    // wait until the process completes (or crashes)
    while (process->state() == QProcess::Running){
        // make sure we read stdin
        process->waitForFinished(100);
        process->waitForReadyRead(100);

        // display stdin and errors
        QString msg_stdout(process->readAllStandardOutput());
        QString msg_stderr(process->readAllStandardError());
        if (msg_stdout.length() > 0){
            QStringList lines(msg_stdout.split('\n'));
            for (int i=0; i<lines.length(); i++){
                qDebug().nospace().noquote()  << lines[i];
            }
        }
        if (msg_stderr.length() > 0){
            QStringList lines(msg_stderr.split('\n'));
            for (int i=0; i<lines.length(); i++){
                qDebug().nospace().noquote() << "ERROR: " << lines[i];
            }
        }
    }
    //process->waitForFinished(60000);
    process->close();
    process->deleteLater();
    return true;
}

void AppLoader::onRunScript(){
    // retrieve the sender action/button
    QAction *action = qobject_cast<QAction*>(QObject::sender());
    if (action == nullptr){
        qDebug() << "Warning: Unknown script to run";
        return;
    }

    // retrieve the executable/python file path
    QString filepath(action->objectName());
    if (!QFile::exists(filepath)){
        qDebug() << "Script file does not exist! " << filepath;
        return;
    }

    // If the action is checkable, save a station parameter with the name of the file (1= checked, 0= unchecked)
    if (action->isCheckable()){
        QFileInfo fileInfo(filepath);
        RDK->setParam(fileInfo.baseName(), action->isChecked() ? "1" : "0");
    }

    // start the process
    QProcess *proc = new QProcess();
    QStringList args;

    connect(proc, SIGNAL(finished(int)), this, SLOT(onScriptFinished()));

    // update environment to provide the same pythonpath used in RoboDK
    QProcessEnvironment env = QProcessEnvironment::systemEnvironment();
    QStringList envlist = env.toStringList();
    envlist.append("PYTHONPATH=" + RDK->getParam("PYTHONPATH"));
    proc->setEnvironment(envlist);

    // run the script
    qDebug() << "Running script: " << filepath;
    if (filepath.endsWith(".py", Qt::CaseInsensitive)){
        args.append(filepath);
        if (action->isCheckable()){ // pass an argument if the option is checkable
            args.append(action->isChecked() ? "Checked" : "Unchecked");
        }
        proc->start(RDK->getParam("PYTHON_EXEC"), args);
    } else {
        proc->start(filepath);
    }

}

// Triggered when a script finished executing
void AppLoader::onScriptFinished(){    
    QProcess *proc = qobject_cast<QProcess*>(QObject::sender());
    if (proc == nullptr){
        qDebug() << "Warning: Unknown process finished!";
        return;
    }

    qDebug() << "Script finished";

    // Display warning message when there is an error
    if (proc->exitCode() != 0){
        /*QString script_path("unknown");
        if (script_path.length() > 0){
            script_path = proc->arguments()[0];
        }*/
        //QString msg("Error running script:<br>" + script_path + "<br>");
        QString msg;
        msg = msg + "<font color='red'><strong>" + tr("Python script failed returning %1").arg(proc->exitCode()) + "</strong>";
        msg = msg + "<font face='consolas'>";
        msg = msg + "<br>" + QString(proc->readAllStandardError()).replace("\n", "<br>") + "</font></font>";
        msg = msg + "<br>" + QString(proc->readAllStandardOutput()).replace("\n", "<br>");
        RDK->ShowMessage(msg);
    }

    // Important! Delete the process
    proc->deleteLater();
}


// Define your own button callbacks here
void AppLoader::callback_AppList(){
    DialogAppList *dlg = new DialogAppList(this, MainWindow);
    dlg->exec();
}

void AppLoader::callback_help(){
    //QMessageBox::
    QString msg("<u>" + tr("About the <strong>AppLoader</strong> Plug-In for RoboDK") + "</u>");
    msg = msg + "<br><br>";
    msg = msg + tr("The App loader plugin allows you to easily load scripts and executable files as if they were plugins, adding scripts to the menu and toolbar.");
    msg = msg + "<br><br>";
    msg = msg + tr("No apps have been found in the RoboDK/Apps/ folder. Make sure to create a folder in the RoboDK/Apps folder with your scripts inside. ");
    msg = msg + tr("Select Tools-App List to enable existing apps. ");
    msg = msg + tr("INI files can also be modified to customize integration (order, context menu option, etc). If the INI file does not exist it will be automatically generated the first time a folder inside Apps is found.");
    msg = msg + "<br><br>";
    msg = msg + tr("More information here:");
    msg = msg + "<br><a href='https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader'>https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader</a><br>";
    RDK->ShowMessage(msg);
}
