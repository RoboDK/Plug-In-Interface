# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# This file let's you edit the settings of this RoboDK App.
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# More information on RoboDK Apps here:
#     https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader
#
# --------------------------------------------

from robodk import robolink, roboapps, robodialogs
import os


class Settings(roboapps.AppSettings):
    """Box Spawner's App Settings"""

    def __init__(self, settings_param='Box-Spawner-Settings'):
        super().__init__(settings_param)

        from collections import OrderedDict
        self._FIELDS_UI = OrderedDict()

        #-----------------------------------------------------
        self.REF_BOX_MM_PATH = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + '/Ref_Box_MM.sld')
        self.REF_BOX_IN_PATH = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + '/Ref_Box_IN.sld')

        self.BOX_ITEM_NAME_MM = 'Box (%ix%ix%i mm)'  # Box (5x5x5 mm)
        self.BOX_ITEM_NAME_IN = 'Box (%ix%ix%i in)'  # Box (5x5x5 in)

        #-----------------------------------------------------
        self._FIELDS_UI['SECTION_SIZE'] = "$SIZE$"
        self._FIELDS_UI['UNITS_TYPE'] = "Box units"
        self.UNITS_TYPE = [0, ['Metric [mm]', 'Imperial [in]']]

        self._FIELDS_UI['BOX_SIZE_XYZ'] = "Box size (x,y,z) [units]"
        self.BOX_SIZE_XYZ = [400., 200., 200.]

        #-----------------------------------------------------
        self._FIELDS_UI['SECTION_SPAWN'] = "$SPAWN$"
        self._FIELDS_UI['SPAWN_FRAME'] = "Spawn location"
        self.SPAWN_FRAME = [0, ['']]

        self._FIELDS_UI['ATTACH_TO_CLOSEST_CONVEYOR'] = "Attach to closest conveyor"
        self._FIELDS_UI['MAX_CONV_DISTANCE'] = "Maximum conveyor distance [mm]"
        self.ATTACH_TO_CLOSEST_CONVEYOR = False
        self.MAX_CONV_DISTANCE = 500.

        #-----------------------------------------------------
        self._FIELDS_UI['SECTION_RANDOM'] = "$RANDOMIZE$"
        self._FIELDS_UI['ENABLE_RANDOM_POSITION'] = "Randomize position"
        self._FIELDS_UI['ENABLE_RANDOM_ORIENTATION'] = "Randomize orientation [deg]"
        self._FIELDS_UI['ENABLE_RANDOM_SIZE'] = "Randomize size"

        self._FIELDS_UI['RANDOM_POSITION'] = "Random position (x,y,z) range (+/-) [mm]"
        self.ENABLE_RANDOM_POSITION = False
        self.RANDOM_POSITION = [50., 50., 0.]

        self._FIELDS_UI['RANDOM_ORIENTATION'] = "Random orientation (rx,ry,rz) range (+/-)"
        self.ENABLE_RANDOM_ORIENTATION = False
        self.RANDOM_ORIENTATION = [0., 0., 5.]

        self._FIELDS_UI['RANDOM_SIZE'] = "Random size range (min, max) [%/100]"
        self.ENABLE_RANDOM_SIZE = False
        self.RANDOM_SIZE = [0.6, 1.]

        self.UpdateFrameList()

    def UpdateFrameList(self, RDK=None):
        if RDK is None:
            RDK = robolink.Robolink()

        frames = [RDK.ActiveStation().Name()] + RDK.ItemList(robolink.ITEM_TYPE_FRAME, True)
        if self.SPAWN_FRAME[1][self.SPAWN_FRAME[0]] not in frames:
            self.SPAWN_FRAME[0] = 0
        self.SPAWN_FRAME[1] = frames

    def ShowUI(self, *args, **kwargs):
        self.UpdateFrameList()
        return super().ShowUI(*args, **kwargs)

    def SetDefaults(self):
        super().SetDefaults()
        self.UpdateFrameList()


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        id = robodialogs.InputDialog("Box Spawner ID", 0)
        if id is None:
            roboapps.Exit()  # User cancelled
        S = Settings('Box-Spawner-Settings-' + str(id))
        S.Load()
        S.ShowUI('Box Spawner Settings (' + str(id) + ')')


if __name__ == '__main__':
    runmain()