import os

from robodk import robolink, roboapps
from pathlib import Path


def AddScript():
    RDK = robolink.Robolink()
    filename = "play_sound"
    scripts = RDK.ItemList(robolink.ITEM_TYPE_PROGRAM_PYTHON, True)
    if filename not in scripts:
        current_folder = Path(__file__).absolute().parent
        file_path = current_folder / f"{filename}.py"
        if not file_path.exists():
            file_path = current_folder.parent / f"{filename}.py"
        if not file_path.exists():
            RDK.ShowMessage("Unable to add the sound script.")
            return
        RDK.AddFile(str(file_path))
    else:
        RDK.ShowMessage("The sound script has already been added to your station.")


def runmain():
    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        AddScript()


if __name__ == '__main__':
    runmain()