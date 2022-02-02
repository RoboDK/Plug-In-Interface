# This script allows you to take snapshots

from robodk.robolink import *
from robodk.robodialogs import *
import datetime

RDK = Robolink()

#date_str = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
date_str = datetime.datetime.now().strftime("%H-%M-%S")
path_rdk = RDK.getParam('PATH_OPENSTATION')
file_name = "RoboDK-Screenshot-" + date_str + ".png"

file_path = getSaveFileName(path_preference=path_rdk, strfile=file_name, defaultextension='.png', filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")])
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
