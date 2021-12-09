# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
# Note: It is not required to keep a copy of this file, your python script is saved with the station
from robolink import ITEM_TYPE_FRAME, Robolink, getPathIcon  # RoboDK API
import tkinter as tk
import ObjectDeleterTools as odt
import os


class ObjectDeleterEditor:

    SIZE_SPINBOX_FROM = 0.1
    SIZE_SPINBOX_TO = 10000
    SIZE_SPINBOX_INCREMENT = 1
    SIZE_SPINBOX_FORMAT = "%0.2f"
    WIDTH_ENTRY = 32
    STICKY = tk.NSEW

    def __init__(self, RDK=None) -> None:
        self.RDK = RDK
        if self.RDK is None:
            self.RDK = Robolink()

        self.root = tk.Tk()

        self.radius = tk.DoubleVar(value=0)
        self.parent_name_text = tk.StringVar(value=odt.PARENT.Name() if odt.PARENT is not None else 'Unset')

        odt.loadParameters(self.RDK)

        self.init()

    def init(self):

        self.radius.set(odt.RADIUS)
        self.parent_name_text.set(odt.PARENT.Name() if odt.PARENT is not None else 'Unset')

    def setRadius(self):
        odt.RADIUS = self.radius.get()

    def selectParent(self):
        self.RDK.setSelection([])
        choices = self.RDK.ItemList(ITEM_TYPE_FRAME)
        choices.append(self.RDK.ActiveStation())
        parent = self.RDK.ItemUserPick('Select Deleter location', choices)
        if parent is not None and parent.Valid():
            odt.PARENT = parent
            self.parent_name_text.set(odt.PARENT.Name())

    def saveAndClose(self):
        self.setRadius()
        odt.setParameters(self.RDK)
        self.root.destroy()

    def loadDefaults(self):
        odt.loadDefaults()
        self.init()

    def show(self):

        # Generate the main window
        frame = tk.Frame(self.root)
        frame.pack(side=tk.TOP, fill=tk.X, padx=1, pady=1)
        row = -1

        # Radius
        row += 1
        l_radius = tk.Label(frame, text='Radius (mm)', anchor='w')
        sb_radius = tk.Spinbox(
            frame,
            textvariable=self.radius,
            from_=self.SIZE_SPINBOX_FROM,
            to=self.SIZE_SPINBOX_TO,
            increment=self.SIZE_SPINBOX_INCREMENT,
            format=self.SIZE_SPINBOX_FORMAT,
            command=self.setRadius,
        )

        l_radius.grid(column=0, columnspan=1, row=row, sticky=self.STICKY)
        sb_radius.grid(column=1, columnspan=3, row=row, sticky=self.STICKY)

        # Delete location
        row += 1
        l_parent = tk.Label(frame, text='Location (Item)', anchor='w')
        e_parent = tk.Entry(frame, textvariable=self.parent_name_text, state='readonly', width=self.WIDTH_ENTRY)
        b_parent = tk.Button(frame, text='Select', command=self.selectParent, padx=1, pady=1)

        l_parent.grid(column=0, columnspan=1, row=row, sticky=self.STICKY)
        e_parent.grid(column=1, columnspan=1, row=row, sticky=self.STICKY)
        b_parent.grid(column=2, columnspan=2, row=row, sticky=self.STICKY, padx=1, pady=1)

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
        window_title = "Object Deleter Editor"
        self.root.title(window_title)

        # Logo
        icon_path = getPathIcon()
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

        self.root.resizable(0, 0)
        self.root.mainloop()


if __name__ == "__main__":
    ObjectDeleterEditor().show()