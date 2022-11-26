# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Replace object(s) with another object from the disk (prompts user).
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


def ReplaceObjects(objects=None):
    """
    Replace object(s) with another object from the disk (prompts user).
    """

    # Get the objects: from specified list, user selection (context-menu) or prompt (action)
    RDK = robolink.Robolink()
    if objects is None:
        objects = [x for x in RDK.Selection() if x.Type() in [robolink.ITEM_TYPE_OBJECT]]
        if not objects:
            objects = RDK.ItemUserPick('Select the object to replace', robolink.ITEM_TYPE_OBJECT)
            if not objects.Valid():
                return
            objects = [objects]
    else:
        objects = [x for x in objects if x.Type() in [robolink.ITEM_TYPE_OBJECT]]
        if not objects:
            return

    # Get the replacement object
    objects_ext = ['.sld', '.stl', '.iges', '.igs', '.step', '.stp', '.obj', '.slp', '.3ds', '.dae', '.blend', '.wrl', '.wrml']
    replacement_path = robodialogs.getOpenFileName(strtitle='Replacing object. Select new object...', defaultextension='.sld', filetypes=[('Object', '.sld'), ('3D Object', ' '.join(objects_ext))])
    if not replacement_path or not os.path.exists(replacement_path):
        return

    # Turn off render to hide operations and speed-up the process
    RDK.Render(False)

    # Import the replacement once and copy
    replacement_item = RDK.AddFile(replacement_path, 0)
    if not replacement_item.Valid():
        return
    replacement_item.Copy()

    # Replace objects
    for object_item in objects:
        object_links = object_item.getLinks(None)
        _object_item = object_item.Parent().Paste()
        _object_item.setPose(object_item.Pose())
        object_item.Delete()

        for object_link in object_links:
            try:
                object_link.setLink(_object_item)
            except:
                pass

    # Delete initial copy
    replacement_item.Delete()

    # Turn render back on
    RDK.Render(True)


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        ReplaceObjects()


if __name__ == '__main__':
    runmain()