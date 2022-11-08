from robodk import robolink, robodialogs, roboapps
import os

ACTION_NAME = os.path.basename(__file__)


def ReplaceObjects(objects=None):
    """Action to perform when the action is clicked in RoboDK."""

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

    Example for a 'Checkable Action':

    .. code-block:: python

        def runmain():
            if roboapps.Unchecked():
                ActionUnchecked()
            else:
                roboapps.SkipKill()  # Optional, prevents RoboDK from force-killing the action after 2 seconds
                ActionChecked()

    Example for a 'Momentary Action':

    .. code-block:: python

        def runmain():
            if roboapps.Unchecked():
                roboapps.Exit()  # or sys.exit()
            else:
                roboapps.SkipKill()  # Optional, prevents RoboDK from force-killing the action after 2 seconds
                ActionChecked()

    Example for a 'Checkable Option':

    .. code-block:: python

        def runmain():
            if roboapps.Unchecked():
                ActionUnchecked()
            else:
                roboapps.KeepChecked()  # Important, prevents RoboDK from unchecking the action after it has completed
                ActionChecked()

    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        ReplaceObjects()


if __name__ == '__main__':
    runmain()