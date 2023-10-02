# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# This file lets you edit the settings of this RoboDK App.
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


def rgba2hex(r, g, b, a):
    return '#{:02x}{:02x}{:02x}{:02x}'.format(a, r, g, b).upper()


def rgba2f(r, g, b, a):
    return [x / 255. for x in [r, g, b, a]]


class Settings(roboapps.AppSettings):
    """Set Style's App Settings"""

    def __init__(self, settings_param='Set-Style-Settings'):
        super().__init__(settings_param)

        from collections import OrderedDict
        self._FIELDS_UI = OrderedDict()

        #-----------------------------------------------------
        self._FIELDS_UI['SECTION_POINTS'] = "$POINTS$"

        # Points cloud
        self._FIELDS_UI['POINTS_CLOUD_COLOR'] = "Point cloud color (r,g,b,a)"
        self._FIELDS_UI['POINTS_CLOUD_SIZE'] = "Point cloud size [mm]"
        self.POINTS_CLOUD_COLOR = [119, 17, 17, 255]  # "#FF771111"
        self.POINTS_CLOUD_SIZE = 4.

        # Spheres
        self._FIELDS_UI['POINTS_SPHERE_COLOR'] = "Sphere color (r,g,b,a)"
        self._FIELDS_UI['POINTS_SPHERE_SIZE'] = "Sphere size [mm]"
        self._FIELDS_UI['POINTS_SPHERE_RINGS'] = "Sphere resolution"
        self.POINTS_SPHERE_COLOR = [255, 255, 255, 255]  # "#FFFFFFFF"
        self.POINTS_SPHERE_SIZE = 10.
        self.POINTS_SPHERE_RINGS = 8

        # Cubes
        self._FIELDS_UI['POINTS_CUBE_COLOR'] = "Cube color (r,g,b,a)"
        self._FIELDS_UI['POINTS_CUBE_SIZE'] = "Cube size (x,y,z) [mm]"
        self.POINTS_CUBE_COLOR = [68, 68, 255, 255]  # "#FF4444FF"
        self.POINTS_CUBE_SIZE = [2., 2., 2.]

        #-----------------------------------------------------
        self._FIELDS_UI['SECTION_CURVES'] = "$CURVES$"

        # White curves
        self._FIELDS_UI['CURVE_1_LINE_WEIGHT'] = "Curve #1 line weight"
        self._FIELDS_UI['CURVE_1_COLOR'] = "Curve #1 color (r,g,b,a)"
        self.CURVE_1_LINE_WEIGHT = 3
        self.CURVE_1_COLOR = [255, 255, 255, 255]

        # Orange curves
        self._FIELDS_UI['CURVE_2_LINE_WEIGHT'] = "Curve #2 line weight"
        self._FIELDS_UI['CURVE_2_COLOR'] = "Curve #2 color (r,g,b,a)"
        self.CURVE_2_LINE_WEIGHT = 3
        self.CURVE_2_COLOR = [255, 127, 0, 255]

        #-----------------------------------------------------
        self._FIELDS_UI['SECTION_SURFACES'] = "$SURFACES$"

        # Green surfaces
        self._FIELDS_UI['SURFACE_COLOR_1'] = "Surface #1 color (r,g,b,a)"
        self.SURFACE_COLOR_1 = [0, 255, 0, 255]

        # Orange surfaces
        self._FIELDS_UI['SURFACE_COLOR_2'] = "Surface #2 color (r,g,b,a)"
        self.SURFACE_COLOR_2 = [204, 102, 51, 255]


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
        S.ShowUI('Set Style Settings')


if __name__ == '__main__':
    runmain()