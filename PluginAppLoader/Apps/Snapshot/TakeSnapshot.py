# This script allows you to take snapshots

from robodk import *
from robolink import *
import datetime

from tkinter import *
from tkinter import filedialog


RDK = Robolink()

#date_str = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
date_str = datetime.datetime.now().strftime("%H-%M-%S")
path_rdk = RDK.getParam('PATH_OPENSTATION')
file_name = "RoboDK-Screenshot-" + date_str + ".png"

root = Tk()
root.withdraw()
types = (("PNG files","*.png"),("JPEG files","*.jpg"),("All files","*.*"))
file_path = filedialog.asksaveasfilename(title = "Select image file to save", defaultextension = types, filetypes = types, initialdir=path_rdk, initialfile=file_name)
if not file_path:
    print("Operation cancelled")
    quit()

print("Saving image to: " + file_path)

cmd = "Snapshot"
#cmd = "SnapshotWhite" # Snapshot with white background
#cmd = "SnapshotWhiteNoTextNoFrames" # Snapshot with white background, no text or coordinate systems


returned = RDK.Command(cmd, file_path)
print(returned)
RDK.ShowMessage("Snapshot saved: " + file_path, False)




