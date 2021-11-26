# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
# Note: It is not required to keep a copy of this file, your python script is saved with the station
from robolink import ITEM_TYPE_FRAME, Robolink, getPathIcon  # RoboDK API
import tkinter as tk
import SpawnBoxTools as sbt
import os

#------ UI PARAMETERS ------#

SIZE_SPINBOX_FROM = 0.1  # mm or in
SIZE_SPINBOX_TO = 10000  # mm or in
SIZE_SPINBOX_INCREMENT = 0.5  # mm or in
STICKY = tk.NSEW


#------ UI FUNCTIONS ------#
def switchUnitsFormat(toggle=True):
    global units_format

    if toggle:
        sbt.USE_METRIC = not sbt.USE_METRIC

    units_format = '(mm)' if sbt.USE_METRIC else '(in)'

    if 'l_boxlength_text' in globals():
        l_boxlength_text.set('Box Length ' + units_format)
        l_boxwidth_text.set('Box Width ' + units_format)
        l_boxheight_text.set('Box Height ' + units_format)


def setBoxDimensions():
    sbt.BOX_SIZE_XYZ[0] = box_length.get()
    sbt.BOX_SIZE_XYZ[1] = box_width.get()
    sbt.BOX_SIZE_XYZ[2] = box_height.get()


def selectParent():
    global e_parentname_text
    RDK.setSelection([])
    choices = [RDK.ActiveStation()]
    choices.extend(RDK.ItemList(ITEM_TYPE_FRAME))
    parent = RDK.ItemUserPick('Select spawning location', choices)
    if parent is not None and parent.Valid():
        sbt.PARENT = parent
        e_parentname_text.set(sbt.PARENT.Name())


def selectConvParent():
    global e_convparentname_text
    RDK.setSelection([])
    conv_parent = RDK.ItemUserPick('Select conveyor relocation', ITEM_TYPE_FRAME)
    if conv_parent is not None and conv_parent.Valid():
        sbt.CONV_PARENT = conv_parent
        e_convparentname_text.set(sbt.CONV_PARENT.Name())


def clearConvParent():
    global e_convparentname_text
    sbt.CONV_PARENT = None
    e_convparentname_text.set('Unset')


def saveAndClose():
    global root
    setBoxDimensions()  # This is not called if user entered manually
    sbt.setParameters(RDK)
    root.destroy()


#------ UI PROGRAM ------#

RDK = Robolink()

sbt.loadParameters(RDK)

switchUnitsFormat(False)

# Generate the main window
root = tk.Tk()
frame = tk.Frame(root)
frame.pack(side=tk.TOP, fill=tk.X, padx=1, pady=1)
row = -1

# Unit selection
row += 1
l_boxunits = tk.Label(frame, text='Units', anchor='w')

unit_options = tk.StringVar(value=units_format)
rb_box_units_mm = tk.Radiobutton(frame, text='mm', variable=unit_options, value='(mm)', command=switchUnitsFormat)
rb_box_units_in = tk.Radiobutton(frame, text='in', variable=unit_options, value='(in)', command=switchUnitsFormat)

l_boxunits.grid(column=0, row=row, sticky=STICKY)
rb_box_units_mm.grid(column=1, columnspan=1, row=row, sticky=tk.NW)
rb_box_units_in.grid(column=2, columnspan=3, row=row, sticky=tk.NW)

# Box length (x)
row += 1
l_boxlength_text = tk.StringVar(value='Box Length ' + units_format)
l_boxlength = tk.Label(frame, textvariable=l_boxlength_text, anchor='w')

box_length = tk.DoubleVar(value=sbt.BOX_SIZE_XYZ[0])
e_boxlenght = tk.Spinbox(frame, textvariable=box_length, from_=SIZE_SPINBOX_FROM, to=SIZE_SPINBOX_TO, increment=SIZE_SPINBOX_INCREMENT, command=setBoxDimensions)

l_boxlength.grid(column=0, columnspan=1, row=row, sticky=STICKY)
e_boxlenght.grid(column=1, columnspan=3, row=row, sticky=STICKY)

# Box width (y)
row += 1
l_boxwidth_text = tk.StringVar(value='Box Width ' + units_format)
l_boxwidth = tk.Label(frame, textvariable=l_boxwidth_text, anchor='w')

box_width = tk.DoubleVar(value=sbt.BOX_SIZE_XYZ[1])
e_boxwidth = tk.Spinbox(frame, textvariable=box_width, from_=SIZE_SPINBOX_FROM, to=SIZE_SPINBOX_TO, increment=SIZE_SPINBOX_INCREMENT, command=setBoxDimensions)

l_boxwidth.grid(column=0, columnspan=1, row=row, sticky=STICKY)
e_boxwidth.grid(column=1, columnspan=3, row=row, sticky=STICKY)

# Box height (z)
row += 1
l_boxheight_text = tk.StringVar(value='Box Height ' + units_format)
l_boxheight = tk.Label(frame, textvariable=l_boxheight_text, anchor='w')

box_height = tk.DoubleVar(value=sbt.BOX_SIZE_XYZ[2])
e_boxheight = tk.Spinbox(frame, textvariable=box_height, from_=SIZE_SPINBOX_FROM, to=SIZE_SPINBOX_TO, increment=SIZE_SPINBOX_INCREMENT, command=setBoxDimensions)

l_boxheight.grid(column=0, columnspan=1, row=row, sticky=STICKY)
e_boxheight.grid(column=1, columnspan=3, row=row, sticky=STICKY)

# Spawn location
row += 1
l_parent = tk.Label(frame, text='Spawn location (Item)', anchor='w')

e_parentname_text = tk.StringVar(value=sbt.PARENT.Name() if sbt.PARENT is not None else 'Unset')
e_parent = tk.Entry(frame, textvariable=e_parentname_text, state='readonly')

b_parent = tk.Button(frame, text='Select', command=selectParent)

l_parent.grid(column=0, columnspan=1, row=row, sticky=STICKY)
e_parent.grid(column=1, columnspan=1, row=row, sticky=STICKY)
b_parent.grid(column=2, columnspan=2, row=row, sticky=STICKY)

# Conveyor remap
row += 1
l_convparent = tk.Label(frame, text='Conveyor relocation (Item)', anchor='w')

e_convparentname_text = tk.StringVar(value=sbt.CONV_PARENT.Name() if sbt.CONV_PARENT is not None else 'Unset')
e_convparent = tk.Entry(frame, textvariable=e_convparentname_text, state='readonly')

b_convparent = tk.Button(frame, text='Select', command=selectConvParent)
b_convparent_clr = tk.Button(frame, text='Clear', command=clearConvParent)

l_convparent.grid(column=0, columnspan=1, row=row, sticky=STICKY)
e_convparent.grid(column=1, columnspan=1, row=row, sticky=STICKY)
b_convparent.grid(column=2, columnspan=1, row=row, sticky=STICKY)
b_convparent_clr.grid(column=3, columnspan=1, row=row, sticky=STICKY)

# User controls
control_row = tk.Frame(root)

# Creating the OK button
b_ok = tk.Button(control_row, text='OK', command=saveAndClose, width=12)
b_ok.pack(side=tk.LEFT, padx=5, pady=5)

# Creating the Cancel button
b_cancel = tk.Button(control_row, text='Cancel', command=root.destroy, width=12)
b_cancel.pack(side=tk.LEFT, padx=5, pady=5)

# Creating the Default button
b_defaults = tk.Button(control_row, text='Defaults', command=sbt.loadDefaults, width=12)
b_defaults.pack(side=tk.LEFT, padx=5, pady=5)

control_row.pack(side=tk.BOTTOM, fill=tk.X, padx=1, pady=1)

# Set window name
window_title = "Box Spawner Editor"
root.title(window_title)

# Logo
icon_path = getPathIcon()
if os.path.exists(icon_path):
    root.iconbitmap(icon_path)

# We can embed the window into RoboDK as a docked window
# Make sure the window title is unique
#EmbedWindow(window_title, size_w=200, area_add=2)

root.mainloop()