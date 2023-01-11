# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Manage recorded 3D views using a list of named views
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# More information on RoboDK Apps here:
#     https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader
#
# --------------------------------------------

from robodk import robolink, robomath, robodialogs, roboapps
import ast
import sys
import os

import threading

global stop_threads
stop_threads = False

global STEPS_SIZE
STEPS_SIZE = 10.0  # mm, desired step size between split poses

global WAYPOINTS_DELAY
WAYPOINTS_DELAY = 0.0  # s, delay between waypoints/views (multi-select)

if sys.version_info[0] < 3:  # Python 2.X only:
    import Tkinter as tkinter
else:  # Python 3.x only
    import tkinter


def ViewManager():

    # Start the RoboDK API
    RDK = robolink.Robolink()

    # Name of the view we can use with the first button of the toolbar
    MAIN_VIEW_NAME = "ViewManager-View-0"

    ListNames = []
    ListPoses = []

    def SaveViews():
        on_Stop()

        # The first view is always the main view
        strall = ""
        for i in range(0, len(ListNames)):
            if i == 0 and ListNames[i] == MAIN_VIEW_NAME:
                continue

            x, y, z, a, b, c = robomath.Pose_2_KUKA(ListPoses[i])
            stri = "%s|[%.3f,%.3f,%.3f,%.3f,%.3f,%.3f]" % (ListNames[i], x, y, z, a, b, c)
            strall += "%s||" % stri
            print(stri)

        RDK.setParam("ViewNames", strall)

    def SaveSettings():
        on_Stop()

        global STEPS_SIZE
        global WAYPOINTS_DELAY

        STEPS_SIZE = float(varStepsSize.get())
        WAYPOINTS_DELAY = float(varWaypointDelay.get())

        RDK.setParam("ViewStepsSize", STEPS_SIZE)
        RDK.setParam("ViewWaypointsDelay", WAYPOINTS_DELAY)

    def threadMoveTo(poses, stop):
        RDK = robolink.Robolink()
        for pose in poses:
            RDK.setViewPose(pose)
            robomath.pause(1 / 100)
            if stop():
                break

    def NavigateTo(poses_to):
        on_Stop()

        global stop_threads
        stop_threads = False

        global STEPS_SIZE
        global WAYPOINTS_DELAY

        def PoseSplit(pose1, pose2, flatview=False):
            pose_delta = robomath.invH(pose1) * pose2
            pose_list = []

            # Calculate steps
            pose_delta_cam = pose1 * robomath.invH(pose2)  # Pose delta seen by the camera
            travel_mm = robomath.norm(pose_delta_cam.Pos())
            steps = travel_mm / STEPS_SIZE
            if steps > 1e6:
                print('Too many steps! ' + str(steps))
            steps = int(min(steps, 1e6))

            x, y, z, w, p, r = robomath.Pose_2_UR(pose_delta)

            xd = x / steps
            yd = y / steps
            zd = z / steps
            wd = w / steps
            pd = p / steps
            rd = r / steps
            for i in range(steps - 1):
                factor = i + 1
                pose_i = pose1 * robomath.UR_2_Pose([xd * factor, yd * factor, zd * factor, wd * factor, pd * factor, rd * factor])
                if flatview:
                    xyzabc = robomath.Pose_2_KUKA(robomath.invH(pose_i))
                    xyzabc[4] = 0
                    pose_i = robomath.invH(robomath.KUKA_2_Pose(xyzabc))

                pose_list.append(pose_i)

            pose_list.append(pose2)  # Ensure we do not 'jump'

            return pose_list

        add_delay = WAYPOINTS_DELAY > 0 and len(poses_to) > 1
        pose_lst = []
        pose_curr = RDK.ViewPose()
        for pose_to in poses_to:

            if stop_threads:
                return

            if pose_to == pose_curr:
                continue

            xyzabc1 = robomath.Pose_2_KUKA(robomath.invH(pose_curr))
            xyzabc2 = robomath.Pose_2_KUKA(robomath.invH(pose_to))

            keep_Y_flat = True
            if abs(xyzabc1[4]) > 5 or abs(xyzabc2[4]) > 5:
                print("Moving in full 6DOF")
                keep_Y_flat = False

            split_poses = PoseSplit(pose_curr, pose_to, flatview=keep_Y_flat)

            if add_delay:
                t = threading.Thread(target=threadMoveTo, args=(split_poses, lambda: stop_threads))
                t.start()
                t.join()  # need to join to have a delay
                robomath.pause(WAYPOINTS_DELAY)
            else:
                pose_lst.extend(split_poses)

            pose_curr = pose_to

        if not add_delay and len(pose_lst) > 0:
            t = threading.Thread(target=threadMoveTo, args=(pose_lst, lambda: stop_threads))
            t.start()  # no need to join, all poses are included

    def on_Close():
        on_Stop()
        SaveViews()
        SaveSettings()
        w.destroy()

    def on_Stop():
        global stop_threads
        stop_threads = True
        robomath.pause(0.1)

    def on_ListDelete():
        on_Stop()

        sel = listbox.curselection()
        if len(sel) == 0:
            print("Nothing selected")
            return

        for index in sel[::-1]:  # move backwards!!
            print(index)
            nm = ListNames[index]
            if robodialogs.ShowMessageYesNoCancel("Delete view: " + nm):
                del ListNames[index]
                del ListPoses[index]
                listbox.delete(index)  # delete from UI

                SaveViews()

                msg = "Deleted view: " + nm
                RDK.ShowMessage(msg, False)

    def on_ListRename():
        on_Stop()

        sel = listbox.curselection()
        if len(sel) == 0:
            print("Nothing selected")
            return

        for index in sel:
            print(index)
            lbli = ListNames[index]
            new_name = robodialogs.mbox("Enter the view name for %s" % listbox.get(index), entry=lbli)
            if not new_name:
                continue

            ListNames[index] = new_name
            listbox.delete(index)
            listbox.insert(index, new_name)

            msg = "Renamed selected view to " + ListNames[index]
            RDK.ShowMessage(msg, False)

        SaveViews()

    def on_ListUpdate():
        on_Stop()

        sel = listbox.curselection()
        index = 0
        if len(sel) == 0:
            #print("Nothing selected")
            #return
            index_after = len(ListNames)
            index = index_after
            new_name = "New View " + str(index + 1)
            listbox.insert(index_after, new_name)
            ListNames.append(new_name)
            ListPoses.append(RDK.ViewPose())

        else:
            for index in sel:
                print(index)
                ListPoses[index] = RDK.ViewPose()
                break

        SaveViews()

        msg = "Updated view: " + ListNames[index]
        RDK.ShowMessage(msg, False)

    def on_ListAdd():
        on_Stop()

        sel = listbox.curselection()
        new_name = robodialogs.mbox("Enter the view name", entry="New View %i" % (len(ListNames) + 1))
        if not new_name:
            return

        index_after = len(ListNames)
        for index in sel:
            index_after = index + 1
            break

        vp = RDK.ViewPose()

        listbox.insert(index_after, new_name)

        ListNames.append(new_name)
        ListPoses.append(vp)

        SaveViews()

        msg = "Recorded view: " + new_name
        RDK.ShowMessage(msg, False)

    def on_ListShow(evtdblclick=None):
        on_Stop()

        sel = listbox.curselection()
        if len(sel) == 0:
            print("Nothing selected")
            return

        index = 0
        for index in sel:
            print(index)
            vp = ListPoses[index]

            strpose = str(robomath.Pose_2_TxyzRxyz(robomath.transl(0, 0, +2000) * vp))[1:-1]
            result = RDK.Command("ViewPoseVR", strpose)

            RDK.setViewPose(vp)

            msg = "Selected view: " + ListNames[index]
            RDK.ShowMessage(msg, False)

            break

    def on_ListNavigateTo(evtdblclick=None):
        on_Stop()

        SaveSettings()  # Force update the fields, as manual entry doesn't trigger the update

        sel = listbox.curselection()
        if len(sel) == 0:
            print("Nothing selected")
            return

        print('Navigating to ' + str(sel))
        view_poses = [ListPoses[i] for i in sel]
        t = threading.Thread(target=NavigateTo, args=(view_poses,))
        t.start()

    def on_ListUp():
        on_Stop()

        sel = listbox.curselection()
        for index in sel:
            print(index)
            if index >= 2:
                oldindex = index
                newindex = index - 1
                ListNames.insert(newindex, ListNames.pop(oldindex))
                ListPoses.insert(newindex, ListPoses.pop(oldindex))

                listbox.delete(oldindex)
                listbox.insert(newindex, ListNames[newindex])

                listbox.select_set(newindex)
            break

        SaveViews()

    def on_ListDown():
        on_Stop()

        sel = listbox.curselection()
        for index in sel:
            print(index)
            if index >= 1 and index < (len(ListNames) - 1):
                oldindex = index
                newindex = index + 1
                ListNames.insert(newindex, ListNames.pop(oldindex))
                ListPoses.insert(newindex, ListPoses.pop(oldindex))

                listbox.delete(oldindex)
                listbox.insert(newindex, ListNames[newindex])

                listbox.select_set(newindex)
            break

        SaveViews()

    #------------------------------------------------
    global STEPS_SIZE
    global WAYPOINTS_DELAY

    steps_size = RDK.getParam("ViewStepsSize")
    if steps_size is not None:
        STEPS_SIZE = float(steps_size)

    waypoints_delay = RDK.getParam("ViewWaypointsDelay")
    if waypoints_delay is not None:
        WAYPOINTS_DELAY = float(waypoints_delay)

    vp_str = RDK.getParam("ViewPose")
    if vp_str is not None:
        vp_xyzabc = ast.literal_eval(vp_str)
        vp = robomath.KUKA_2_Pose(vp_xyzabc)
        ListNames.append(MAIN_VIEW_NAME)
        ListPoses.append(vp)

    strvp_all = RDK.getParam("ViewNames")
    if strvp_all is not None:
        for strvp in strvp_all.split("||"):
            strvp_slt = strvp.split("|")
            if len(strvp) > 1:
                vp_xyzabc = ast.literal_eval(strvp_slt[1])
                if len(vp_xyzabc) >= 6:
                    vp = robomath.KUKA_2_Pose(vp_xyzabc)
                    view_name = strvp_slt[0]
                    print("Loaded view: " + strvp)
                    ListNames.append(view_name)
                    ListPoses.append(vp)

    w = tkinter.Tk()

    w.attributes("-topmost", True)
    w.title("Manage views")
    iconpath = robolink.getPathIcon()
    if os.path.exists(iconpath):
        w.iconbitmap(iconpath)

    w.geometry("200x400")
    w.protocol("WM_DELETE_WINDOW", on_Close)

    listbox = tkinter.Listbox(w, selectmode="extended")

    for i in range(len(ListNames)):
        listbox.insert(i + 1, ListNames[i])

    # Settings
    frame = tkinter.Frame(w)
    frame.pack(fill=tkinter.X, side=tkinter.BOTTOM, expand=True, anchor='n')
    frame.grid_columnconfigure(1, weight=1)

    row = 0
    tkinter.Label(frame, text='Steps size (mm)').grid(column=0, row=row, padx=(0, 15), sticky='w')
    varStepsSize = tkinter.IntVar(value=STEPS_SIZE)
    sbStepsSize = tkinter.Spinbox(frame, textvariable=varStepsSize, from_=0.1, to=999.9, increment=1, format='%0.1f', justify=tkinter.RIGHT, command=SaveSettings)
    sbStepsSize.grid(column=1, row=row, sticky='ew')

    row += 1
    tkinter.Label(frame, text='Waypoint delay (s)').grid(column=0, row=row, padx=(0, 15), sticky='w')
    varWaypointDelay = tkinter.DoubleVar(value=WAYPOINTS_DELAY)
    sbWaypointDelay = tkinter.Spinbox(frame, textvariable=varWaypointDelay, from_=0.0, to=60.0, increment=0.5, justify=tkinter.RIGHT, format='%0.2f', command=SaveSettings)
    sbWaypointDelay.grid(column=1, row=row, sticky='ew')

    # Controls
    btnStop = tkinter.Button(w, text="Stop", command=on_Stop)
    btnStop.pack(fill=tkinter.X, side=tkinter.BOTTOM)

    btnDel = tkinter.Button(w, text="Delete", command=on_ListDelete)
    btnDel.pack(fill=tkinter.X, side=tkinter.BOTTOM)

    btnShow = tkinter.Button(w, text="Down", command=on_ListDown)
    btnShow.pack(fill=tkinter.X, side=tkinter.BOTTOM)

    btnShow = tkinter.Button(w, text="Up", command=on_ListUp)
    btnShow.pack(fill=tkinter.X, side=tkinter.BOTTOM)

    btnRename = tkinter.Button(w, text="Rename", command=on_ListRename)
    btnRename.pack(fill=tkinter.X, side=tkinter.BOTTOM)

    btnRec = tkinter.Button(w, text="Record View", command=on_ListUpdate)
    btnRec.pack(fill=tkinter.X, side=tkinter.BOTTOM)

    btnRec = tkinter.Button(w, text="Add View", command=on_ListAdd)
    btnRec.pack(fill=tkinter.X, side=tkinter.BOTTOM)

    btnGo = tkinter.Button(w, text="Go to view", command=on_ListShow)
    btnGo.pack(fill=tkinter.X, side=tkinter.BOTTOM)

    btnGo = tkinter.Button(w, text="Move to view", command=on_ListNavigateTo)
    btnGo.pack(fill=tkinter.X, side=tkinter.BOTTOM)

    listbox.pack(fill=tkinter.X, side=tkinter.TOP)
    listbox.bind('<Double-Button>', on_ListNavigateTo)  #on_ListShow)

    w.mainloop()

    print("Finished")


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        ViewManager()


if __name__ == '__main__':
    runmain()