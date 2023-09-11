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

from robodk import roboapps


class Settings(roboapps.AppSettings):
    """
    Curve Utilities Settings
    """

    def __init__(self, settings_param='Curve-Utilities-Settings'):
        super().__init__(settings_param)

        from collections import OrderedDict
        self._FIELDS_UI = OrderedDict()

        #----------------------------------------------------------
        self._FIELDS_UI['SECTION_SIMPLIFY_CURVE'] = "$SIMPLIFY CURVE$"

        self._FIELDS_UI['SIMPLIFY_INPLACE'] = "Replace original curve (not reversible)"
        self.SIMPLIFY_INPLACE = False

        self._FIELDS_UI['SIMPLIFY_PROJECT_POINT'] = "Project points on surface (XYZ)"
        self.SIMPLIFY_PROJECT_POINT = False

        self._FIELDS_UI['SIMPLIFY_RECALC_NORMAL'] = "Recalculate point normal according to surface normal (IJK)"
        self.SIMPLIFY_RECALC_NORMAL = False

        self._FIELDS_UI['SIMPLIFY_PROJECT_ALONG_NORMAL'] = "Project along current normal"
        self.SIMPLIFY_PROJECT_ALONG_NORMAL = True

        self._FIELDS_UI['SIMPLIFY_SORT'] = "Sort segments (make continuous)"
        self.SIMPLIFY_SORT = True

        self._FIELDS_UI['SIMPLIFY_REVERSE'] = "Fix reversed segments when sorting"
        self.SIMPLIFY_REVERSE = True

        self._FIELDS_UI['SIMPLIFY_MERGE'] = "Merge segments into one curve"
        self.SIMPLIFY_MERGE = True

        self._FIELDS_UI['SIMPLIFY_DUPLICATES'] = "Remove duplicated points"
        self.SIMPLIFY_DUPLICATES = True

        self._FIELDS_UI['SIMPLIFY_COMPARE_NORMALS'] = "Include normals when comparing points"
        self.SIMPLIFY_COMPARE_NORMALS = True

        self._FIELDS_UI['SIMPLIFY_STRAIGHT_LINES'] = "Remove intermediary points along straight lines"
        self.SIMPLIFY_STRAIGHT_LINES = True

        self._FIELDS_UI['SIMPLIFY_TOLERANCE_POINT'] = "Point distance tolerance [mm]"
        self.SIMPLIFY_TOLERANCE_POINT = 0.002

        self._FIELDS_UI['SIMPLIFY_TOLERANCE_NORMALS'] = "Point normal tolerance [rad]"
        self.SIMPLIFY_TOLERANCE_NORMALS = 0.01

        self._FIELDS_UI['SIMPLIFY_TOLERANCE_STRAIGHT_LINE'] = "Straight line tolerance [rad]"
        self.SIMPLIFY_TOLERANCE_STRAIGHT_LINE = 0.02

        #----------------------------------------------------------
        self._FIELDS_UI['SECTION_SPLIT'] = "$Split Discontinuous Curves$"

        self._FIELDS_UI['SPLIT_TOLERANCE'] = "Split tolerance [mm]"
        self.SPLIT_TOLERANCE = 50.0

        #----------------------------------------------------------
        self._FIELDS_UI['SECTION_CURVE_TO_TARGETS'] = "$Curve to targets$"

        self._FIELDS_UI['TARGET_INVERSE_NORMAL'] = "Inverse point normal"
        self.TARGET_INVERSE_NORMAL = True

        #----------------------------------------------------------
        self._FIELDS_UI['SECTION_SVG'] = "$SVG TO CURVE$"

        self._FIELDS_UI['SVG_SIZE'] = "Size of the imported SVG (w, h) [mm]"
        self.SVG_SIZE = (1000.0, 1000.0)

        self._FIELDS_UI['SVG_STEP'] = "Step size [mm]"
        self.SVG_STEP = 2.0

        self._FIELDS_UI['SVG_KEEP_SMALLER_STEP'] = "Keep segments smaller that the step size"
        self.SVG_KEEP_SMALLER_STEP = True

        self._FIELDS_UI['SVG_INVERT_NORMAL'] = "Invert normals (Z-)"
        self.SVG_INVERT_NORMAL = False

        self._FIELDS_UI['SVG_CENTER_OBJECT_FRAME'] = "Center object reference"
        self.SVG_CENTER_OBJECT_FRAME = False

        self._FIELDS_UI['SVG_AS_POINTS'] = "Import as points instead of curves"
        self.SVG_AS_POINTS = False

        self._FIELDS_UI['SVG_DEFAULT_COLOR'] = "Default color (r, g, b) [0-255]"
        self.SVG_DEFAULT_COLOR = [255, 255, 255]

        self._FIELDS_UI['SVG_IMPORT_COLOR'] = "Import colors from styling"
        self.SVG_IMPORT_COLOR = True

        self._FIELDS_UI['SVG_STROKE_OVER_FILL_COLOR'] = "Use stroke color over fill color"
        self.SVG_STROKE_OVER_FILL_COLOR = True


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        S = Settings()
        S.Load()
        S.ShowUI('Curve Utilities Settings')


if __name__ == '__main__':
    runmain()