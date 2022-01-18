# Type help("robodk.robolink") or help("robodk.robomath") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
# Note: It is not required to keep a copy of this file, your python script is saved with the station
from robodk.robolink import ITEM_TYPE_FRAME, Robolink, getPathIcon  # RoboDK API
import tkinter as tk
import SpawnBoxTools as sbt
import os


class SpawnBoxEditor:

    SIZE_SPINBOX_FROM = 0.1
    SIZE_SPINBOX_TO = 10000
    SIZE_SPINBOX_INCREMENT = 0.5
    SIZE_SPINBOX_FORMAT = "%0.2f"
    WIDTH_ENTRY = 32
    STICKY = tk.NSEW

    def __init__(self, RDK=None) -> None:
        self.RDK = RDK
        if self.RDK is None:
            self.RDK = Robolink()

        self.root = tk.Tk()

        self.unit_options = tk.IntVar()
        self.units_format = ''

        self.box_length = tk.DoubleVar(value=0)
        self.box_width = tk.DoubleVar(value=0)
        self.box_height = tk.DoubleVar(value=0)

        self.box_length_text = tk.StringVar(value='')
        self.box_width_text = tk.StringVar(value='')
        self.box_height_text = tk.StringVar(value='')

        self.parent_name_text = tk.StringVar(value='')
        self.conv_parent_name_text = tk.StringVar(value='')

        sbt.loadParameters(self.RDK)

        self.init()

    def init(self):
        self.unit_options.set(int(sbt.USE_METRIC))
        self.units_format = '(mm)' if sbt.USE_METRIC else '(in)'

        self.box_length.set(sbt.BOX_SIZE_XYZ[0])
        self.box_width.set(sbt.BOX_SIZE_XYZ[1])
        self.box_height.set(sbt.BOX_SIZE_XYZ[2])

        self.box_length_text.set('Box Length ' + self.units_format)
        self.box_width_text.set('Box Width ' + self.units_format)
        self.box_height_text.set('Box Height ' + self.units_format)

        self.parent_name_text.set(sbt.PARENT.Name() if sbt.PARENT is not None else 'Unset')
        self.conv_parent_name_text.set(sbt.CONV_PARENT.Name() if sbt.CONV_PARENT is not None else 'Unset')

    def switchUnitsFormat(self):

        use_metric = self.unit_options.get() == 1

        if use_metric != sbt.USE_METRIC:
            # Convert units
            factor = 25.4  # in to mm
            if sbt.USE_METRIC and not use_metric:
                factor = 1 / 25.4  # mm to in

            self.box_length.set(self.box_length.get() * factor)
            self.box_width.set(self.box_width.get() * factor)
            self.box_height.set(self.box_height.get() * factor)

        sbt.USE_METRIC = use_metric

    def setBoxDimensions(self):
        sbt.BOX_SIZE_XYZ[0] = self.box_length.get()
        sbt.BOX_SIZE_XYZ[1] = self.box_width.get()
        sbt.BOX_SIZE_XYZ[2] = self.box_height.get()

    def selectParent(self):
        self.RDK.setSelection([])
        choices = self.RDK.ItemList(ITEM_TYPE_FRAME)
        choices.append(self.RDK.ActiveStation())
        parent = self.RDK.ItemUserPick('Select spawning location', choices)
        if parent is not None and parent.Valid():
            sbt.PARENT = parent
            self.parent_name_text.set(sbt.PARENT.Name())

    def selectConvParent(self):
        self.RDK.setSelection([])
        conv_parent = self.RDK.ItemUserPick('Select conveyor relocation', ITEM_TYPE_FRAME)
        if conv_parent is not None and conv_parent.Valid():
            sbt.CONV_PARENT = conv_parent
            self.conv_parent_name_text.set(sbt.CONV_PARENT.Name())

    def clearConvParent(self):
        sbt.CONV_PARENT = None
        self.conv_parent_name_text.set('Unset')

    def saveAndClose(self):
        self.setBoxDimensions()  # This is not called if user entered manually
        sbt.setParameters(self.RDK)
        self.root.destroy()

    def loadDefaults(self):
        sbt.loadDefaults()
        self.init()

    def show(self):

        # Generate the main window
        frame = tk.Frame(self.root)
        frame.pack(side=tk.TOP, fill=tk.X, padx=1, pady=1)
        row = -1

        # Unit selection
        row += 1
        l_units = tk.Label(frame, text='Units', anchor='w')
        rb_box_units_mm = tk.Radiobutton(frame, text='mm', variable=self.unit_options, value=1, command=self.switchUnitsFormat)
        rb_box_units_in = tk.Radiobutton(frame, text='in', variable=self.unit_options, value=0, command=self.switchUnitsFormat)

        l_units.grid(column=0, row=row, sticky=self.STICKY)
        rb_box_units_mm.grid(column=1, columnspan=1, row=row, sticky=tk.NW)
        rb_box_units_in.grid(column=2, columnspan=3, row=row, sticky=tk.NW)

        # Box length (x)
        row += 1
        l_box_length = tk.Label(frame, textvariable=self.box_length_text, anchor='w')
        sb_box_length = tk.Spinbox(
            frame,
            textvariable=self.box_length,
            from_=self.SIZE_SPINBOX_FROM,
            to=self.SIZE_SPINBOX_TO,
            increment=self.SIZE_SPINBOX_INCREMENT,
            format=self.SIZE_SPINBOX_FORMAT,
            command=self.setBoxDimensions,
        )

        l_box_length.grid(column=0, columnspan=1, row=row, sticky=self.STICKY)
        sb_box_length.grid(column=1, columnspan=3, row=row, sticky=self.STICKY)

        # Box width (y)
        row += 1
        l_box_width = tk.Label(frame, textvariable=self.box_width_text, anchor='w')
        sb_box_width = tk.Spinbox(
            frame,
            textvariable=self.box_width,
            from_=self.SIZE_SPINBOX_FROM,
            to=self.SIZE_SPINBOX_TO,
            increment=self.SIZE_SPINBOX_INCREMENT,
            format=self.SIZE_SPINBOX_FORMAT,
            command=self.setBoxDimensions,
        )

        l_box_width.grid(column=0, columnspan=1, row=row, sticky=self.STICKY)
        sb_box_width.grid(column=1, columnspan=3, row=row, sticky=self.STICKY)

        # Box height (z)
        row += 1
        l_box_height = tk.Label(frame, textvariable=self.box_height_text, anchor='w')
        sb_box_height = tk.Spinbox(
            frame,
            textvariable=self.box_height,
            from_=self.SIZE_SPINBOX_FROM,
            to=self.SIZE_SPINBOX_TO,
            increment=self.SIZE_SPINBOX_INCREMENT,
            format=self.SIZE_SPINBOX_FORMAT,
            command=self.setBoxDimensions,
        )

        l_box_height.grid(column=0, columnspan=1, row=row, sticky=self.STICKY)
        sb_box_height.grid(column=1, columnspan=3, row=row, sticky=self.STICKY)

        # Spawn location
        row += 1
        l_parent = tk.Label(frame, text='Spawn location (Item)', anchor='w')
        e_parent = tk.Entry(frame, textvariable=self.parent_name_text, state='readonly', width=self.WIDTH_ENTRY)
        b_parent = tk.Button(frame, text='Select', command=self.selectParent)

        l_parent.grid(column=0, columnspan=1, row=row, sticky=self.STICKY)
        e_parent.grid(column=1, columnspan=1, row=row, sticky=self.STICKY)
        b_parent.grid(column=2, columnspan=2, row=row, sticky=self.STICKY, padx=1, pady=1)

        # Conveyor remap
        row += 1
        l_conv_parent = tk.Label(frame, text='Conveyor relocation (Item)', anchor='w')
        e_conv_parent = tk.Entry(frame, textvariable=self.conv_parent_name_text, state='readonly', width=self.WIDTH_ENTRY)
        b_conv_parent = tk.Button(frame, text='Select', command=self.selectConvParent)
        b_conv_parent_clr = tk.Button(frame, text='Clear', command=self.clearConvParent)

        l_conv_parent.grid(column=0, columnspan=1, row=row, sticky=self.STICKY)
        e_conv_parent.grid(column=1, columnspan=1, row=row, sticky=self.STICKY)
        b_conv_parent.grid(column=2, columnspan=1, row=row, sticky=self.STICKY, padx=1, pady=1)
        b_conv_parent_clr.grid(column=3, columnspan=1, row=row, sticky=self.STICKY, padx=1, pady=1)

        # User controls
        control_row = tk.Frame(self.root)
        control_row.pack(side=tk.BOTTOM, padx=1, pady=1)

        # Creating the OK button
        b_ok = tk.Button(control_row, text='OK', command=self.saveAndClose, width=12)
        b_ok.grid(column=0, row=0, sticky=self.STICKY, padx=1, pady=1)

        # Creating the Cancel button
        b_cancel = tk.Button(control_row, text='Cancel', command=self.root.destroy, width=12)
        b_cancel.grid(column=1, row=0, sticky=self.STICKY, padx=1, pady=1)

        # Creating the Default button
        b_defaults = tk.Button(control_row, text='Defaults', command=self.loadDefaults, width=12)
        b_defaults.grid(column=2, row=0, sticky=self.STICKY, padx=1, pady=1)

        # Set window name
        window_title = "Box Spawner Editor"
        self.root.title(window_title)

        # Logo
        icon_path = getPathIcon()
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

        self.root.resizable(0, 0)
        self.root.mainloop()


if __name__ == "__main__":
    SpawnBoxEditor().show()