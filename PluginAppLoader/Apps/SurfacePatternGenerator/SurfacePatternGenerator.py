# The Surface Pattern Generator (SPG) App let's you generate surface patterns on an object surface, with its associated Curve Follow Project (CFP).
#
# Type help("robodk.robolink") or help("robodk.robomath") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html

from robodk import robolink, roboapps
from _spgtools import *

# Optionally provide a part name to auto select it without asking the user
PART_NAME = None  # 'Paint Part'


def runmain():

    #---------------------------------------------
    class SurfaceSettings(roboapps.AppSettings):

        from collections import OrderedDict
        __FIELDS_UI = OrderedDict()

        __FIELDS_UI['SIZE_X'] = "Size along X (mm)"
        __FIELDS_UI['SIZE_Y'] = "Size along Y (mm)"
        SIZE_X = 500.0
        SIZE_Y = 500.0

        __FIELDS_UI['STEP_X'] = "Step along X (mm)"
        __FIELDS_UI['STEP_Y'] = "Step along Y (mm)"
        STEP_X = 20.0
        STEP_Y = 50.0

        __FIELDS_UI['ANGLE_TRIANGLE'] = "Triangular path (deg)"
        ANGLE_TRIANGLE = 0.0

        __FIELDS_UI['COVER_ALL'] = "Cover all surface"
        __FIELDS_UI['EVEN_DISTRIBUTION'] = "Distribute lines evenly"
        __FIELDS_UI['CONTINUOUS'] = "Connect lines"
        COVER_ALL = False
        EVEN_DISTRIBUTION = False
        CONTINUOUS = True

        __FIELDS_UI['REPEAT_TIMES'] = "Repeat times"
        __FIELDS_UI['REPEAT_OFFSET'] = "Repeat Offset along Z (mm)"
        REPEAT_TIMES = 1
        REPEAT_OFFSET = 2.0

        __FIELDS_UI['ANGLE_TCP_X'] = "Tool angle X (deg)"
        __FIELDS_UI['ANGLE_TCP_Y'] = "Tool angle Y (deg)"
        ANGLE_TCP_X = 0.0
        ANGLE_TCP_Y = 0.0

        __FIELDS_UI['SPEED_OPERATION'] = "Operation speed (mm/s)"
        SPEED_OPERATION = 20.0

        def __init__(self):
            super(SurfaceSettings, self).__init__('Surface-Settings')
            self._FIELDS_UI = self.__FIELDS_UI

        def SetDefaults(self):
            defaults = SurfaceSettings()
            self.CopyFrom(defaults)

        def ShowUI(self):

            def update_pattern():
                self._UI_READ_FIELDS()
                for REF in REF_PATTERN_LIST:
                    new_obj = CreatePaths(REF, PART, self.SIZE_X, self.SIZE_Y, self.STEP_X, self.STEP_Y, self.REPEAT_TIMES, self.REPEAT_OFFSET, self.COVER_ALL, self.EVEN_DISTRIBUTION, self.CONTINUOUS, self.ANGLE_TRIANGLE)

                if True:
                    update_prog()

            def update_prog():
                prog_name_list = []
                for REF in REF_PATTERN_LIST:
                    prog = CreateProgram(REF, self.SPEED_OPERATION, self.ANGLE_TCP_X, self.ANGLE_TCP_Y)

                    if prog is not None and prog.Valid():
                        prog_name_list.append(prog.Name())

                CreateMainProgram(PART, prog_name_list)

            windowtitle = PART.Name()

            if not roboapps.ENABLE_QT:

                def custom_frame(w):

                    def set_defaults():
                        w.destroy()
                        self.SetDefaults()
                        self.ShowUI()

                    import tkinter as tk
                    row = tk.Frame(w)
                    b_defaults = tk.Button(row, text='Set defaults', command=set_defaults, width=8)
                    b_defaults.pack(side=tk.LEFT, padx=5, pady=5)
                    b_update = tk.Button(row, text='Update Pattern', command=update_pattern, width=8)
                    b_update.pack(side=tk.LEFT, padx=5, pady=5)
                    row.pack(side=tk.TOP, fill=tk.X, padx=1, pady=1)

            else:

                from PySide2 import QtWidgets

                def custom_frame(w: QtWidgets.QWidget):

                    def set_defaults():
                        w.window().close()
                        w.deleteLater()
                        self.SetDefaults()
                        self.ShowUI()

                    layout = w.layout()

                    b_default = QtWidgets.QPushButton('Set defaults')
                    b_default.clicked.connect(set_defaults)
                    b_update = QtWidgets.QPushButton('Update Pattern')
                    b_update.clicked.connect(update_pattern)

                    layout.addWidget(b_default)
                    layout.addWidget(b_update)

            super(SurfaceSettings, self).ShowUI(windowtitle=windowtitle, callback_frame=custom_frame)

    #---------------------------------------------
    # Initialize the RoboDK API
    RDK = robolink.Robolink()

    #---------------------------------------------
    # First: Retrieve the part item
    if not RDK.ItemList(robolink.ITEM_TYPE_OBJECT, True):
        RDK.ShowMessage("A least one object is required for projection. Please add an Object.")
        quit()

    PART = None
    if PART_NAME is None:
        RDK.setSelection([])
        PART = RDK.ItemUserPick("Select a part", robolink.ITEM_TYPE_OBJECT)
        if not PART.Valid():
            ShowMsg("Operation cancelled by user")
            quit()
    else:
        PART = RDK.Item(PART_NAME, robolink.ITEM_TYPE_OBJECT)
        if not PART.Valid():
            raise Exception("The selected part is not valid or not available")

    #---------------------------------------------
    # List all the reference frames that we want to use to create
    # raster paths (references attached to the object reference
    part_ref = PART.Parent()

    # Get the list of items attached to the part reference
    ref_pattern_candidates = part_ref.Childs()

    # Iterate through these child items and list the reference frames
    # Optionally add ignore in the name
    REF_PATTERN_LIST = []
    for ref_i in ref_pattern_candidates:
        if ref_i.Type() == robolink.ITEM_TYPE_FRAME and (not "ignore" in ref_i.Name()):
            REF_PATTERN_LIST.append(ref_i)

    if len(REF_PATTERN_LIST) <= 0:
        RDK.ShowMessage("No reference frames found. Add one or more frames to " + part_ref.Name())
        quit()

    #---------------------------------------------
    # Load GUI tools
    S = SurfaceSettings()
    S.Load()
    S.ShowUI()


if __name__ == "__main__":
    runmain()