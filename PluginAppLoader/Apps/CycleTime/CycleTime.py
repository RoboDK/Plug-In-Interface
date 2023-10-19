# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Generate a cycle time report for Program(s).
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# More information on RoboDK Apps here:
#     https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader
#
# --------------------------------------------

from robodk import robolink, robodialogs, roboapps
import os


def CycleTime(RDK=None, programs=None):
    """
    Generate a cycle time report for Program(s).
    """

    if RDK is None:
        RDK = robolink.Robolink()

    if programs is None:
        programs = [x for x in RDK.Selection() if x.type in [robolink.ITEM_TYPE_PROGRAM]]
        if not programs:
            programs = RDK.ItemUserPick('Select the program to use for cycle time', robolink.ITEM_TYPE_PROGRAM)
            if not programs.Valid():
                return
            programs = [programs]
    else:
        programs = [x for x in programs if x.type in [robolink.ITEM_TYPE_PROGRAM]]
        if not programs:
            return

    # Retrieve the cycle time estimates
    progs_data = []
    for prog_item in programs:

        robot_item = prog_item.getLink(robolink.ITEM_TYPE_ROBOT)
        if not robot_item.Valid():
            robot_item = RDK.ItemUserPick('Select the robot associated with the program "%s"' % prog_item.Name(), robolink.ITEM_TYPE_ROBOT)
            if not robot_item.Valid():
                continue
            prog_item.setRobot(robot_item)

        valid_instructions, program_time, program_distance, valid_ratio, readable_msg = prog_item.Update()
        progs_data.append((prog_item.Name(), valid_ratio * 100, program_distance, program_time))

    if not progs_data:
        return

    # Create an HTML table to show to the user
    headers = "Program\tFeasibility (%)\tTravel Length (mm)\tCycle Time (s)"
    msg_html = "<table border=1><tr><td>" + headers.replace('\t', '</td><td>') + "</td></tr>"
    for prog_data in progs_data:
        prog_name, valid_ratio, program_distance, program_time = prog_data
        newline = "%s\t%.0f %%\t%.1f mm\t%.1f s" % (prog_name, valid_ratio, program_distance, program_time)
        msg_html = msg_html + '<tr><td>' + newline.replace('\t', '</td><td>') + '</td></tr>'
    msg_html = msg_html + '</table>'
    RDK.ShowMessage(msg_html)

    # Save as a .CSV file
    save_path = RDK.getParam('PATH_OPENSTATION')
    if not save_path:
        save_path = RDK.getParam('PATH_DESKTOP')
    file_path = robodialogs.getSaveFileName(path_preference=save_path, strfile=RDK.ActiveStation().Name().strip().replace(' ', '-') + '-Cycle-Time.csv', defaultextension='.csv', filetypes=[('CSV Files', '.csv')])
    if not file_path:
        return

    with open(file_path, 'w') as f:
        f.write(headers.replace('\t', ',') + '\n')
        for prog_data in progs_data:
            prog_name, valid_ratio, program_distance, program_time = prog_data
            f.write('%s,%.0f,%.6f,%.6f\n' % (prog_name, valid_ratio, program_distance, program_time))

    os.startfile(file_path)


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        CycleTime()


if __name__ == '__main__':
    runmain()