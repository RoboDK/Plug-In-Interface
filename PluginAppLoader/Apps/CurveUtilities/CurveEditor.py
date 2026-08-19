
# --------------------------------------------
# Imports
# --------------------------------------------
from robodk import robolink, robomath, roboapps, robodialogs

robolink.import_install('PySide2')
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import Qt, QMimeData
from PySide2.QtGui import QClipboard
from PySide2.QtWidgets import QApplication

import _cutools as cutools

import os
import typing
from pathlib import Path
import math
import numpy as np
import sys

from enum import Enum, Flag, auto

# --------------------------------------------
# Globals
# --------------------------------------------

DEBUG_LEVEL = 1
DEBUG_SHOW_TEMP_ITEMS = False

ENABLE_CURVE_PREVIEW_ARROWS = False  # TODO This crashes RoboDK when there is a lot of curves
ENABLE_CURVE_PREVIEW_POINTS = False  # TODO This crashes RoboDK when there is a lot of curves
ENABLE_POINTS_PREVIEW = False  # Use RoboDK's default point preview for all points, only highlight selection

COLOR_HIGHLIGHT = [0, 1, 1, 0.9]  # cyan
COLOR_ARROW = [0, 170 / 255, 0, 0.7]  # green
#COLOR_POINT = [0, 170 / 255, 0, 0.7]  # green
COLOR_POINT = [0, 0, 1, 0.7]  # RoboDK curve points blue

# items
ARROW_SIZE = 10
POINT_SIZE = 4
CURVE_POINT_SIZE = 2

# display
CURVE_LINE_SIZE = 1

ROOT = Path(__file__).resolve().parent
if Path(__file__).suffix != ".py":
    ROOT = ROOT.parent
os.chdir(ROOT)  # the .ui use relative path to the working directly

# --------------------------------------------
# Utility functions
# --------------------------------------------


def calculate_curve_length(curve_points):  # TODO: Add travel length as a statistic?
    if not curve_points or len(curve_points) < 2:
        return 0

    length = 0
    for i in range(1, len(curve_points)):
        p1 = curve_points[i - 1]
        p2 = curve_points[i]
        segment_length = robomath.distance(p1, p2)
        length += segment_length

    return length


def Draw_Wire_Arrows(wire, invert, ratio_spacing, size_curve_arrow):
    # This function was ported from RoboDK 'as-is'

    arrows = []  # list of (point, vector)

    npoints = len(wire)
    lenght_total = calculate_curve_length(wire)  # mm
    narrows = round(0.5 * lenght_total / size_curve_arrow)
    if narrows < 1:
        narrows = 2
    spacing = lenght_total / narrows
    i_prev = npoints - 1
    i = npoints - 2
    if (invert):
        i_prev = 0
        i = 1

    #real_body lenght_cumul = 0;
    lenght_cumul = -spacing * max(0.0, min(ratio_spacing, 1.0))  # changed on 2020-04-27
    lenght = lenght_cumul
    first_done = False
    while (True):
        pta = wire[i_prev][:3]
        ptb = wire[i][:3]
        if (not first_done):
            first_done = True
            #arrows.append((ptb, vba_unit))  # TODO changed from arrows.append((pta, ptb)) # Draw_Arrow(pta, ptb)
            lenght_cumul = spacing

        len_segment = robomath.distance(pta, ptb)
        while (lenght_cumul < lenght + len_segment):
            pointx = (lenght_cumul - lenght)
            if (pointx < 0):
                lenght_cumul = lenght_cumul + spacing
                continue
            elif (pointx > len_segment):
                break

            vba_unit = robomath.normalize3(robomath.subs3(pta, ptb))
            ptx = robomath.add3(ptb, robomath.mult3(vba_unit, pointx))
            arrows.append((ptx, vba_unit))  # TODO: Changed from Draw_Arrow(ptx, ptb)
            lenght_cumul = lenght_cumul + spacing

        lenght = lenght + len_segment

        if (invert):
            i = i + 1
            i_prev = i_prev + 1
            if (i >= npoints):
                break
        else:
            i = i - 1
            i_prev = i_prev - 1
            if (i < 0):
                break
    return arrows


def arrow_mesh():
    return robomath.Mat([
        [-0.719, -0.719, 0.422, -1.316, -0.422, 0.719, 1.439, -1.316, 0.719, -1.439, -1.316, 1.439, 1.316, -1.439, 1.439, -0.719, -1.439, 1.316, 0.422, -0.719, 1.316, 0.000, -3.838, -1.918, 0.000, -3.510, -3.838, 0.000, -1.126, -3.510, 0.000, 1.918, -1.126, -1.918, -0.719, -3.838, -1.316, -1.126, -3.510, -3.510, -3.838, -0.719, -1.439, -3.510, -0.719, -1.316, -3.510, -1.439, 1.918, -1.126, -1.316, -0.422, 1.918, -1.316, 0.719, 1.918, -0.422, -1.439, -0.719, -0.719, -1.439, -1.439, -0.719, -1.316, -1.439, -1.439, -1.316, -1.316, -1.439, -0.422, -1.316, -1.316, -0.422, -0.422, -1.316, 0.719, -0.422, -0.422, 0.719, 0.719, -0.422, 0.000, 3.838, 1.918, 0.000, 3.510, 3.838, 0.000, 1.126, 3.510, 0.000, -1.918, 1.126, 1.918, 0.719, 3.838, 1.316, 1.126, 3.510, 3.510, 3.838, 0.719, 1.439, 3.510, 0.719, 1.316, 3.510, 1.439, -1.918, 1.126, 1.316, 0.422, -1.918, 1.316, -0.719, -1.918, 0.422, 1.439, 0.719, 0.719, 1.439, 1.439, 0.719, 1.316, 1.439, 1.439, 1.316, 1.316, 1.439, 0.422, 1.316, 1.316, 0.422, 0.422, 1.316, -0.719, 0.422, 0.422],
        [-1.316, -1.316, -1.439, 0.719, 1.439, 1.316, 0.422, 0.719, 1.316, -0.422, 0.719, 0.422, -0.719, -0.422, 0.422, -1.316, -0.422, -0.719, -1.439, -1.316, -0.719, 0.000, -1.126, -3.510, 0.000, 1.918, -1.126, 0.000, 3.838, 1.918, 0.000, 3.510, 3.838, -3.510, -1.316, -1.126, 0.719, 3.838, 1.918, 1.918, -1.126, -1.316, -0.422, 1.918, -1.316, 0.719, 1.918, -0.422, 3.510, 3.838, 0.719, 1.439, 3.510, 0.719, 1.316, 3.510, 1.439, -0.422, -1.316, -1.316, -0.422, -0.422, -1.316, 0.719, -0.422, -0.422, 0.719, 0.719, -0.422, 1.439, 0.719, 0.719, 1.439, 1.439, 0.719, 1.316, 1.439, 1.439, 1.316, 1.316, 1.439, 0.000, 1.126, 3.510, 0.000, -1.918, 1.126, 0.000, -3.838, -1.918, 0.000, -3.510, -3.838, 3.510, 1.316, 1.126, -0.719, -3.838, -1.918, -1.918, 1.126, 1.316, 0.422, -1.918, 1.316, -0.719, -1.918, 0.422, -3.510, -3.838, -0.719, -1.439, -3.510, -0.719, -1.316, -3.510, -1.439, 0.422, 1.316, 1.316, 0.422, 0.422, 1.316, -0.719, 0.422, 0.422, -0.719, -0.719, 0.422, -1.439, -0.719, -0.719, -1.439, -1.439, -0.719, -1.316, -1.439, -1.439],
        [1.000, -5.000, 1.000, -5.000, -5.000, -5.000, -5.000, -5.000, -5.000, -5.000, -5.000, -5.000, -5.000, -5.000, -5.000, -5.000, -5.000, -5.000, -5.000, -5.000, -5.000, 5.000, 0.000, 0.000, 5.000, 0.000, 0.000, 5.000, 0.000, 0.000, 5.000, 0.000, 0.000, 0.000, 1.000, 0.000, 1.000, 0.000, 0.000, 0.000, 0.000, 1.000, 1.000, 0.000, 1.000, 1.000, 0.000, 1.000, 0.000, 0.000, 1.000, 1.000, 0.000, 1.000, 1.000, 0.000, 1.000, -5.000, -5.000, 1.000, 1.000, -5.000, 1.000, -5.000, -5.000, 1.000, 1.000, -5.000, 1.000, -5.000, -5.000, 1.000, 1.000, -5.000, 1.000, -5.000, -5.000, 1.000, 1.000, -5.000, 1.000, 5.000, 0.000, 0.000, 5.000, 0.000, 0.000, 5.000, 0.000, 0.000, 5.000, 0.000, 0.000, 0.000, 1.000, 0.000, 1.000, 0.000, 0.000, 0.000, 0.000, 1.000, 1.000, 0.000, 1.000, 1.000, 0.000, 1.000, 0.000, 0.000, 1.000, 1.000, 0.000, 1.000, 1.000, 0.000, 1.000, -5.000, -5.000, 1.000, 1.000, -5.000, 1.000, -5.000, -5.000, 1.000, 1.000, -5.000, 1.000, -5.000, -5.000, 1.000, 1.000, -5.000, 1.000, -5.000, -5.000, 1.000],
    ])


# TODO
def curve_to_arrows(wire, invert, ratio_spacing, size_curve_arrow):
    arrows = Draw_Wire_Arrows(wire, invert, ratio_spacing, size_curve_arrow)  # [(xyz, ijk), (xyz, ijk)..]
    return [xyz + ijk for (xyz, ijk) in arrows]  # [xyzijk, xyzijk..]


# --------------------------------------------
# Clipboard
# --------------------------------------------
# This function was ported from RoboDK 'as-is'
GLOBAL_MAX_DECIMALS_XYZ = 6  # Example global value


def copy_string_to_clipboard(string):
    """
    Copy a string to the clipboard using PySide2.
    """
    mime_data = QMimeData()
    mime_data.setText(string)
    clipboard = QApplication.clipboard()
    clipboard.setMimeData(mime_data, QClipboard.Clipboard)


def get_string_from_clipboard():
    """
    Get a string from the clipboard using PySide2.
    """
    clipboard = QApplication.clipboard()
    mime_data = clipboard.mimeData()
    if not mime_data.hasText():
        return None
    return mime_data.text()


def copy_point_to_clipboard(point):
    """
    Copy a point (XYZIJK) to the clipboard using PySide2.
    """
    return copy_to_clipboard_matrix4x4(robomath.point_Zaxis_2_pose(point[0:3], point[3:6]))


def get_point_from_clipboard():
    """
    Get a point (XYZIJK) from the clipboard using PySide2.
    """
    data = get_string_from_clipboard()
    if not data:
        return None
    pose = string_to_matrix4x4(data)
    if pose is None:
        return None
    xyz = pose.Pos()
    ijk = pose.VZ()
    return xyz + ijk


def copy_to_clipboard_matrix4x4(matrix4x4):
    """
    Copy a 4x4 matrix to the clipboard as a formatted string.
    """
    result_str = string_from_matrix4x4(matrix4x4)
    copy_string_to_clipboard(result_str)


def string_from_matrix4x4(matrix4x4):
    """
    Format a 4x4 matrix into a string.
    """
    precision = max(6, GLOBAL_MAX_DECIMALS_XYZ)
    formatted_str = "[ "
    formatted_str += string_from_array(matrix4x4[0].tr().tolist(), precision, "", ", ") + " ;\n  "
    formatted_str += string_from_array(matrix4x4[1].tr().tolist(), precision, "", ", ") + " ;\n  "
    formatted_str += string_from_array(matrix4x4[2].tr().tolist(), precision, "", ", ") + " ;\n  "
    formatted_str += string_from_array(matrix4x4[3].tr().tolist(), precision, "", ", ") + " ];\n"
    return formatted_str


def string_to_matrix4x4(string):
    """
    Format a string to a 4x4 matrix.
    """
    if not string.strip() or not string.startswith('['):
        return None

    data = []
    for line in string.strip().split("\n"):
        line = line.lstrip('[').rstrip('];').strip()
        values = [float(x.strip()) for x in line.split(",")]
        if len(values) != 4:
            return None
        data.append(values)

    if len(data) != 4:
        return None

    return robomath.Mat(data)  # RoboDK uses Staubli/Mecademic


def string_from_array(array, precision, prefix, separator):
    """
    Format an array into a string with specific precision and formatting options.
    """
    return separator.join([f"{prefix}{val:.{precision}f}" for val in array])


# --------------------------------------------
# Normals / IJK tools
# --------------------------------------------
def normal_polar_2_vector(phi, theta):
    """Polar coordinates to IJK"""
    phi = math.radians(phi)
    theta = math.radians(theta)
    return robomath.normalize3([math.sin(phi) * math.cos(theta), math.sin(phi) * math.sin(theta), math.cos(phi)])


def normal_vector_2_polar(normal_in):
    """
    Orientation vector (IJK) to Polar/Spherical coordinates (mathematics convention).
        φ (phi): [0,180]
        θ (theta): [0,360]
    """
    phi = 0
    theta = 0
    xyz = robomath.normalize3(normal_in)
    dividend = robomath.sqrt(xyz[0] * xyz[0] + xyz[1] * xyz[1])
    if (dividend < 0.00001):
        if (xyz[2] > 0):
            phi = 0
            theta = 0
        else:
            phi = robomath.pi
            theta = 0
    else:
        phi = robomath.atan2(dividend, xyz[2])
        theta = robomath.atan2(xyz[1], xyz[0])
        if (theta < 0):
            theta = theta + 2 * robomath.pi

    return math.degrees(phi), math.degrees(theta)


def normalize3_lock(i, j, k, edited_component, edited_value):
    """Set IJK values while attempting to keep normalization
    """

    edited_component = ['i', 'j', 'k'][edited_component - 1]

    # Clamp the edited value to the range [-1, 1]
    edited_value = max(min(edited_value, 1), -1)

    # Set the edited component to the new value
    if edited_component == 'i':
        i = edited_value
    elif edited_component == 'j':
        j = edited_value
    elif edited_component == 'k':
        k = edited_value

    # Handle the special case where all components are zero
    if i == 0 and j == 0 and k == 0:
        return 1, 0, 0

    # Calculate the magnitude of the other two components
    remaining_magnitude_squared = 1 - edited_value**2

    # Normalize the other two components
    if edited_component == 'i':
        if j == 0 and k == 0:
            return 1, 0, 0
        scale = math.sqrt(remaining_magnitude_squared / (j**2 + k**2))
        j *= scale
        k *= scale
    elif edited_component == 'j':
        if i == 0 and k == 0:
            return 0, 1, 0
        scale = math.sqrt(remaining_magnitude_squared / (i**2 + k**2))
        i *= scale
        k *= scale
    else:  # edited_component == 'k'
        if i == 0 and j == 0:
            return 0, 0, 1
        scale = math.sqrt(remaining_magnitude_squared / (i**2 + j**2))
        i *= scale
        j *= scale

    return i, j, k


# --------------------------------------------
# Mesh / Curves / Points tools
# --------------------------------------------


def object_has_mesh(object_item):
    if object_item.type != robolink.ITEM_TYPE_OBJECT:
        return False

    feature_mesh = object_item.GetPoints(robolink.FEATURE_OBJECT_MESH, 0)[0]
    if not feature_mesh:
        return False
    return True


def MatMultiplyRow(m, s):
    """Multiply coordinate Y by dist to create the scale along Y"""
    new_m = m.copy()
    new_m.rows[0] = [e * s for e in new_m.rows[0]]
    new_m.rows[1] = [e * s for e in new_m.rows[1]]
    new_m.rows[2] = [e * s for e in new_m.rows[2]]
    return new_m


def MatMoveRef(pose, m):
    """Multiple a Mesh (3xN) of by a pose"""
    #sz1 = len(m.rows)
    sz2 = len(m.rows[0])
    #new_m = robomath.Mat(sz1, sz2)
    new_m = m.copy()
    for c in range(sz2):

        x = m.rows[0][c]
        y = m.rows[1][c]
        z = m.rows[2][c]

        newx = pose.rows[0][0] * x + pose.rows[0][1] * y + pose.rows[0][2] * z + pose.rows[0][3]
        newy = pose.rows[1][0] * x + pose.rows[1][1] * y + pose.rows[1][2] * z + pose.rows[1][3]
        newz = pose.rows[2][0] * x + pose.rows[2][1] * y + pose.rows[2][2] * z + pose.rows[2][3]

        new_m.rows[0][c] = newx
        new_m.rows[1][c] = newy
        new_m.rows[2][c] = newz

    return new_m


# --------------------------------------------
# Color tools
# --------------------------------------------


def rgba2hex(color):
    """[r,g,b,a*] 0-255 to hex #FFFFFF"""
    r, g, b = color[:3]
    a = 255
    if len(color) > 3:
        a = color[3]
    return '#{:02x}{:02x}{:02x}{:02x}'.format(a, r, g, b).upper()


def base255to1(color):
    """[r,g,b,a*] 0-255 to 0-1"""
    return [x / 255 for x in color]


def base1to255(color):
    """[r,g,b,a*] 0-1 to 0-255"""
    return [int(x * 255) for x in color]


def base255toQColor(color):
    """[r,g,b,a*] 0-255 to QColor"""
    r, g, b = color[:3]
    a = 255
    if len(color) > 3:
        a = color[3]
    return QtGui.QColor(r, g, b, a)


def base1toQColor(color):
    """[r,g,b,a*] 0-1 to QColor"""
    return base255toQColor(base1to255(color))


def get_distinct_color(index, total_indices):
    """Get a repeatable distinctive color out of N distinct colors"""
    import colorsys
    if total_indices <= 0:
        raise ValueError("Total indices must be greater than 0")

    # Ensure unique hue for each index
    hue = index / total_indices
    saturation = 0.7  # Fixed saturation
    lightness = 0.5  # Fixed lightness

    # Convert HSL to RGB
    r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)

    return [r, g, b]


def get_alternating_color(index, color1=[1, 0, 1], color2=[0, 1, 1]):
    if index % 2 == 0:
        return color1
    return color2


def create_spinbox(parent=None, data_type=""):
    """
    data_type: x, y, z, i, j, k, θ, φ
    """
    COLORS = {
        "x": base255toQColor([255, 175, 175, 255]),  # red
        "y": base255toQColor([175, 255, 175, 255]),  # green
        "z": base255toQColor([175, 175, 255, 255]),  # blue
        "i": base255toQColor([175, 255, 255, 255]),  # cyan
        "j": base255toQColor([255, 175, 255, 255]),  # magenta
        "k": base255toQColor([255, 255, 175, 255]),  # yellow
        "φ": base255toQColor([175, 255, 255, 255]),  # cyan
        "θ": base255toQColor([255, 175, 255, 255]),  # magenta
    }

    editor = QtWidgets.QDoubleSpinBox(parent)

    # XYZ defaults
    editor.setDecimals(4)
    editor.setRange(-9e6, 9e6)  # mm
    editor.setSingleStep(1)
    editor.setAlignment(Qt.AlignRight)

    col = data_type.lower()
    if col in COLORS.keys():
        palette = editor.palette()
        palette.setColor(QtGui.QPalette.Base, COLORS[col])
        palette.setColor(QtGui.QPalette.Text, QtGui.QColor(0, 0, 0))  # TODO assuming black is better
        editor.setPalette(palette)

    if col in ["i", "j", "k"]:
        editor.setRange(-1, 1)  # unit vector
        editor.setSingleStep(0.1)

    elif col in ["φ"]:
        editor.setRange(0, 180)  # deg
        editor.setSingleStep(15)

    elif col in ["θ"]:
        editor.setRange(0, 360)  # deg
        editor.setSingleStep(15)

    editor.adjustSize()
    return editor


# --------------------------------------------
# General classes
# --------------------------------------------
class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class RoboDKManager(metaclass=Singleton):
    """
    Singleton class that updates RoboDK preview data (coloring scheme, temporary items) as well as saving data.
    """

    CURVE_ARROW_NAME = 'TEMP CURVE ARROW'
    CURVE_POINT_NAME = 'TEMP CURVE POINT'
    POINT_NAME = 'TEMP POINT'

    def __init__(self, RDK):
        self.RDK = RDK

        self.object_points = {}  # Store object points so that we don't have to retrieve them every time
        self.object_curves = {}  # Store object curves so that we don't have to retrieve them every time

        self.object_points_preview = {}
        self.object_curves_arrows_preview = {}  # arrows along the curve
        self.object_curves_points_preview = {}  # selected points in a curve

        self._enable_curve_arrows_previews = ENABLE_CURVE_PREVIEW_ARROWS
        self._enable_curve_points_previews = ENABLE_CURVE_PREVIEW_POINTS
        self._enable_points_previews = ENABLE_POINTS_PREVIEW

        self.hard_clear_temporary_items()

    def __del__(self):
        self.hard_clear_temporary_items()

    def enable_curve_arrows_previews(self, enable):
        self._enable_curve_arrows_previews = enable

    def enable_curve_points_previews(self, enable):
        self._enable_curve_points_previews = enable

    def enable_points_previews(self, enable):
        self._enable_points_previews = enable

    def set_object_points(self, item, points, render_status=True):
        """
        Set the object points, and store them.
        Any change to the points must be reported here.
        """
        self.object_points[item] = points

        # Points are relative to the object origin, while AddPoints is relative to the object pose
        if render_status:
            self.RDK.Render(False)

        item.setParam('Reset', 'Points')  # Note: There is no way to reset a single point using an index, we need to overwrite all the points!
        if points:
            cutools.add_points(item, points, add_to_ref=True, projection_type=robolink.PROJECTION_NONE)

        if render_status:
            self.RDK.Render(True)

    def init_object_points_preview(self, item, render_status=True):
        """
        Initialize previews for Points, without highlights/selection.
        """
        if not self._enable_points_previews:
            return

        if not item in self.object_points or not self.object_points[item]:
            return

        if render_status:
            self.RDK.Render(False)

        # Simply use the existing point in the object, faster than meshes!
        s = f'PARTICLE=SPHERE({POINT_SIZE},{POINT_SIZE*10}) COLOR={rgba2hex(base1to255(COLOR_POINT))}'
        if item in self.object_curves and self.object_curves[item]:
            s += f' LINEW={CURVE_LINE_SIZE*5}'
        item.setParam('Display', s)

        if render_status:
            self.RDK.Render(True)

    def select_object_points_preview(self, item, selected_indexes, render_status=True):
        """
        Update the highlighted/selected points.

        This function attempts to reuse as much of the existing items as possible, for speed.
        """
        if item in self.object_points_preview:
            if self.object_points_preview[item].Valid():
                self.object_points_preview[item].Delete()
            del self.object_points_preview[item]

        if not item in self.object_points or not self.object_points[item]:
            return

        selected_points = [p for i, p in enumerate(self.object_points[item]) if i in selected_indexes]
        if not selected_points:
            return

        # There is currently no way to set the points color by index
        # Thus, we create highlighted points a bit larger than the normal points to see them
        # Every, single, time.

        if render_status:
            self.RDK.Render(False)

        self.object_points_preview[item] = self.RDK.AddPoints(selected_points, 0, False, robolink.PROJECTION_NONE)
        preview_item = self.object_points_preview[item]

        preview_item.setParent(item)
        preview_item.setName(self.POINT_NAME)
        #preview_item.setVisible(False)
        if not DEBUG_SHOW_TEMP_ITEMS:
            preview_item.setParam('Tree', 'Hide')  # Won't be saved with the station
            self.RDK.setFlagsItem(preview_item, robolink.FLAG_ITEM_NONE)
        preview_item.setParam('Display', f'PARTICLE=SPHERE({POINT_SIZE*1.1},{POINT_SIZE*10}) COLOR={rgba2hex(base1to255(COLOR_HIGHLIGHT))}')

        if render_status:
            self.RDK.Render(True)

    def clear_object_points_preview(self, item, render_status=True):
        """
        Remove all Points previews, highlighting and styling.
        """
        if render_status:
            self.RDK.Render(False)

        # Remove points coloring
        if item.Valid(True):
            item.setParam('Display', ' ')

        # Remove points temporary items (spheres)
        if item in self.object_points_preview:
            if self.object_points_preview[item].Valid():
                self.object_points_preview[item].Delete()
            del self.object_points_preview[item]

        if render_status:
            self.RDK.Render(True)

    def set_object_curves(self, item, curves, render_status=True):
        """
        Set the object curves, and store them.
        Any change to the curves must be reported here.
        """
        self.object_curves[item] = curves

        # Curves are relative to the object origin, while AddCurve is relative to the object pose
        if render_status:
            self.RDK.Render(False)

        item.setParam('Reset', 'Curves')  # Note: There is no way to reset a single point using an index, we need to overwrite all the points!
        for i, curve in enumerate(curves):
            cutools.add_curve(item, curve, add_to_ref=True, projection_type=robolink.PROJECTION_NONE)

        if render_status:
            self.RDK.Render(True)

    def init_object_curves_preview(self, item, render_status=True):
        """
        Initialize previews for Curves, without highlights/selection.
        """

        if item in self.object_curves_arrows_preview:
            if self.object_curves_arrows_preview[item].Valid():
                self.object_curves_arrows_preview[item].Delete()
            del self.object_curves_arrows_preview[item]
        if item in self.object_curves_points_preview:
            if self.object_curves_points_preview[item].Valid():
                self.object_curves_points_preview[item].Delete()
            del self.object_curves_points_preview[item]

        if not item in self.object_curves or not self.object_curves[item]:
            return

        if render_status:
            self.RDK.Render(False)

        # Simply put the curves in bold
        s = f' LINEW={CURVE_LINE_SIZE*5}'
        if item in self.object_points and self.object_points[item]:
            s += f'PARTICLE=SPHERE({POINT_SIZE},{POINT_SIZE*10}) COLOR={rgba2hex(base1to255(COLOR_POINT))}'
        item.setParam('Display', s)

        curves = self.object_curves[item]
        total_indices = len(curves)  #sum([len(c) for c in curves])
        shape = []  # one shape for ALLL curves!
        for i, curve in enumerate(curves):
            color = get_distinct_color(i, total_indices)
            item.setColorCurve(color, i)

            if self._enable_curve_arrows_previews:
                wire_arrows = Draw_Wire_Arrows(curve, False, 0, ARROW_SIZE)  # TODO SizeCurveArrow
                for arrow in wire_arrows:
                    xyz, axis = arrow[0], arrow[1]
                    pose = robomath.point_Zaxis_2_pose(xyz, axis)
                    mesh = arrow_mesh()
                    mesh = MatMultiplyRow(mesh, ARROW_SIZE / 10)
                    mesh = MatMoveRef(pose, mesh)
                    shape.append(mesh)
                    shape.append(COLOR_ARROW)

            if self._enable_curve_points_previews:
                # We can't use item.setParam('Display', 'PARTICLE=SPHERE') on curves..
                # TODO We need to create a new object with points instead
                pass

        if shape:
            self.object_curves_arrows_preview[item] = self.RDK.AddShape(shape)
            preview_item = self.object_curves_arrows_preview[item]

            preview_item.setParent(item)
            preview_item.setName(self.CURVE_ARROW_NAME)
            #preview_item.setVisible(False)
            if not DEBUG_SHOW_TEMP_ITEMS:
                preview_item.setParam('Tree', 'Hide')  # Won't be saved with the station
                self.RDK.setFlagsItem(preview_item, robolink.FLAG_ITEM_NONE)

        if render_status:
            self.RDK.Render(True)

    def select_object_curves_preview(self, item, selected_indexes, selected_points_indexes, render_status=True):
        """
        Update the highlighted/selected Curves.

        This function attempts to reuse as much of the existing items as possible, for speed.
        """
        if not item in self.object_curves or not self.object_curves[item]:
            return

        if render_status:
            self.RDK.Render(False)

        # Updates the curves highlight
        curves = self.object_curves[item]
        total_indices = len(curves)  #sum([len(c) for c in curves])
        for i in range(total_indices):
            if i in selected_indexes:
                item.setColorCurve(COLOR_HIGHLIGHT, i)
            else:
                item.setColorCurve(get_distinct_color(i, total_indices), i)

        # Update the curve's point highlight
        fake_curve = []
        for i in selected_indexes:
            fake_curve.extend(curves[i])
        for (ic, ip) in selected_points_indexes:
            fake_curve.append(curves[ic][ip])

        if item in self.object_curves_points_preview:
            self.object_curves_points_preview[item].setParam('Reset', 'Points')
            if fake_curve:
                self.object_curves_points_preview[item].AddPoints(fake_curve, add_to_ref=True, projection_type=robolink.PROJECTION_NONE)
        else:
            if fake_curve:
                self.object_curves_points_preview[item] = self.RDK.AddPoints(fake_curve, 0, False, robolink.PROJECTION_NONE)
                preview_item = self.object_curves_points_preview[item]
                preview_item.setParent(item)
                preview_item.setName(self.POINT_NAME)
                #preview_item.setVisible(False)
                if not DEBUG_SHOW_TEMP_ITEMS:
                    preview_item.setParam('Tree', 'Hide')  # Won't be saved with the station
                    self.RDK.setFlagsItem(preview_item, robolink.FLAG_ITEM_NONE)
                preview_item.setParam('Display', f'PARTICLE=SPHERE({CURVE_POINT_SIZE*1.1},{CURVE_POINT_SIZE*10}) COLOR={rgba2hex(base1to255(COLOR_HIGHLIGHT))}')

        if render_status:
            self.RDK.Render(True)

    def clear_object_curves_preview(self, item, render_status=True):
        """
        Remove all Curves previews, highlighting and styling.
        """
        if render_status:
            self.RDK.Render(False)

        # Remove curves coloring
        if item in self.object_curves and item.Valid(True):
            curves = self.object_curves[item]
            item.setParam('Display', ' ')
            for i in range(len(curves)):
                item.setColorCurve([0, 0, 0, 1], i)

        # Remove curves temporary items (arrows and spheres)
        if item in self.object_curves_arrows_preview:
            if self.object_curves_arrows_preview[item].Valid():
                self.object_curves_arrows_preview[item].Delete()
            del self.object_curves_arrows_preview[item]
        if item in self.object_curves_points_preview:
            if self.object_curves_points_preview[item].Valid():
                self.object_curves_points_preview[item].Delete()
            del self.object_curves_points_preview[item]

        if render_status:
            self.RDK.Render(True)

    def update_object(self, item, curves, points, selected_curves=None, selected_points=None, render_status=True):
        """
        Wrapper function to update an object (write curves/points), update preview and highlights.
        """
        if render_status:
            self.RDK.Render(False)

        self.set_object_curves(item, curves, render_status=False)
        self.set_object_points(item, points, render_status=False)
        self.init_object_curves_preview(item, render_status=False)
        self.init_object_points_preview(item, render_status=False)
        #self.select_object_curves_preview(item, len(curves), selected_curves, render_status=False)
        #self.select_object_points_preview(item, selected_points, render_status=False)

        if render_status:
            self.RDK.Render(True)

    def update_object_previews(self, item, selected_curves, selected_curve_points, selected_points, render_status=True):
        """
        Wrapper function to update an object (write curves/points), update preview and highlights
        """
        if render_status:
            self.RDK.Render(False)

        self.select_object_curves_preview(item, selected_curves, selected_curve_points, render_status=False)
        self.select_object_points_preview(item, selected_points, render_status=False)

        if render_status:
            self.RDK.Render(True)

    def clear_object_previews(self, item, render_status=True):
        if render_status:
            self.RDK.Render(False)

        self.clear_object_curves_preview(item, False)
        self.clear_object_points_preview(item, False)

        if render_status:
            self.RDK.Render(True)

    def hard_clear_temporary_items(self):
        """Hard clear potential leftovers"""

        for item in self.object_points:
            self.clear_object_previews(item)
        for item in self.object_curves:
            self.clear_object_previews(item)

        items = [x for x in self.RDK.ItemList(robolink.ITEM_TYPE_OBJECT) if x.Name() in [self.CURVE_ARROW_NAME, self.CURVE_POINT_NAME, self.POINT_NAME]]
        if items:
            self.RDK.Delete(items)


# --------------------------------------------
# Curve Editor classes
# --------------------------------------------


class CurveSelectionModel(QtCore.QItemSelectionModel):

    def __init__(self, model=None, parent=None):
        super(CurveSelectionModel, self).__init__(model, parent)

    @staticmethod
    def is_point_index(index: QtCore.QModelIndex):
        return index.isValid() and not index.parent().isValid() and not index.child(0, 0).isValid()

    @staticmethod
    def is_curve_index(index: QtCore.QModelIndex):
        return index.isValid() and not index.parent().isValid() and index.child(0, 0).isValid()

    @staticmethod
    def is_curve_point_index(index: QtCore.QModelIndex):
        return index.isValid() and index.parent().isValid() and not index.child(0, 0).isValid()

    def selectedCurves(self):
        """Whole curve indexes"""
        return [r for r in self.selectedRows() if self.is_curve_index(r)]

    def selectedCurvePoints(self):
        """Partial curve point indexes"""
        return [r for r in self.selectedRows() if self.is_curve_point_index(r)]

    def selectedPoints(self):
        """Point indexes"""
        return [r for r in self.selectedRows() if self.is_point_index(r)]

    def selected(self):
        """
        Return the selected curves, curve's points and points as-is.

        :return: [curves, curve_points, points]
        """

        # Keep original ordering
        curves = []
        curve_points = []
        points = []
        for r in self.selectedRows():
            if self.is_curve_index(r):
                curves.append(r)
            elif self.is_curve_point_index(r):
                curve_points.append(r)
            elif self.is_point_index(r):
                points.append(r)

        return curves, curve_points, points

    def selectedUnique(self):
        """
        Return the selected curves, curve's points and points that are unique.
        If a curve point is already selected through a curve, it won't be included.
        If all points of a curve are selected (but not the curve itself), the curve points are replaced by the curve index.

        Return [curves, curve_points, points]
        """

        # Keep original ordering
        curves = []
        curve_points = []
        points = []
        for r in self.selectedRows():
            if self.is_curve_index(r):
                curves.append(r)
            elif self.is_curve_point_index(r):
                curve_points.append(r)
            elif self.is_point_index(r):
                points.append(r)

        # Remove points included in a curve
        for cp in list(curve_points):
            if cp.parent() in curves:
                curve_points.remove(cp)

        # Replace curve points with a curve index if all points of a curve are selected
        parent_child_count = {}
        for cp in curve_points:
            parent = cp.parent()
            parent_child_count[parent] = parent_child_count.get(parent, 0) + 1

        for parent, count in parent_child_count.items():
            if self.model().rowCount(parent) == count:
                curves.append(parent)  # TODO: Keep original order
                for i in range(self.model().rowCount(parent)):
                    curve_points.remove(parent.child(i, 0))

        # Remove duplicates
        # curves = list(dict.fromkeys(curves))
        # curve_points = list(dict.fromkeys(curve_points))
        # points = list(dict.fromkeys(points))

        return curves, curve_points, points

    def selectedExpanded(self):
        """
        Return the selected curves, curve's points and points that are unique, but expands the curves.
        If a curve index is selected, all its points are added.

        Return [curves, curve_points, points]
        """
        curves, curve_points, points = self.selectedUnique()

        # curves = []
        # curve_points = []
        # points = []
        # for r in self.selectedRows():
        #     if self.is_curve_index(r):
        #         curves.append(r)
        #     elif self.is_curve_point_index(r):
        #         curve_points.append(r)
        #     elif self.is_point_index(r):
        #         points.append(r)

        # Expand curves
        for c in list(curves):
            for i in range(self.model().rowCount(c)):
                cp = c.child(i, 0)
                if cp not in curve_points:
                    curve_points.append(cp)  # TODO: Keep original order

        # Remove duplicates
        # curves = list(dict.fromkeys(curves))
        # curve_points = list(dict.fromkeys(curve_points))
        # points = list(dict.fromkeys(points))

        return curves, curve_points, points

    def selectAllCurves(self):
        model = self.model()

        self.blockSignals(True)

        self.clearSelection()
        for index in model.curveIndexes():
            self.select(index, QtCore.QItemSelectionModel.Select | QtCore.QItemSelectionModel.Rows)

        self.blockSignals(False)

        self.selectionChanged.emit(self.selection(), QtCore.QItemSelectionModel.Select)

    def selectAllPoints(self):
        model = self.model()

        self.blockSignals(True)

        self.clearSelection()
        for index in model.pointIndexes():
            self.select(index, QtCore.QItemSelectionModel.Select | QtCore.QItemSelectionModel.Rows)

        self.blockSignals(False)

        self.selectionChanged.emit(self.selection(), QtCore.QItemSelectionModel.Select)


class QDoubleSpinBoxDelegate(QtWidgets.QStyledItemDelegate):

    size_hint = None

    # https://doc.qt.io/qt-5/qtwidgets-itemviews-spinboxdelegate-example.html
    def __init__(self, parent=None):
        super(QDoubleSpinBoxDelegate, self).__init__(parent)

    def displayText(self, value: typing.Any, locale: QtCore.QLocale) -> str:
        return f"{value:.2f}"

    def createEditor(self, parent, option, index):
        editor = create_spinbox(parent, QCurvesItemModel.COLS[index.column()])
        self.size_hint = editor.sizeHint()
        return editor

    def sizeHint(self, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex) -> QtCore.QSize:
        if self.size_hint is None:
            self.createEditor(None, None, index)
            #return super().sizeHint(option, index)
        return self.size_hint


class CurvesTreeView(QtWidgets.QTreeView):

    def __init__(self, parent=None) -> None:
        super(CurvesTreeView, self).__init__(parent)

        self.setUniformRowHeights(True)
        for i in range(1, len(QCurvesItemModel.COLS)):
            self.setItemDelegateForColumn(i, QDoubleSpinBoxDelegate(self))

        self.setDragEnabled(False)

        self.setSortingEnabled(False)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)

        self.setExpandsOnDoubleClick(True)
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.SelectedClicked | QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked)

        self.header().setStretchLastSection(False)
        self.header().setCascadingSectionResizes(True)
        self.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.header().setDragEnabled(False)
        self.header().setSectionsMovable(False)

        self.setHeaderHidden(False)

        self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

        self.clipboard = []  # (model item, original index, original parent)

    def setIJKColumnsVisible(self, visible):
        self.setColumnHidden(QCurvesItemModel.COLS2['I'], not visible)
        self.setColumnHidden(QCurvesItemModel.COLS2['J'], not visible)
        self.setColumnHidden(QCurvesItemModel.COLS2['K'], not visible)

    def setDistanceColumnsVisible(self, visible):
        self.setColumnHidden(QCurvesItemModel.COLS2['Tot. Dist.'], not visible)
        self.setColumnHidden(QCurvesItemModel.COLS2['Rel. Dist.'], not visible)

    def selectionChanged(self, selected, deselected):  # override
        super().selectionChanged(selected, deselected)
        if isinstance(self.selectionModel(), CurveSelectionModel):
            self.model().updateRoboDKSelectionHighlights(*self.selectionModel().selectedExpanded())

    def selectAllCurves(self):
        self.selectionModel().selectAllCurves()

    def selectAllPoints(self):
        self.selectionModel().selectAllPoints()

    def copySelection(self):
        """
        Copy a mix of whole curves, curve's point, and standalone points as a set of subsequent points.
        """
        self.clipboard.clear()

        model = self.model()

        _, curve_points, points = self.selectionModel().selectedExpanded()
        selected_points = curve_points + points
        if not selected_points:
            return

        # Copy GUI elements
        for index in selected_points:
            self.clipboard.append(model.getPointData(index))

        # Clipboard the first point to the "real" clipboard for RoboDK
        copy_point_to_clipboard(self.clipboard[0])

    def cutSelection(self):
        self.copySelection()
        self.deleteSelection()

    def pasteToSelection(self):
        """
        Paste a list of subsequent points to a curve. Behavior depending on selection type:
            Curve: add points at the end
            Curve's point: insert after the selected point
            Point: insert points after the selected point
            Nothing: create a new curve
        """

        # Check paste from RoboDK
        robodk_point = get_point_from_clipboard()
        if robodk_point and not self.clipboard:
            self.clipboard = [robodk_point]

        if not self.clipboard:
            return  # Clipboard is empty

        curves, curve_points, points = self.selectionModel().selectedUnique()
        selected_rows = curves + curve_points + points

        model = self.model()

        if not selected_rows:
            # Add a new curve
            model.addCurve(self.clipboard)

        else:
            for parent_index in selected_rows:
                if not parent_index.isValid():
                    continue

                if model.is_curve_index(parent_index):
                    # If its a curve, add points as its child
                    curve = model.getCurveData(parent_index)
                    model.editCurveData(parent_index, curve + self.clipboard)

                elif model.is_curve_point_index(parent_index):
                    # If its a curve point, add points to its parent after it
                    row = parent_index.row() + 1
                    curve_index = parent_index.parent()
                    curve = model.getCurveData(curve_index)
                    curve = curve[:row] + self.clipboard + curve[row:]
                    model.editCurveData(curve_index, curve)

                elif model.is_point_index(parent_index):
                    # If its a point, add points to its parent after it
                    for p in reversed(self.clipboard):
                        model.addPoint(p, parent_index.siblingAtRow(parent_index.row() + 1))

    def deleteSelection(self):
        curves, curve_points, points = self.selectionModel().selectedUnique()
        if len(curves) + len(curve_points) + len(points) == 0:
            return False

        model = self.model()

        # Get the rows to delete first, then delete them in reverse-order as it breaks the indexes
        curves, curve_points, points = set(curves), set(curve_points), set(points)

        # Remove curve's points if the curve is being deleted
        # Remove the parent curve if its only child is being deleted
        for index in list(curve_points):
            if index.parent() in curves:
                curve_points.remove(index)
                continue
            child_count = model.rowCount(index.parent())
            if child_count == 1:
                curves.add(index.parent())
                curve_points.remove(index)
                continue

        model.removeRowsSmart(curves, curve_points, points)

        self.selectionModel().clearSelection()  # Ensure with trigger selection_changed

        return True

    def addPoint(self):

        model = self.model()
        model.object_item(allow_new=True)

        curves, curve_points, points = self.selectionModel().selectedUnique()
        selected_rows = curves + curve_points + points

        if not selected_rows:
            # Add a new curve
            model.addPoint([0, 0, 0, 0, 0, 1])  # alternatively, use addPoint by default

        else:
            for parent_index in selected_rows:
                if not parent_index.isValid():
                    continue

                if model.is_curve_index(parent_index):
                    # If its a curve, add point as its child
                    curve = model.getCurveData(parent_index)
                    model.editCurveData(parent_index, curve + [[0, 0, 0, 0, 0, 1]])

                elif model.is_curve_point_index(parent_index):
                    # If its a curve point, add points to its parent after it
                    row = parent_index.row() + 1
                    curve_index = parent_index.parent()
                    curve = model.getCurveData(curve_index)
                    curve = curve[:row] + [[0, 0, 0, 0, 0, 1]] + curve[row:]
                    model.editCurveData(curve_index, curve)

                elif model.is_point_index(parent_index):
                    # If its a point, add a point
                    model.addPoint([0, 0, 0, 0, 0, 1])

    def moveRow(self, from_index: QtCore.QModelIndex, to_index: QtCore.QModelIndex):
        """Move a row within a parent"""
        if not from_index.isValid() or not to_index.isValid():
            return False

        if from_index.parent() != to_index.parent():
            return False

        #from_row = from_index.row()
        to_row = to_index.row()
        row_count = self.model().rowCount(from_index.parent())
        if to_row < 0 or to_row >= row_count:
            return False

        is_expanded = self.isExpanded(from_index)  # Moving a parent will collapse the children

        from_item = self.model().itemFromIndex(from_index)
        parent_item = from_item.parent()
        if not parent_item:
            parent_item = self.model().invisibleRootItem()

        self.model().blockSignals(True)
        row_items = [x for x in parent_item.takeRow(from_item.row()) if x is not None]
        self.model().blockSignals(False)
        parent_item.insertRow(to_index.row(), row_items)

        self.setExpanded(to_index, is_expanded)

        return True

    def moveUp(self):
        selected_rows = self.selectionModel().selectedRows()
        if not selected_rows:
            return False

        if len(selected_rows) > 1:
            self.selectionModel().select(selected_rows[0], QtCore.QItemSelectionModel.Rows | QtCore.QItemSelectionModel.SelectCurrent)
            selected_rows = self.selectionModel().selectedRows()  # TODO: Allow multi select

        from_index = selected_rows[0]
        if not from_index.isValid():
            return False
        to_index = from_index.siblingAtRow(from_index.row() - 1)
        if not to_index.isValid():
            return False

        # Prevent a point to be moved up above a curve
        model = self.model()
        if model.is_point_index(from_index) and model.is_curve_index(to_index):
            return False

        success = self.moveRow(from_index, to_index)

        if success:
            self.selectionModel().select(to_index, QtCore.QItemSelectionModel.Rows | QtCore.QItemSelectionModel.SelectCurrent)
        return success

    def moveDown(self):
        selected_rows = self.selectionModel().selectedRows()
        if not selected_rows:
            return False

        if len(selected_rows) > 1:
            self.selectionModel().select(selected_rows[0], QtCore.QItemSelectionModel.Rows | QtCore.QItemSelectionModel.SelectCurrent)
            selected_rows = self.selectionModel().selectedRows()  # TODO: Allow multi select

        from_index = selected_rows[0]
        if not from_index.isValid():
            return False
        to_index = from_index.siblingAtRow(from_index.row() + 1)
        if not to_index.isValid():
            return False

        # Prevent a curve to be moved down below single points
        model = self.model()
        if model.is_curve_index(from_index) and model.is_point_index(to_index):
            return False

        success = self.moveRow(from_index, to_index)

        # Select the moved row
        if success:
            self.selectionModel().select(to_index, QtCore.QItemSelectionModel.Rows | QtCore.QItemSelectionModel.SelectCurrent)
        return success

    def reverseCurve(self):
        selected_curves, _, _ = self.selectionModel().selectedUnique()
        if not selected_curves:
            selected_curves = self.model().curveIndexes()
        if not selected_curves:
            return

        self.model().blockSignals(True)
        for index in selected_curves:
            curve = self.model().getCurveData(index)
            curve_parsed = reversed(curve)
            if curve == curve_parsed:
                continue

            self.model().editCurveData(index, curve_parsed)

        self.model().blockSignals(False)
        self.model().on_data_changed()

    def mergeCurves(self):
        selected_curves, _, _ = self.selectionModel().selectedUnique()
        if not selected_curves:
            selected_curves = self.model().curveIndexes()
        if not selected_curves or len(selected_curves) < 2:
            return

        # Use the first selected curve as the base for merging
        base_curve_index = selected_curves[0]
        curves_to_merge = sorted(selected_curves[1:], key=lambda x: x.row(), reverse=True)
        if not base_curve_index.isValid() or base_curve_index.parent().isValid():
            return  # Not a valid curve
        self.setExpanded(base_curve_index, False)

        base_curve_item = self.model().itemFromIndex(base_curve_index)

        # Iterate over remaining selected curves and move their points
        self.model().blockSignals(True)
        for index in curves_to_merge:
            self.setExpanded(index, False)
            curve_item = self.model().itemFromIndex(index)
            while curve_item.rowCount() > 0:
                # Move each point from the current curve to the base curve
                row_items = curve_item.takeRow(0)
                base_curve_item.appendRow(row_items)
        self.model().blockSignals(False)

        # Remove the original curves, except for the base curve
        self.model().removeRowsSmart(curves_to_merge, [], [])

    def curvesToPoints(self):
        """
        Split selected curves into standalone points, deleting the original curves.
        """
        selected_curves, _, _ = self.selectionModel().selectedUnique()
        if not selected_curves:
            selected_curves = self.model().curveIndexes()
        if not selected_curves:
            return

        self.model().blockSignals(True)

        for index in selected_curves:
            self.setExpanded(index, False)
            curve_item = self.model().itemFromIndex(index)
            while curve_item.rowCount() > 0:
                # Move each point from the current curve to the base curve
                row_items = curve_item.takeRow(0)
                self.model().appendRow(row_items)

        self.model().blockSignals(False)

        # Remove the original curves
        self.model().removeRowsSmart(selected_curves, [], [])

    def pointsToCurve(self):
        """
        Convert selected points into a new curve, deleting the original points
        """
        _, _, selected_points = self.selectionModel().selectedUnique()
        if not selected_points:
            selected_points = self.model().pointIndexes()
        if not selected_points:
            return

        # Fetch the data before we delete the points
        curve = []
        for index in selected_points:
            curve.append(self.model().getPointData(index))

        self.model().blockSignals(True)

        # Remove the original points
        self.model().removeRowsSmart([], [], selected_points)

        self.model().blockSignals(False)

        # Add new curve (must be after we delete the points!)
        self.model().addCurve(curve)

    def filterRemoveDuplicates(self):
        selected_curves, _, _ = self.selectionModel().selectedUnique()
        if not selected_curves:
            selected_curves = self.model().curveIndexes()
        if not selected_curves:
            return

        def dialog_remove_duplicates():

            inputs = {
                "Point to point tolerance [mm]": 0.002,
                "Compare normals": True,
                "Tolerance for comparing normals [deg]": math.degrees(0.01),
            }

            outputs = robodialogs.InputDialog(
                'Remove subsequent duplicated points. It does not wraps around (point 1 is not compared against point N-1).',
                inputs,
                'Remove Duplicates',
            )
            if outputs is None:
                # User cancelled
                return None
            return outputs

        settings = dialog_remove_duplicates()
        if settings is None:
            return

        [tolerance_mm, check_normals, tolerance_normals_deg] = list(settings.values())

        self.model().blockSignals(True)
        for index in selected_curves:
            curve = self.model().getCurveData(index)
            curve_parsed = cutools.filter_subsequent_duplicated_points(curve, tolerance_mm, check_normals, math.radians(tolerance_normals_deg))
            if curve == curve_parsed:
                continue

            # Update the model
            self.model().editCurveData(index, curve_parsed)

        self.model().blockSignals(False)
        self.model().on_data_changed()

    def filterProjectPoints(self):
        selected_curves, _, _ = self.selectionModel().selectedUnique()
        if not selected_curves:
            selected_curves = self.model().curveIndexes()
        if not selected_curves:
            return

        selected_item = self.model().object_item()
        if not selected_item:
            return

        candidates = sorted([o for o in selected_item.RDK().ItemList(robolink.ITEM_TYPE_OBJECT) if object_has_mesh(o)], key=lambda x: (0 if x.Name() == selected_item.Name() else 1, x.Name()))
        destination_item = selected_item.RDK().ItemUserPick("Select an object to project points to", candidates)
        if not destination_item.Valid():
            return

        def dialog_project_points():

            # Ensure the indexes matches robolink.PROJECTION_NONE, ...
            inputs = {
                "Projection Type": [3, [
                    "No Projection",
                    "Shortest Distance",
                    "Along Normal",
                    "Along Normal + Recalc. Normals",
                    "Shortest Distance + Recalc. Normals",
                    "No Projection + Recalc. Normals (Shortest Distance)",
                    "No Projection + Recalc. Normals (Along Normal)",
                ]]
            }

            outputs = robodialogs.InputDialog("Project points on the object's surface, and recalculate position and normal accordingly.", inputs, 'Project Points')
            if outputs is None:
                # User cancelled
                return None
            return outputs

        settings = dialog_project_points()
        if settings is None:
            return

        project_type = settings["Projection Type"]
        project_on_surface = project_type[0] in [1, 2, 3, 4]
        project_along_normal = project_type[0] in [2, 3, 6]
        recalculate_normals = project_type[0] in [3, 4, 5, 6]

        self.model().blockSignals(True)

        # Curves are relative to the object origin, while AddCurve and ProjectPoints is relative to the object pose

        offset_pose_from = selected_item.Pose()
        offset_pose_to = offset_pose_from.inv()
        if destination_item != selected_item:
            offset_pose_from = (selected_item.PoseAbs().inv() * destination_item.Parent().PoseAbs()) * destination_item.Pose()
            offset_pose_to = (destination_item.PoseAbs().inv() * selected_item.Parent().PoseAbs()) * selected_item.Pose()

        for index in selected_curves:
            curve = self.model().getCurveData(index)
            if not curve:
                continue

            # Move points to the destination coordinate system
            curve_offset = cutools.transform_curve(offset_pose_from, curve)

            curve_parsed = cutools.project_points(curve_offset, destination_item, project_on_surface=project_on_surface, project_along_normal=project_along_normal, recalculate_normals=recalculate_normals)
            if curve_offset == curve_parsed:
                continue

            # Move them back to the source coordinate system
            curve_parsed = cutools.transform_curve(offset_pose_to, curve_parsed)
            if curve == curve_parsed:
                continue

            # Update the model
            self.model().editCurveData(index, curve_parsed)

        self.model().blockSignals(False)
        self.model().on_data_changed()

    def filterOffsetPoints(self):
        """Add a fixed offset to a curve along the IJK vectors"""
        selected_curves, _, _ = self.selectionModel().selectedUnique()
        if not selected_curves:
            selected_curves = self.model().curveIndexes()
        if not selected_curves:
            return

        # Open dialog
        offset = []
        dialog = BulkEditDialog(title="Offset Points", show_ijk=False, parent=self)
        if dialog.exec_():
            offset = dialog.getValues()[:3]
            offset = [x if x else 0 for x in offset]  # None to 0
        else:
            return

        if not offset:
            return False

        self.model().blockSignals(True)
        for index in selected_curves:
            curve = self.model().getCurveData(index)
            curve_parsed = cutools.offset_curve_fixed(curve, offset)
            if curve == curve_parsed:
                continue

            # Update the model
            self.model().editCurveData(index, curve_parsed)

        self.model().blockSignals(False)
        self.model().on_data_changed()

    def filterOffsetPointsIJK(self):
        """Offsets a curve along the IJK vectors."""
        selected_curves, _, _ = self.selectionModel().selectedUnique()
        if not selected_curves:
            selected_curves = self.model().curveIndexes()
        if not selected_curves:
            return

        # Open dialog
        offset = robodialogs.InputDialog("Offset [mm]", 10)
        if not offset:
            return False

        self.model().blockSignals(True)
        for index in selected_curves:
            curve = self.model().getCurveData(index)
            curve_parsed = cutools.offset_curve_ijk(curve, offset)
            if curve == curve_parsed:
                continue

            # Update the model
            self.model().editCurveData(index, curve_parsed)

        self.model().blockSignals(False)
        self.model().on_data_changed()

    def filterOffsetPointsSideways(self):
        """Offsets a curve sideways based on the cross product of direction and IJK vectors."""
        selected_curves, _, _ = self.selectionModel().selectedUnique()
        if not selected_curves:
            selected_curves = self.model().curveIndexes()
        if not selected_curves:
            return

        selected_item = self.model().object_item()
        if not selected_item:
            return

        # Open dialog
        offset = robodialogs.InputDialog("Side Offset [mm]", 10)
        if not offset:
            return False

        self.model().blockSignals(True)
        for index in selected_curves:
            curve = self.model().getCurveData(index)
            curve_parsed = cutools.offset_curve_sideways(curve, offset)
            if curve == curve_parsed:
                continue

            # Update the model
            self.model().editCurveData(index, curve_parsed)

        self.model().blockSignals(False)
        self.model().on_data_changed()

    def filterFlipIJK(self):
        _, selected_curve_points, selected_points = self.selectionModel().selectedExpanded()
        if len(selected_curve_points) + len(selected_points) == 0:
            selected_curve_points, selected_points = [ip for ic in self.model().curveIndexes() for ip in self.model().curvePointIndexes(ic)], self.model().pointIndexes()
        if len(selected_curve_points) + len(selected_points) == 0:
            return

        self.model().blockSignals(True)
        for index in selected_curve_points + selected_points:
            x, y, z, i, j, k = self.model().getPointData(index)
            self.model().editPointData(index, [x, y, z, i * -1, j * -1, k * -1])
        self.model().blockSignals(False)
        self.model().on_data_changed()

    def filterBulkEditPoints(self):
        _, selected_curve_points, selected_points = self.selectionModel().selectedExpanded()
        if len(selected_curve_points) + len(selected_points) == 0:
            selected_curve_points, selected_points = [ip for ic in self.model().curveIndexes() for ip in self.model().curvePointIndexes(ic)], self.model().pointIndexes()
        if len(selected_curve_points) + len(selected_points) == 0:
            return

        # Open dialog
        dialog = BulkEditDialog(title="Bulk Edit Points", show_ijk=True, parent=self)
        if dialog.exec_():
            values = dialog.getValues()
            self.model().blockSignals(True)
            for index in selected_curve_points + selected_points:
                x, y, z, i, j, k = values
                if x is not None:
                    self.model().setData(index.siblingAtColumn(1), x, Qt.EditRole)
                if y is not None:
                    self.model().setData(index.siblingAtColumn(2), y, Qt.EditRole)
                if z is not None:
                    self.model().setData(index.siblingAtColumn(3), z, Qt.EditRole)
                if i is not None:
                    self.model().setData(index.siblingAtColumn(4), i, Qt.EditRole)
                if j is not None:
                    self.model().setData(index.siblingAtColumn(5), j, Qt.EditRole)
                if k is not None:
                    self.model().setData(index.siblingAtColumn(6), k, Qt.EditRole)
            self.model().blockSignals(False)
            self.model().on_data_changed()

    def filterSetNormals(self):
        _, selected_curve_points, selected_points = self.selectionModel().selectedExpanded()
        if len(selected_curve_points) + len(selected_points) == 0:
            selected_curve_points, selected_points = [ip for ic in self.model().curveIndexes() for ip in self.model().curvePointIndexes(ic)], self.model().pointIndexes()
        if len(selected_curve_points) + len(selected_points) == 0:
            return

        # Open dialog to ask for angles
        inputs = {"Phi (0-180) [Tilt/Elevation]": 0.0, "Theta (0-360) [Azimuth/Bearing]": 0.0}
        outputs = robodialogs.InputDialog(
            'Set absolute normals using Polar/Spherical angles (degrees) for all selected points.\n' +
            'This sets the normal direction relative to the WORLD frame (or the object frame), where:\n' +
            '- Phi is the angle between the vector and the Positive Z-axis. (Often corresponds to a "Tilt" or "Elevation" angle from a horizontal plane, but measured from the vertical Z-axis), and\n' +
            '- Theta is the angle in the XY plane from the Positive X-axis. (Often corresponds to a "Azimuth" or "Bearing" angle).',
            inputs,
            'Set Normals (Absolute)'
        )
        if outputs is None:
            return  # User cancelled

        phi = outputs["Phi (0-180) [Tilt/Elevation]"]
        theta = outputs["Theta (0-360) [Azimuth/Bearing]"]
        
        # Clamp phi to its valid range
        phi = max(0, min(180, phi))

        # Convert angles to a normalized IJK vector
        try:
            new_ijk = normal_polar_2_vector(phi, theta)
            new_i, new_j, new_k = new_ijk[0], new_ijk[1], new_ijk[2]
        except Exception as e:
            robodialogs.ShowMessage(f"Invalid angle. Using [0, 0, 1]. Error: {e}")
            new_i, new_j, new_k = 0.0, 0.0, 1.0

        self.model().blockSignals(True)
        for index in selected_curve_points + selected_points:
            x, y, z, _, _, _ = self.model().getPointData(index)  # Get existing XYZ
            self.model().editPointData(index, [x, y, z, new_i, new_j, new_k])  # Set new IJK
        self.model().blockSignals(False)
        self.model().on_data_changed()

    def filterSetNormalsRelative(self):
        _, selected_curve_points, selected_points = self.selectionModel().selectedExpanded()
        if len(selected_curve_points) + len(selected_points) == 0:
            selected_curve_points, selected_points = [ip for ic in self.model().curveIndexes() for ip in self.model().curvePointIndexes(ic)], self.model().pointIndexes()
        if len(selected_curve_points) + len(selected_points) == 0:
            return

        # Open dialog
        inputs = {"Delta Phi (deg) [Tilt/Elevation Change]": 0.0, "Delta Theta (deg) [Azimuth/Bearing Change]": 0.0}
        outputs = robodialogs.InputDialog(
            'Add relative offset to the normal direction using Polar/Spherical angles (degrees).\n' +
            'This rotation is applied relative to the current normal vector direction, where:\n' +
            "- The Tilt/Elevation Change value rotates the normal vector up or down towards the fixed vertical Z-axis (or away from it). This is the change in the vector's elevation or how 'steep' it is, and\n" +
            "- The Azimuth/Bearing Change value rotates the normal vector around the Z-axis. This changes the vector's 'bearing' or compass direction in the XY plane.",
            inputs,
            'Set Normals (Relative)'
        )
        if outputs is None:
            return  # User cancelled

        delta_phi = outputs["Delta Phi (deg) [Tilt/Elevation Change]"]
        delta_theta = outputs["Delta Theta (deg) [Azimuth/Bearing Change]"]

        # If user entered [0,0], there is nothing to do.
        if abs(delta_phi) < 1e-6 and abs(delta_theta) < 1e-6:
            return

        self.model().blockSignals(True)
        for index in selected_curve_points + selected_points:
            x, y, z, old_i, old_j, old_k = self.model().getPointData(index)  # Get existing XYZ and IJK
            
            # Convert current IJK to polar angles
            old_phi, old_theta = normal_vector_2_polar([old_i, old_j, old_k])
            
            # Apply the relative delta
            new_phi = old_phi + delta_phi
            new_theta = old_theta + delta_theta
            
            # Clamp Phi to its [0, 180] degree range
            new_phi = max(0, min(180, new_phi))
            
            # Wrap Theta to its [0, 360] degree range
            new_theta = new_theta % 360
            
            # Convert new angles back to a normalized IJK vector
            try:
                new_ijk = normal_polar_2_vector(new_phi, new_theta)
            except Exception:
                new_ijk = [0.0, 0.0, 1.0] # Fallback

            self.model().editPointData(index, [x, y, z, new_ijk[0], new_ijk[1], new_ijk[2]])  # Set new IJK
            
        self.model().blockSignals(False)
        self.model().on_data_changed()

    def filterSetNormalsTangent(self):
        _, selected_curve_points, selected_points = self.selectionModel().selectedExpanded()
        if len(selected_curve_points) + len(selected_points) == 0:
            selected_curve_points, selected_points = [ip for ic in self.model().curveIndexes() for ip in self.model().curvePointIndexes(ic)], self.model().pointIndexes()
        if len(selected_curve_points) + len(selected_points) == 0:
            return

        # Open dialog
        angle_deg = robodialogs.InputDialog(
            "Enter angle (degrees) to tilt the normal.\n" +
            "The normal will be tilted 'sideways' relative to the curve's direction (around its tangent vector).\n" +
            "This angle acts as a Side/Tilt Angle relative to the path.",
            45.0,
            'Set Normals (Tangent)'
        )
        if angle_deg is None:
            return  # User cancelled

        angle_rad = math.radians(angle_deg)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        self.model().blockSignals(True)

        # Group points by their parent curve to efficiently get curve data
        points_by_parent = {}
        for point_index in selected_curve_points:
            parent_index = point_index.parent()
            if parent_index not in points_by_parent:
                points_by_parent[parent_index] = []
            points_by_parent[parent_index].append(point_index)

        # Now process one curve at a time
        for parent_index, point_indices in points_by_parent.items():
            curve = self.model().getCurveData(parent_index)
            curve_len = len(curve)
            if curve_len < 2:
                continue  # Need at least 2 points for a tangent

            for point_index in point_indices:
                idx = point_index.row()
                x, y, z, i, j, k = curve[idx]  # Get data from the curve list
                current_normal = [i, j, k]
                current_xyz = [x, y, z]

                # Find Tangent (Direction)
                direction = None

                # 1. Look Forward
                if idx < curve_len - 1:
                    # Find the next non-duplicate point
                    for lookahead_idx in range(idx + 1, curve_len):
                        dir_vec = robomath.subs3(curve[lookahead_idx][:3], current_xyz)
                        if robomath.norm(dir_vec) > 1e-6:
                            direction = robomath.normalize3(dir_vec)
                            break

                # 2. Look Backward (if forward failed or we're at the last point)
                if direction is None and idx > 0:
                    # Find the previous non-duplicate point
                    for lookback_idx in range(idx - 1, -1, -1):
                        dir_vec = robomath.subs3(current_xyz, curve[lookback_idx][:3])
                        if robomath.norm(dir_vec) > 1e-6:
                            direction = robomath.normalize3(dir_vec)
                            break

                if direction is None:
                    # Can't find a tangent (e.g., isolated point, or all points in curve are identical)
                    continue
                # End Tangent logic

                # Calculate New Normal
                side_direction = [0, 0, 0]
                try:
                    # Get the "sideways" vector: Side = cross(Normal, Tangent)
                    side_direction = robomath.normalize3(robomath.cross(current_normal, direction))
                except Exception:
                    # Normal and tangent are parallel
                    continue  # Skip this point

                # New_Normal = cos(angle) * Old_Normal + sin(angle) * Side_Vector
                new_i = cos_a * current_normal[0] + sin_a * side_direction[0]
                new_j = cos_a * current_normal[1] + sin_a * side_direction[1]
                new_k = cos_a * current_normal[2] + sin_a * side_direction[2]

                new_normal = robomath.normalize3([new_i, new_j, new_k])

                # Update the model for this specific point
                self.model().editPointData(point_index, [x, y, z, new_normal[0], new_normal[1], new_normal[2]])

        self.model().blockSignals(False)
        self.model().on_data_changed()
    
    def filterAverageNormals(self):
        _, selected_curve_points, selected_points = self.selectionModel().selectedExpanded()
        if len(selected_curve_points) + len(selected_points) == 0:
            selected_curve_points, selected_points = [ip for ic in self.model().curveIndexes() for ip in self.model().curvePointIndexes(ic)], self.model().pointIndexes()
        if len(selected_curve_points) + len(selected_points) == 0:
            return

        # Open dialog
        filter_size_str = robodialogs.mbox(
            "Enter the filter size (the number of points/normals used for the average filter).\n" +
            "For example, a size of 10 will average each point with 5 neighbors on each side.",
            entry="10"
        )
        if not filter_size_str:
            return  # User cancelled
        
        try:
            filter_size = int(filter_size_str)
            if filter_size <= 0:
                raise ValueError
        except ValueError:
            robodialogs.ShowMessage("Invalid filter size. Please enter a positive number.")
            return
            
        self.model().blockSignals(True)

        # Group points by their parent curve to efficiently get curve data
        points_by_parent = {}
        for point_index in selected_curve_points:
            parent_index = point_index.parent()
            if parent_index not in points_by_parent:
                points_by_parent[parent_index] = []
            points_by_parent[parent_index].append(point_index)
        
        # Process one curve at a time
        for parent_index, point_indices in points_by_parent.items():
            curve = self.model().getCurveData(parent_index)
            curve_len = len(curve)
            if curve_len < 1:
                continue

            # We create a new list so that the averaging calculations all use the original, non-averaged normals.
            new_curve_points = curve.copy()
            
            # Create a set of rows for quick lookup
            selected_rows = set(p.row() for p in point_indices)

            for idx in selected_rows:
                # Calculate the window for averaging
                id_avg_from = round(max(0, idx - 0.5 * filter_size))
                id_avg_to = round(min(curve_len - 1, idx + 0.5 * filter_size))
                
                sum_normals = [0, 0, 0]

                # Sum all normals within the window
                for j in range(id_avg_from, id_avg_to + 1):
                    # Use the original curve data for the calculation
                    n_j = curve[j][3:6] 
                    sum_normals = robomath.add3(sum_normals, n_j)
                
                try:
                    # Normalize the sum
                    avg_normal = robomath.normalize3(sum_normals)
                except Exception:
                    avg_normal = [0, 0, 1] # Fallback
                
                # Get the original XYZ
                x, y, z = curve[idx][:3]
                
                # Store the new point in our new_curve_points list
                new_curve_points[idx] = [x, y, z, avg_normal[0], avg_normal[1], avg_normal[2]]

            # Update the model with the new curve data
            self.model().editCurveData(parent_index, new_curve_points)

        self.model().blockSignals(False)
        self.model().on_data_changed()

    def filterResampleCurve(self):
        selected_curves, selected_curve_points, _ = self.selectionModel().selectedUnique()
        parent_curves = set(selected_curves)
        for cp in selected_curve_points:
            parent_curves.add(cp.parent())
        
        curves_to_process = list(parent_curves)

        if not curves_to_process:
            robodialogs.ShowMessage("This operation requires selecting one or more curves (or points within a curve).")
            return

        # Open dialog
        step_mm = robodialogs.InputDialog(
            "Enter the desired step size (mm) between points.\n" +
            "New points will be added to the curve.",
            5.0  # Default to 5mm
        )
        if step_mm is None or step_mm <= 1e-3:
            return  # User cancelled or invalid value

        self.model().blockSignals(True)
        
        for index in curves_to_process:
            curve = self.model().getCurveData(index)
            if not curve or len(curve) < 2:
                continue  # Need at least 2 points to resample

            resampled_curve = []
            
            for i in range(len(curve) - 1):
                # Get start and end point of the segment
                p_start = curve[i]
                p_end = curve[i+1]
                
                xyz_start = p_start[:3]
                xyz_end = p_end[:3]
                
                # Default normals if not present
                ijk_start = p_start[3:6] if len(p_start) >= 6 else [0, 0, 1]
                ijk_end = p_end[3:6] if len(p_end) >= 6 else [0, 0, 1]

                # Add the first point of the segment
                resampled_curve.append(p_start)

                segment_length = robomath.distance(xyz_start, xyz_end)
                if segment_length <= step_mm:
                    # Segment is shorter than or equal to the step size.
                    # No new points needed, just continue.
                    # The end point (p_end) will be added as the p_start of the next loop.
                    continue
                
                # Calculate how many new points to add
                num_steps = int(math.floor(segment_length / step_mm))
                
                # Get the direction vector for position and normal
                dir_vec = robomath.subs3(xyz_end, xyz_start)
                normal_vec = robomath.subs3(ijk_end, ijk_start)
                
                for j in range(1, num_steps + 1):
                    # Calculate the interpolation ratio (0.0 to 1.0)
                    ratio = (j * step_mm) / segment_length
                    
                    # For the last point, use a ratio of 1.0 to avoid precision errors
                    if j == num_steps:
                         # If the last step is very close to the end, just skip it.
                         # The p_end point will be added by the next loop.
                        if (segment_length - (j * step_mm)) < (step_mm * 0.5):
                            continue
                            
                    # Interpolate XYZ position
                    new_xyz = robomath.add3(xyz_start, robomath.mult3(dir_vec, ratio))
                    
                    # Interpolate IJK normal (linear interpolation)
                    interp_ijk = robomath.add3(ijk_start, robomath.mult3(normal_vec, ratio))
                    new_ijk = robomath.normalize3(interp_ijk) # Re-normalize the interpolated vector
                    
                    resampled_curve.append(new_xyz + new_ijk)

            # Add the very last point of the original curve
            resampled_curve.append(curve[-1])

            # Update the model with the new resampled curve
            self.model().editCurveData(index, resampled_curve)

        self.model().blockSignals(False)
        self.model().on_data_changed()
    
    def filterResampleByFactor(self):
        """
        Curve Filter

        Splits every segment in the selected curves into N equal-length segments
        by inserting N-1 points using linear interpolation (Oversampling).
        """
        selected_curves, selected_curve_points, _ = self.selectionModel().selectedUnique()
        parent_curves = set(selected_curves)
        for cp in selected_curve_points:
            parent_curves.add(cp.parent())

        curves_to_process = list(parent_curves)

        if not curves_to_process:
            robodialogs.ShowMessage("This operation requires selecting one or more curves (or points within a curve).")
            return

        # Open dialog for factor N
        factor_n_raw = robodialogs.InputDialog(
            "Enter the factor (N) to split each segment (N parts, N-1 new points).\n" +
            "A factor of 2 will double the number of segments (x2 points).",
            2  # Default to split in half
        )
        try:
            factor_n = int(factor_n_raw)
            if factor_n < 2:
                robodialogs.ShowMessage("Factor must be an integer greater than 1.")
                return
        except (TypeError, ValueError):
            return # User cancelled or invalid input
            
        self.model().blockSignals(True)

        for index in curves_to_process:
            curve = self.model().getCurveData(index)
            if not curve or len(curve) < 2:
                continue

            resampled_curve = []
            num_insert_points = factor_n - 1

            for i in range(len(curve) - 1):
                p_start = curve[i]
                p_end = curve[i + 1]

                xyz_start = p_start[:3]
                ijk_start = p_start[3:6] if len(p_start) >= 6 else [0, 0, 1]
                
                xyz_end = p_end[:3]
                ijk_end = p_end[3:6] if len(p_end) >= 6 else [0, 0, 1]

                # Add the start point of the segment
                resampled_curve.append(p_start)

                # Get the difference vectors for linear interpolation
                dir_vec = robomath.subs3(xyz_end, xyz_start)
                normal_vec = robomath.subs3(ijk_end, ijk_start)

                for j in range(1, num_insert_points + 1):
                    # Calculate the interpolation ratio (1/N, 2/N, ..., (N-1)/N)
                    ratio = j / factor_n

                    # Interpolate XYZ position
                    new_xyz = robomath.add3(xyz_start, robomath.mult3(dir_vec, ratio))

                    # Interpolate IJK normal (linear interpolation and re-normalize)
                    interp_ijk = robomath.add3(ijk_start, robomath.mult3(normal_vec, ratio))
                    new_ijk = robomath.normalize3(interp_ijk)

                    resampled_curve.append(new_xyz + new_ijk)

            # Add the very last point of the original curve (p_end of the last segment)
            if curve:
                resampled_curve.append(curve[-1])

            # Update the model with the new resampled curve
            self.model().editCurveData(index, resampled_curve)

        self.model().blockSignals(False)
        self.model().on_data_changed()

    def filterCCMASmoothing(self):
        """
        Curve Filter
        
        CCMA smoothing filter for 2D/3D paths.
        Smooths the path while correcting inwards bending using the CCMA algorithm.
        """   
        import ccma   
        selected_curves, _, _ = self.selectionModel().selectedUnique()
        if not selected_curves:
            selected_curves = self.model().curveIndexes()
        if not selected_curves:
            return
        
        # Dialog to get CCMA parameters
        inputs = {
            "MA Window Width (w_ma)": 5,
            "CC Window Width (w_cc)": 3,
            "Kernel Type": [3, ["normal", "uniform", "pascal", "hanning"]],
            "Boundary Mode": [0, ["padding", "wrapping", "fill_boundary", "none"]]
        }

        outputs = robodialogs.InputDialog('Smooth 2D/3D paths while correcting inwards bending.', inputs, 'CCMA Smoothing')
        if outputs is None:
            return

        w_ma = int(outputs["MA Window Width (w_ma)"])
        w_cc = int(outputs["CC Window Width (w_cc)"])
        i = outputs["Kernel Type"][0]
        distrib = outputs["Kernel Type"][1][i]
        j = outputs["Boundary Mode"][0]
        mode = outputs["Boundary Mode"][1][j]

        print(f"DEBUG: Kernel Type received: '{distrib}' (Length: {len(distrib)})")
        print(f"DEBUG: Boundary Mode received: '{mode}' (Length: {len(mode)})")

        # Initialize the filter
        ccma_var = ccma.CCMA(w_ma=w_ma, w_cc=w_cc, distrib=distrib)
        self.model().blockSignals(True)
        for index in selected_curves:
            # 1. Get current curve data as a list of [x, y, z, i, j, k]
            curve_data = self.model().getCurveData(index)
            if len(curve_data) < (w_ma + w_cc + 1) * 2:
                continue
            
            # 2. Extract XYZ for smoothing (CCMA operates on coordinates)
            points_np = np.array([p[:3] for p in curve_data])
            normals_np = np.array([p[3:6] for p in curve_data])
        
            # 3. Apply Filter
            smoothed_xyz = ccma_var.filter(points_np, mode=mode, cc_mode=True)
            smoothed_normals = []
            for i in range(len(normals_np)):
                start = max(0, i - w_ma)
                end = min(len(normals_np), i + w_ma + 1)
                avg_n = np.mean(normals_np[start:end], axis=0)
                smoothed_normals.append(robomath.normalize3(avg_n.tolist()))
        
            # 4. Reconstruct points. 
            # Note: If CCMA changes the number of points (mode='none'), we use dummy normals.
            # If mode='padding' or 'fill_boundary', length is preserved.
            new_curve = []
            result_len = len(smoothed_xyz)
            for i in range(result_len):
                if i < len(smoothed_normals):
                    target_normal = smoothed_normals[i]
                else:
                    target_normal = [0, 0, 1]
                # If length is preserved, keep original normals, otherwise use [0,0,1]
                new_curve.append(list(smoothed_xyz[i]) + list(target_normal))

            # 5. Update the model
            self.model().editCurveData(index, new_curve)

        self.model().blockSignals(False)
        self.model().on_data_changed()
    
    def filterBSplineSmoothing(self):
        from scipy.interpolate import splprep, splev
        
        selected_curves, _, _ = self.selectionModel().selectedUnique()
        if not selected_curves:
            selected_curves = self.model().curveIndexes()

        s_factor = robodialogs.InputDialog("Smoothing Factor: Higher is smoother but less accurate.", 500.0)
        if s_factor is None:
            return

        self.model().blockSignals(True)
        for index in selected_curves:
            curve_data = self.model().getCurveData(index)
            if len(curve_data) < 5:
                continue
        
            pts = np.array(curve_data)
            x, y, z = pts[:, 0], pts[:, 1], pts[:, 2]
            i_comp, j_comp, k_comp = pts[:, 3], pts[:, 4], pts[:, 5]
            ijk = np.column_stack((i_comp, j_comp, k_comp))

            tckp, u = splprep([x, y, z], s=s_factor, k=3)
            new_xyz = splev(u, tckp)

            if np.sum(np.std(ijk, axis=0)) > 1e-6:
                # TODO: Albert comment: I get this error
                # ValueError: Invalid inputs.
                # The data needs to be sorted?
                tckn, un = splprep([i_comp, j_comp, k_comp], s=s_factor, k=3)
                new_ijk_raw = splev(u, tckn)
                for idx in range(len(new_ijk_raw[0])):
                    norm = [new_ijk_raw[0][idx], new_ijk_raw[1][idx], new_ijk_raw[2][idx]]
            
            else:
                for idx in range(len(ijk[0])):
                    norm = [ijk[0][idx], ijk[1][idx], ijk[2][idx]]

            smoothed_curve = []
            for idx in range(len(new_xyz[0])):
                pos = [new_xyz[0][idx], new_xyz[1][idx], new_xyz[2][idx]]
                norm = robomath.normalize3(norm)
                smoothed_curve.append(pos + norm)

            self.model().editCurveData(index, smoothed_curve)

        self.model().blockSignals(False)
        self.model().on_data_changed()

    def filterStraightLines(self):
        """
        Curve Filter

        Remove intermediary points in what is considered a straight line.
        The normal of subsequent points must be equal to count as a line, unless specified otherwise.
        The first and last point will never be altered.
        """
        selected_curves, _, _ = self.selectionModel().selectedUnique()
        if not selected_curves:
            selected_curves = self.model().curveIndexes()
        if not selected_curves:
            return

        def dialog_filter_straight_lines():
            inputs = {
                "Point to point tolerance [deg]": 1,
                "Compare normals": True,
                "Tolerance for comparing normals [deg]": 0.5,
            }

            outputs = robodialogs.InputDialog(
                'Remove intermediary points in what is considered a straight line. The normal of subsequent points must be equal to count as a line, unless specified otherwise. The first and last point will never be altered.',
                inputs,
                'Filter Straight Lines',
            )
            if outputs is None:
                # User cancelled
                return None
            return outputs

        settings = dialog_filter_straight_lines()
        if settings is None:
            return

        [tolerance_line_deg, check_normals, tolerance_normals_deg] = list(settings.values())

        self.model().blockSignals(True)
        for curve_index in selected_curves:
            curve = self.model().getCurveData(curve_index)
            if curve is None:
                continue

            filtered_curve = cutools.filter_straight_lines(curve, math.radians(tolerance_line_deg), check_normals, math.radians(tolerance_normals_deg))
            if curve == filtered_curve:
                continue

            self.model().editCurveData(curve_index, curve)

        self.model().blockSignals(False)
        self.model().on_data_changed()

    def filterSortCurves(self):
        """
        Curve Filter

        Sort the order of curves (re-order indexes) by distance from the end of a segment to the start of the next segment.
        Optionally, check both ends of the segments and reverse the order of curve.
        """
        # Process all curves, as there is no convenient way to "remember" the original indexes
        selected_curves = self.model().curveIndexes()
        if not selected_curves or len(selected_curves) <= 1:
            return

        def dialog_filter_curve_segments():
            inputs = {
                "Check both ends of segments (allow reversing curves)": False,
            }

            outputs = robodialogs.InputDialog(
                'Sort the order of all curves (re-order indexes) by distance from the end of a curve to the start of the next curve. The first curve is left untouched and is the starting point.',
                inputs,
                'Sort Curves',
            )
            if outputs is None:
                # User cancelled
                return None
            return outputs

        settings = dialog_filter_curve_segments()
        if settings is None:
            return

        [reverse_segments] = list(settings.values())

        curves, points = self.model().getData()

        filtered_curves = cutools.sort_curve_segments(curves, start=curves[0], reverse_segments=reverse_segments)
        if curves == filtered_curves:
            return

        self.model().blockSignals(True)
        for curve_index, filtered_curve in zip(selected_curves, filtered_curves):
            self.model().editCurveData(curve_index, filtered_curve)

        self.model().blockSignals(False)
        self.model().on_data_changed()

    def filterSplitDiscontinuousCurves(self):
        """
        Curve Filter

        Split/group segments into separate curves objects based on continuity.
        """
        selected_item = self.model().object_item()
        if not selected_item:
            return

        # Process all curves, as there is no convenient way to "remember" the original indexes
        selected_curves = self.model().curveIndexes()
        if not selected_curves or len(selected_curves) <= 1:
            return

        def dialog_filter_split_curve_segments():
            inputs = {
                "Tolerance to split [mm]": 50.0,
            }

            outputs = robodialogs.InputDialog(
                'Split/group all segments into separate (new) curve objects based on continuity. The first curve is used as the starting point. It is recommended to sort the curves first. The source object is left untouched.',
                inputs,
                'Split/Group Curves',
            )
            if outputs is None:
                # User cancelled
                return None
            return outputs

        settings = dialog_filter_split_curve_segments()
        if settings is None:
            return

        [tolerance_mm] = list(settings.values())

        curves, points = self.model().getData()

        grouped_curves = cutools.split_discontinuous_curves(curves, start=curves[0], tolerance_mm=tolerance_mm)
        if not grouped_curves:
            return

        selected_item.RDK().Render(False)
        parent = selected_item.Parent()
        pose = selected_item.Pose()
        for i, group in enumerate(grouped_curves):
            if not group:
                continue

            sorted_object_item = selected_item.RDK().AddCurve(group[0])
            sorted_object_item.setName(selected_item.Name() + f' {i}')
            sorted_object_item.setParent(parent)
            sorted_object_item.setVisible(False)

            for curve in group[1:]:
                cutools.add_curve(sorted_object_item, curve, True, robolink.PROJECTION_NONE)

            sorted_object_item.setPose(pose)  # Must be after AddCurve
            sorted_object_item.setVisible(True)  # There is a bug in RoboDK where the resulting object does not show the curve icon, toggling visibility is a workaround

        selected_item.RDK().setSelection([selected_item])
        selected_item.RDK().Render(True)

    def convertToTargets(self):
        """
        Convert

        Convert curves and points to robot targets
        """
        selected_item = self.model().object_item()
        if not selected_item:
            return

        selected_curves, selected_curve_points, selected_points = self.selectionModel().selectedUnique()
        if not selected_curves and not selected_curve_points and not selected_points:
            selected_curves = self.model().curveIndexes()
            selected_points = self.model().pointIndexes()
            selected_curve_points = []
        if not selected_curves and not selected_curve_points and not selected_points:
            return

        def dialog_filter_split_curve_segments():
            inputs = {
                "Invert Tool Z+ axis": True,
            }

            outputs = robodialogs.InputDialog(
                'Convert selection to robot Targets. Tool Z+ axis will be aligned with the points normal.',
                inputs,
                'Convert to Targets',
            )
            if outputs is None:
                # User cancelled
                return None
            return outputs

        settings = dialog_filter_split_curve_segments()
        if settings is None:
            return

        curves = [self.model().getCurveData(ci) for ci in selected_curves] + [self.model().getPointData(pi) for pi in selected_curve_points + selected_points]

        [invert] = list(settings.values())

        RDK = selected_item.RDK()
        RDK.Render(False)

        # TODO: For curves, use the direction vector for XY (like offset_curve_sideways)
        pose = selected_item.Pose()
        for i, points in enumerate(curves):
            for j, point in enumerate(points):
                xyz = point[:3]
                ijk = point[3:6]
                if invert:
                    ijk = robomath.mult3(ijk, -1)

                target = RDK.AddTarget(f'{selected_item.Name()} {i+1} {j+1}', selected_item.Parent())
                target.setPose(pose * robomath.point_Zaxis_2_pose(xyz, ijk))

        RDK.Render(True)

    def loadSVG(self):
        curves = cutools.load_svg()
        if not curves:
            return

        selected_item = self.model().object_item(allow_new=True)  # Get or create a new container object of the curves
        for i, curve in enumerate(curves):
            cutools.add_curve(selected_item, curve, add_to_ref=True, projection_type=robolink.PROJECTION_NONE)

    def loadCSVCurves(self):
        curves = cutools.load_curves()
        if not curves:
            return

        selected_item = self.model().object_item(allow_new=True)  # Get or create a new container object of the curves
        for i, curve in enumerate(curves):
            cutools.add_curve(selected_item, curve, add_to_ref=True, projection_type=robolink.PROJECTION_NONE)

    def loadCSVPoints(self):
        points = cutools.load_points()
        if not points:
            return

        selected_item = self.model().object_item(allow_new=True)  # Get or create a new container object of the curves
        cutools.add_points(selected_item, points, add_to_ref=True, projection_type=robolink.PROJECTION_NONE)

    def loadDXF(self):
        cutools.LoadDXF()

    def loadProgram(self):
        curves = cutools.load_program()
        if not curves:
            return

        selected_item = self.model().object_item(allow_new=True)  # Get or create a new container object of the curves
        for i, curve in enumerate(curves):
            cutools.add_curve(selected_item, curve, add_to_ref=True, projection_type=robolink.PROJECTION_NONE)


class QCurvesItemModel(QtGui.QStandardItemModel):

    COLS = {0: '', 1: "X", 2: "Y", 3: "Z", 4: "I", 5: "J", 6: "K", 7: "φ", 8: "θ", 9: "Rel. Dist.", 10: "Tot. Dist."}
    COLS2 = {v: k for k, v in COLS.items()}

    class DataTypes(Enum):
        POINT = auto()
        CURVE = auto()
        CURVE_POINT = auto()

    def __init__(self, RDK, parent=None) -> None:
        super(QCurvesItemModel, self).__init__(parent)

        self.setHorizontalHeaderLabels(list(self.COLS.values()))

        self.selected_item = None
        self.original_curves = []

        self.RDK = RDK

        self.RDKM = RoboDKManager(self.RDK)
        app = QtWidgets.QApplication.instance()
        app.aboutToQuit.connect(self.RDKM.hard_clear_temporary_items)

        self.dataChanged.connect(self.on_data_changed)
        self.rowsInserted.connect(self.on_rows_changed)
        self.rowsMoved.connect(self.on_rows_changed)
        self.rowsRemoved.connect(self.on_rows_changed)

    def on_rows_changed(self, *args, **kwargs):
        self.on_data_changed(roles=[Qt.EditRole])

    def on_data_changed(self, top_left=-1, bottom_right=-1, roles=[Qt.EditRole]):
        if self.signalsBlocked():
            return

        if not roles or Qt.EditRole not in roles:
            return

        if DEBUG_LEVEL:
            print('on_data_changed')

        self.updateDistanceColumns()
        self.updateRowColors()
        self.updateRoboDK()

    def __del__(self):
        self.clear_object_item()

    def is_point_index(self, index: QtCore.QModelIndex):
        return index.isValid() and not index.parent().isValid() and not index.child(0, 0).isValid()

    def is_curve_index(self, index: QtCore.QModelIndex):
        return index.isValid() and not index.parent().isValid() and index.child(0, 0).isValid()

    def is_curve_point_index(self, index: QtCore.QModelIndex):
        return index.isValid() and index.parent().isValid() and not index.child(0, 0).isValid()

    def index_data_type(self, index: QtCore.QModelIndex):
        if self.is_point_index(index):
            return QCurvesItemModel.DataTypes.POINT
        elif self.is_curve_index(index):
            return QCurvesItemModel.DataTypes.CURVE
        elif self.is_curve_point_index(index):
            return QCurvesItemModel.DataTypes.CURVE_POINT
        raise

    def curveCount(self):
        return len(self.curveIndexes())

    def pointCount(self):
        return len(self.pointIndexes())

    def curveIndexes(self):
        indexes = []
        index = self.index(0, 0)  # sibling is less expensive
        for row_i in range(self.rowCount()):
            row_index = index.siblingAtRow(row_i)
            if self.is_curve_index(row_index):
                indexes.append(row_index)
        return indexes

    def curvePointIndexes(self, curve_index):
        if not self.is_curve_index(curve_index):
            return None

        indexes = []
        for i in range(self.rowCount(curve_index)):
            indexes.append(curve_index.child(i, 0))
        return indexes

    def pointIndexes(self):
        indexes = []
        index = self.index(0, 0)  # sibling is less expensive
        for row_i in range(self.rowCount()):
            row_index = index.siblingAtRow(row_i)
            if self.is_point_index(row_index):
                indexes.append(row_index)
        return indexes

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlags:
        if not index.isValid():
            return QtGui.Qt.ItemFlag.NoItemFlags

        if self.data(index, QtGui.Qt.DisplayRole) is None or index.column() == 0 or not self.COLS.get(index.column(), '_') in 'XYZφθ':
            return QtGui.Qt.ItemFlag.ItemIsSelectable | QtGui.Qt.ItemFlag.ItemIsEnabled

        return QtGui.Qt.ItemFlag.ItemIsSelectable | QtGui.Qt.ItemFlag.ItemIsEditable | QtGui.Qt.ItemFlag.ItemIsEnabled

    def headerData(self, section, orientation, role):
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        return super().headerData(section, orientation, role)

    def updateRoboDKSelectionHighlights(self, selected_curves, selected_curve_points, selected_points):
        if not self.object_item():
            return

        if DEBUG_LEVEL:
            print('updateRoboDKSelectionHighlights')

        # From model indexes to indexes in the data
        selected_curves = list(set([index.row() for index in selected_curves]))
        selected_curve_points = list(set([(index.parent().row(), index.row()) for index in selected_curve_points]))

        c_count = self.curveCount()
        selected_points = list(set([index.row() - c_count for index in selected_points]))

        self.RDKM.update_object_previews(self.selected_item, selected_curves, selected_curve_points, selected_points)

    def updateRoboDK(self):

        if self.signalsBlocked():
            return

        # TODO: Revert curve color

        if not self.object_item():
            return

        if DEBUG_LEVEL:
            print('Updating RoboDK')

        # We can't really apply only the change from 1 cell, we need to overwrite all the curves!
        curves, points = self.getData()

        self.RDKM.update_object(self.selected_item, curves, points)

    def object_item(self, allow_new=False):
        if not self.selected_item and not allow_new:
            return None

        if self.selected_item and not self.selected_item.Valid(True):
            self.clear_object_item()

        if not self.selected_item and allow_new:
            self.RDK.Render(False)
            self.RDK.setSelection([])
            self.selected_item = self.RDK.AddCurve([[0, 0, 0], [0, 0, 0]])
            #self.selected_item.setPose(robomath.eye(4))
            self.selected_item.setParam('Reset', 'Curves')
            self.RDK.setSelection([self.selected_item])
            self.RDK.Render(True)

        return self.selected_item

    def clear_object_item(self):
        if not self.selected_item:
            return

        self.RDKM.clear_object_previews(self.selected_item)
        self.selected_item = None

    def editPointData(self, index: QtCore.QModelIndex, point):
        """Edit an existing point"""
        if not self.is_point_index(index) and not self.is_curve_point_index(index):
            return False

        signal_blocked = self.signalsBlocked()
        self.blockSignals(True)

        x, y, z, i, j, k = point[:6]
        self.setData(index.siblingAtColumn(1), x, Qt.EditRole)
        self.setData(index.siblingAtColumn(2), y, Qt.EditRole)
        self.setData(index.siblingAtColumn(3), z, Qt.EditRole)
        self.setData(index.siblingAtColumn(4), i, Qt.EditRole)
        self.setData(index.siblingAtColumn(5), j, Qt.EditRole)
        self.setData(index.siblingAtColumn(6), k, Qt.EditRole)
        # NOTE: I, J, and K will force recalculate theta and phi 3 times!

        self.blockSignals(signal_blocked)
        if not signal_blocked:
            self.dataChanged.emit(-1, -1, [Qt.EditRole])

        return True

    def editCurveData(self, index: QtCore.QModelIndex, curve):
        """Edit an existing curve. If the length of the curve has changed, new rows are added."""
        if not self.is_curve_index(index):
            return False

        signal_blocked = self.signalsBlocked()
        self.blockSignals(True)

        point_count = self.rowCount(index)
        curve_item = self.itemFromIndex(index)
        for ip, point in enumerate(curve):
            if ip >= point_count:
                point_row = self.create_point_row(point)
                curve_item.appendRow(point_row)
            else:
                self.editPointData(self.index(ip, 0, index), point)

        self.blockSignals(signal_blocked)
        if not signal_blocked:
            self.rowsInserted.emit(-1, -1, -1)
            #self.dataChanged.emit(-1, -1, [Qt.EditRole])

        return True

    def setData(self, index: QtCore.QModelIndex, value, role: int = ...) -> bool:

        if role != Qt.EditRole or not index.isValid() or (not self.is_point_index(index) and not self.is_curve_point_index(index)):
            return super().setData(index, value, role)

        current_value = self.data(index, Qt.DisplayRole)
        if value == current_value:
            # No need to trigger data changed
            return True

        # Update IJK and phi/theta
        # NOTE: This can create nested loops!
        # Curves will be updated using IJK, thus update phi/theta (but dont change IJK!)
        # User will edit using phi/theta, thus update IJK (but dont change phi/theta!)

        column = index.column()
        column_name = self.COLS.get(column, '')
        if column_name in ['I', 'J', 'K']:

            if DEBUG_LEVEL > 0:
                print("IJK")

            # Editing I, J or K. Update phi and theta
            i_index = index.siblingAtColumn(self.COLS2['I'])
            j_index = index.siblingAtColumn(self.COLS2['J'])
            k_index = index.siblingAtColumn(self.COLS2['K'])
            phi_index = index.siblingAtColumn(self.COLS2['φ'])
            theta_index = index.siblingAtColumn(self.COLS2['θ'])

            i = self.data(i_index, Qt.DisplayRole)
            j = self.data(j_index, Qt.DisplayRole)
            k = self.data(k_index, Qt.DisplayRole)
            phi = self.data(phi_index, Qt.DisplayRole)
            theta = self.data(theta_index, Qt.DisplayRole)

            normalized_i, normalized_j, normalized_k = (value if column_name == "I" else i), (value if column_name == "J" else j), (value if column_name == "K" else k)
            normalized_phi, normalized_theta = normal_vector_2_polar([normalized_i, normalized_j, normalized_k])

            blocked = self.signalsBlocked()
            self.blockSignals(True)

            super().setData(phi_index, normalized_phi, Qt.EditRole)
            super().setData(theta_index, normalized_theta, Qt.EditRole)

            self.blockSignals(blocked)

        elif column_name in ["φ", "θ"]:

            if DEBUG_LEVEL > 0:
                print("POLAR")

            # Editing phi or theta. Update IJK
            i_index = index.siblingAtColumn(self.COLS2['I'])
            j_index = index.siblingAtColumn(self.COLS2['J'])
            k_index = index.siblingAtColumn(self.COLS2['K'])
            phi_index = index.siblingAtColumn(self.COLS2['φ'])
            theta_index = index.siblingAtColumn(self.COLS2['θ'])

            i = self.data(i_index, Qt.DisplayRole)
            j = self.data(j_index, Qt.DisplayRole)
            k = self.data(k_index, Qt.DisplayRole)
            phi = self.data(phi_index, Qt.DisplayRole)
            theta = self.data(theta_index, Qt.DisplayRole)

            normalized_phi, normalized_theta = (value if column_name == "φ" else phi), (value if column_name == "θ" else theta)
            normalized_i, normalized_j, normalized_k = normal_polar_2_vector(normalized_phi, normalized_theta)

            # Update the model with normalized values
            blocked = self.signalsBlocked()
            self.blockSignals(True)

            super().setData(i_index, normalized_i, Qt.EditRole)
            super().setData(j_index, normalized_j, Qt.EditRole)
            super().setData(k_index, normalized_k, Qt.EditRole)

            self.blockSignals(blocked)

        return super().setData(index, value, role)

    def getData(self):
        curves = [self.getCurveData(ci) for ci in self.curveIndexes()]
        points = [self.getPointData(pi) for pi in self.pointIndexes()]
        return curves, points

    def getCurveData(self, curve_index):
        if not self.is_curve_index(curve_index):
            return None

        return [self.getPointData(pi) for pi in self.curvePointIndexes(curve_index)]

    def getPointData(self, point_index):
        if not self.is_point_index(point_index) and not self.is_curve_point_index(point_index):
            return None

        x = self.data(point_index.siblingAtColumn(1), QtGui.Qt.DisplayRole)
        y = self.data(point_index.siblingAtColumn(2), QtGui.Qt.DisplayRole)
        z = self.data(point_index.siblingAtColumn(3), QtGui.Qt.DisplayRole)
        i = self.data(point_index.siblingAtColumn(4), QtGui.Qt.DisplayRole)
        j = self.data(point_index.siblingAtColumn(5), QtGui.Qt.DisplayRole)
        k = self.data(point_index.siblingAtColumn(6), QtGui.Qt.DisplayRole)

        return [x, y, z, i, j, k]

    def append(self, curves, points):
        if not curves and not points or not self.selected_item:
            return

        curr_curves, curr_points = self.getData()
        self.load(curr_curves + curves, curr_points + points)

    def create_point_row(self, point):
        x, y, z = point[:3]
        i, j, k = point[3:6]
        phi, theta = normal_vector_2_polar([i, j, k])

        point_node = QtGui.QStandardItem('Point')
        point_node.setEditable(False)

        child_X = QtGui.QStandardItem()
        child_Y = QtGui.QStandardItem()
        child_Z = QtGui.QStandardItem()
        child_X.setData(x, QtGui.Qt.EditRole)
        child_Y.setData(y, QtGui.Qt.EditRole)
        child_Z.setData(z, QtGui.Qt.EditRole)
        child_X.setData(QtCore.Qt.AlignRight, QtCore.Qt.TextAlignmentRole)
        child_Y.setData(QtCore.Qt.AlignRight, QtCore.Qt.TextAlignmentRole)
        child_Z.setData(QtCore.Qt.AlignRight, QtCore.Qt.TextAlignmentRole)
        child_X.setEditable(True)
        child_Y.setEditable(True)
        child_Z.setEditable(True)

        child_I = QtGui.QStandardItem()
        child_J = QtGui.QStandardItem()
        child_K = QtGui.QStandardItem()
        child_I.setData(i, QtGui.Qt.EditRole)
        child_J.setData(j, QtGui.Qt.EditRole)
        child_K.setData(k, QtGui.Qt.EditRole)
        child_I.setData(QtCore.Qt.AlignRight, QtCore.Qt.TextAlignmentRole)
        child_J.setData(QtCore.Qt.AlignRight, QtCore.Qt.TextAlignmentRole)
        child_K.setData(QtCore.Qt.AlignRight, QtCore.Qt.TextAlignmentRole)
        child_I.setEditable(False)
        child_J.setEditable(False)
        child_K.setEditable(False)

        child_psi = QtGui.QStandardItem()
        child_theta = QtGui.QStandardItem()
        child_psi.setData(phi, QtGui.Qt.EditRole)
        child_theta.setData(theta, QtGui.Qt.EditRole)
        child_psi.setData(QtCore.Qt.AlignRight, QtCore.Qt.TextAlignmentRole)
        child_theta.setData(QtCore.Qt.AlignRight, QtCore.Qt.TextAlignmentRole)
        child_psi.setEditable(True)
        child_theta.setEditable(True)

        child_tot_distance = QtGui.QStandardItem()
        child_tot_distance.setData(9999.99, QtGui.Qt.EditRole)
        child_tot_distance.setData(QtCore.Qt.AlignRight, QtCore.Qt.TextAlignmentRole)
        child_tot_distance.setEditable(False)

        child_rel_distance = QtGui.QStandardItem()
        child_rel_distance.setData(999.99, QtGui.Qt.EditRole)
        child_rel_distance.setData(QtCore.Qt.AlignRight, QtCore.Qt.TextAlignmentRole)
        child_rel_distance.setEditable(False)

        return (point_node, child_X, child_Y, child_Z, child_I, child_J, child_K, child_psi, child_theta, child_rel_distance, child_tot_distance)

    def addCurve(self, curve, skip_validate=False):
        if not curve:
            return

        blocked = self.signalsBlocked()
        self.blockSignals(True)

        curve_node = QtGui.QStandardItem('Curve')
        curve_node.setEditable(False)
        for ip, point in enumerate(curve):
            point_row = self.create_point_row(point)
            curve_node.appendRow(point_row)

        self.blockSignals(blocked)

        if skip_validate:
            self.appendRow(curve_node)
            return

        row = 0
        for i in reversed(range(self.rowCount())):
            if not self.is_point_index(self.index(i, 0)):
                row = i + 1
                break
        self.insertRow(row, curve_node)

    def addPoint(self, point, index=None, skip_validate=False):
        if not point:
            return

        point_row = self.create_point_row(point)

        if not index or not self.is_point_index(index):
            self.appendRow(point_row)
            return

        if skip_validate:
            self.insertRow(index.row(), point_row)
            return

        min_row = 0
        for i in reversed(range(self.rowCount())):
            if not self.is_point_index(self.index(i, 0)):
                min_row = i + 1
                break
        self.insertRow(max(min_row, index.row()), point_row)

    def load(self, curves, points):

        blocked = self.signalsBlocked()
        self.blockSignals(True)

        self.removeRows(0, self.rowCount())  # dont use self.clear()

        for ic, curve in enumerate(curves):
            self.addCurve(curve, skip_validate=True)

        for ip, point in enumerate(points):
            self.addPoint(point)

        self.blockSignals(blocked)

        self.rowsRemoved.emit(-1, -1, -1)

    def from_items(self, items):

        self.clear_object_item()

        if not items:
            self.original_curves = []
            self.original_points = []
            self.load([], [])
            return

        # TODO: Support multi select
        self.selected_item = items[0]

        curves = cutools.get_curves(self.selected_item)
        points = cutools.get_points(self.selected_item)

        self.original_curves = curves.copy()
        self.original_points = points.copy()

        self.load(curves, points)

    def revert_changes(self):
        self.load(self.original_curves, self.original_points)

    def updateDistanceColumns(self):
        signal_blocked = self.signalsBlocked()
        self.blockSignals(True)

        for ic in self.curveIndexes():
            cumul_dist = 0
            for _i, ip in enumerate(self.curvePointIndexes(ic)):
                x, y, z, i, j, k = self.getPointData(ip)
                if _i == 0:
                    p1 = [x, y, z]
                    self.setData(ip.siblingAtColumn(self.COLS2['Rel. Dist.']), 0, QtCore.Qt.EditRole)
                    self.setData(ip.siblingAtColumn(self.COLS2['Tot. Dist.']), 0, QtCore.Qt.EditRole)
                    continue
                p2 = [x, y, z]
                rel_dist = robomath.distance(p1, p2)
                cumul_dist += rel_dist
                p1 = p2

                self.setData(ip.siblingAtColumn(self.COLS2['Rel. Dist.']), rel_dist, QtCore.Qt.EditRole)
                self.setData(ip.siblingAtColumn(self.COLS2['Tot. Dist.']), cumul_dist, QtCore.Qt.EditRole)

        cumul_dist = 0
        for _i, ip in enumerate(self.pointIndexes()):
            x, y, z, i, j, k = self.getPointData(ip)
            if _i == 0:
                p1 = [x, y, z]
                self.setData(ip.siblingAtColumn(self.COLS2['Rel. Dist.']), 0, QtCore.Qt.EditRole)
                self.setData(ip.siblingAtColumn(self.COLS2['Tot. Dist.']), 0, QtCore.Qt.EditRole)
                continue
            p2 = [x, y, z]
            rel_dist = robomath.distance(p1, p2)
            cumul_dist += rel_dist
            p1 = p2

            self.setData(ip.siblingAtColumn(self.COLS2['Rel. Dist.']), rel_dist, QtCore.Qt.EditRole)
            self.setData(ip.siblingAtColumn(self.COLS2['Tot. Dist.']), cumul_dist, QtCore.Qt.EditRole)

        self.blockSignals(signal_blocked)

    def updateRowColors(self):
        total_indices = self.rowCount()
        for row_index in range(total_indices):
            color = get_distinct_color(row_index, total_indices)
            self.setColorForRow(row_index, color)

    def setColorForRow(self, row, color):
        for column in range(self.columnCount()):
            index = self.index(row, column)
            if index.isValid():
                rgb_color = base1toQColor(color + [0.5])
                self.setData(index, rgb_color, QtCore.Qt.BackgroundRole)

    def removeRowsSmart(self, curves, curve_points, points):
        """Remove row indexes in an ordered manner, as removing rows invalidate the row index"""

        curves, curve_points, points = set(curves) if curves else set(), set(curve_points) if curve_points else set(), set(points) if points else set()
        if not curves and not curve_points and not points:
            return

        signal_blocked = self.signalsBlocked()
        self.blockSignals(True)

        # Remove curve's points if the curve is being deleted
        # Remove the parent curve if its only child is being deleted
        for index in list(curve_points):
            if index.parent() in curves:
                curve_points.remove(index)
                continue
            child_count = self.rowCount(index.parent())
            if child_count == 1:
                curves.add(index.parent())
                curve_points.remove(index)
                continue

        # Remove children of curves first, then points, then curves
        curve_points = sorted(curve_points, key=lambda x: x.row(), reverse=True)
        for point in curve_points:
            # Remove curves if all its points are being deleted
            parent = point.parent()
            child_count = self.rowCount(parent)
            if child_count <= 1:
                curves.add(parent)

            self.removeRow(point.row(), point.parent())

        points = sorted(points, key=lambda x: x.row(), reverse=True)
        for point in points:
            self.removeRow(point.row(), point.parent())

        curves = sorted(curves, key=lambda x: x.row(), reverse=True)
        for curve in curves:
            self.removeRow(curve.row(), curve.parent())

        self.blockSignals(signal_blocked)

        self.rowsRemoved.emit(-1, -1, -1)


class CurveEditor(QtWidgets.QMainWindow):

    def __init__(self):
        super(CurveEditor, self).__init__()

        self.RDK = robolink.Robolink()
        self.RDKM = RoboDKManager(self.RDK)

        self._app_settings = {
            "DisplayPoints": 1,  # "Display points" (bool)
            "ShowPointNormals": 1,  # "Display point normals" (bool)
            "ShowCurveNormals": 1,  # "Display curve normals" (bool)
            "SizeRatioCurves": 0.5,  # "Display curves. Size:" (float) -> must be before flag
            "DisplayCurves": 1,  # "Display curves. Size:" (bool)
            "SizeCurvePoints": 1.0,  # "Display curve points. Size:" (float) -> must be before flag
            "ShowCurvePoints": 1,  # "Display curve points. Size:" (bool)
            #"SizeCurveArrow": 30.0, # "Arrow size (curve/point)" (float)
            #"SizeNormals": 30.0,  # "Normal size" (float) -> TODO There is a bug in RoboDK where normals are not properly rescaled. Skip for now
            "DisplayCurveNormalsOnSelect": 0,  # "Display curve normals on selection" (bool)
            "ShowSelectedPointNormals": 0,  # "Display point normals on selection" (bool)
        }
        self._user_settings = {}

        self.RDK.Render(False)
        for cmd, value in self._app_settings.items():
            try:
                # Some API calls were added in RoboDK v5.7.1
                self._user_settings[cmd] = type(value)(self.RDK.Command(cmd))

                # Allow user to increase the size
                if cmd in ['SizeRatioCurves', 'SizeCurvePoints', 'SizeNormals', 'SizeCurveArrow']:
                    self._app_settings[cmd] = max(self._user_settings[cmd], value)
                    value = self._app_settings[cmd]
            except:
                pass
            print(self.RDK.Command(cmd, value))
        self.RDK.Render(True)

        global ARROW_SIZE
        try:
            ARROW_SIZE = float(self.RDK.Command('SizeCurveArrow'))  # Added in RoboDK v5.7.1
        except:
            pass

        self.initUI()

        # Threads
        self.selection_thread = SelectionThread()
        self.selection_thread.selection_changed.connect(self.selectionChanged)
        self.selection_thread.start()

    def initUI(self):
        self.setWindowTitle("Curve Editor")
        self.setWindowIcon(QtGui.QIcon("CurveEditor.svg"))
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        centralWidget = QtWidgets.QWidget(self)

        self.model = QCurvesItemModel(self.RDK)
        self.selection_model = CurveSelectionModel(self.model)

        self.treeView = CurvesTreeView(centralWidget)
        self.treeView.setModel(self.model)
        self.treeView.setSelectionModel(self.selection_model)
        self.treeView.setAlternatingRowColors(True)

        #====================================================
        # Menu Bar
        #====================================================
        menu_bar = QtWidgets.QMenuBar()

        #----------------------------------------
        # \ File
        menu_file = menu_bar.addMenu("File")
        menu_file.addAction('Import Curve(s)...').triggered.connect(self.treeView.loadCSVCurves)
        menu_file.addAction('Export Curve(s)...').triggered.connect(lambda state: cutools.save_curves(self.treeView.model().getData()[0]))  # TODO: check selection
        menu_file.addSeparator()
        menu_file.addAction('Import Points(s)...').triggered.connect(self.treeView.loadCSVPoints)
        menu_file.addAction('Export Point(s)...').triggered.connect(lambda state: cutools.save_points(self.treeView.model().getData()[1]))  # TODO: check selection
        menu_file.addSeparator()
        menu_file.addAction('Revert All Changes').triggered.connect(lambda state: self.treeView.model().revert_changes())
        menu_file.addSeparator()
        menu_file.addAction('Exit').triggered.connect(self.close)

        #----------------------------------------
        # \ Edit
        menu_edit = menu_bar.addMenu("Edit")

        #menu_edit.addAction('Undo')
        #menu_edit.addAction('Redo')
        #menu_edit.addSeparator()

        cut_action = menu_edit.addAction('Cut')
        cut_action.setToolTip("Cut")
        cut_action.setShortcut('Ctrl+X')
        cut_action.triggered.connect(self.treeView.cutSelection)

        copy_action = menu_edit.addAction('Copy')
        copy_action.setToolTip("Copy")
        copy_action.setShortcut('Ctrl+C')
        copy_action.triggered.connect(self.treeView.copySelection)

        paste_action = menu_edit.addAction('Paste')
        paste_action.setToolTip("Paste")
        paste_action.setShortcut('Ctrl+V')
        paste_action.triggered.connect(self.treeView.pasteToSelection)

        menu_edit.addSeparator()
        action_delete = menu_edit.addAction('Delete')
        action_delete.setToolTip("Delete")
        action_delete.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Delete))
        action_delete.triggered.connect(self.treeView.deleteSelection)

        menu_edit.addSeparator()
        action_add = menu_edit.addAction('Add New Point')
        action_add.setToolTip("Add a new point")
        action_add.triggered.connect(self.treeView.addPoint)

        #----------------------------------------
        # \ Selection
        menu_selection = menu_bar.addMenu("Selection")

        action_select_all = menu_selection.addAction('Select All')
        action_select_all.setToolTip("Select All Rows")
        action_select_all.setShortcut(QtGui.QKeySequence(QtCore.Qt.Modifier.CTRL + QtCore.Qt.Key_A))
        action_select_all.triggered.connect(self.treeView.selectAll)

        action_select_curves = menu_selection.addAction('Select Curves')
        action_select_curves.setToolTip("Select All Curve Rows")
        action_select_curves.triggered.connect(self.treeView.selectAllCurves)

        action_select_points = menu_selection.addAction('Select Points')
        action_select_points.setToolTip("Select All Point Rows")
        action_select_points.triggered.connect(self.treeView.selectAllPoints)

        menu_selection.addSeparator()
        action_moveUp = menu_selection.addAction('Move Up')
        action_moveUp.setToolTip("Move Selected Row Up")
        action_moveUp.triggered.connect(self.treeView.moveUp)
        action_moveUp.setShortcut(QtGui.QKeySequence(QtCore.Qt.Modifier.ALT + QtCore.Qt.Key_Up))

        action_moveDown = menu_selection.addAction('Move Down')
        action_moveDown.setToolTip("Move Selected Row Down")
        action_moveDown.triggered.connect(self.treeView.moveDown)
        action_moveDown.setShortcut(QtGui.QKeySequence(QtCore.Qt.Modifier.ALT + QtCore.Qt.Key_Down))

        #----------------------------------------
        # \ View
        menu_view = menu_bar.addMenu("View")
        menu_view.addAction('Expand All').triggered.connect(self.treeView.expandAll)
        menu_view.addAction('Collapse All').triggered.connect(self.treeView.collapseAll)

        menu_view.addSeparator()

        if ENABLE_CURVE_PREVIEW_ARROWS:
            action_show_surve_arrows = menu_view.addAction('Show Curve Directional Arrows')
            action_show_surve_arrows.setCheckable(True)
            action_show_surve_arrows.setChecked(True)
            action_show_surve_arrows.toggled.connect(self.RDKM.enable_curve_arrows_previews)
            action_show_surve_arrows.setChecked(False)  # Force it

        if ENABLE_CURVE_PREVIEW_POINTS:
            action_show_curve_points = menu_view.addAction('Show Curve Points Previews')
            action_show_curve_points.setCheckable(True)
            action_show_curve_points.setChecked(True)
            action_show_curve_points.toggled.connect(self.RDKM.enable_curve_points_previews)

        if ENABLE_POINTS_PREVIEW:
            action_show_points = menu_view.addAction('Show Points Previews')
            action_show_points.setCheckable(True)
            action_show_points.setChecked(True)
            action_show_points.toggled.connect(self.RDKM.enable_points_previews)

        menu_view.addSeparator()
        toggle_ijk_action = menu_view.addAction("Show IJK Columns")
        toggle_ijk_action.setCheckable(True)
        toggle_ijk_action.setChecked(True)
        toggle_ijk_action.toggled.connect(self.treeView.setIJKColumnsVisible)
        toggle_ijk_action.setChecked(False)  # Force it

        menu_view.addSeparator()
        toggle_distance_action = menu_view.addAction("Show Point-to-Point Distances")
        toggle_distance_action.setCheckable(True)
        toggle_distance_action.setChecked(True)
        toggle_distance_action.toggled.connect(self.treeView.setDistanceColumnsVisible)
        toggle_distance_action.setChecked(False)  # Force it

        #----------------------------------------
        # \ Transform (does not change the number of points)

        menu_transform = menu_bar.addMenu("Transform")

        menu_transform.addAction('Merge Curves').triggered.connect(self.treeView.mergeCurves)
        menu_transform.addAction('Reverse Curve(s)').triggered.connect(self.treeView.reverseCurve)
        menu_transform.addAction('Convert Curve(s) to Points').triggered.connect(self.treeView.curvesToPoints)
        menu_transform.addAction('Convert Point(s) to Curve').triggered.connect(self.treeView.pointsToCurve)
        menu_transform.addSeparator()

        menu_transform.addAction('Offset Curve(s) Points (Relative)').triggered.connect(self.treeView.filterOffsetPoints)
        menu_transform.addAction('Offset Curve(s) Points (Along Normal)').triggered.connect(self.treeView.filterOffsetPointsIJK)
        menu_transform.addAction('Offset Curve(s) Points (Tangent)').triggered.connect(self.treeView.filterOffsetPointsSideways)
        menu_transform.addSeparator()

        menu_transform.addAction('Project Curve(s) Points on Surface').triggered.connect(self.treeView.filterProjectPoints)
        menu_transform.addSeparator()

        menu_transform.addAction('Bulk Edit Points (Absolute)').triggered.connect(self.treeView.filterBulkEditPoints)
        menu_transform.addAction('Flip Normals').triggered.connect(self.treeView.filterFlipIJK)
        menu_transform.addAction('Average Normals').triggered.connect(self.treeView.filterAverageNormals)
        menu_transform.addSeparator()

        menu_transform.addAction('Set Normals (Absolute)').triggered.connect(self.treeView.filterSetNormals)
        menu_transform.addAction('Set Normals (Relative)').triggered.connect(self.treeView.filterSetNormalsRelative)
        menu_transform.addAction('Set Normals (Tangent)').triggered.connect(self.treeView.filterSetNormalsTangent)
        menu_transform.addSeparator()

        #----------------------------------------
        # \ Filters (can change the number of points)
        menu_filters = menu_bar.addMenu("Filter")

        menu_filters.addAction('Remove Duplicated Points').triggered.connect(self.treeView.filterRemoveDuplicates)
        menu_filters.addAction('Simplify Straight Lines').triggered.connect(self.treeView.filterStraightLines)

        menu_filters.addAction('Resample Curve (Fixed Step)').triggered.connect(self.treeView.filterResampleCurve)
        menu_filters.addAction('Resample Curve (By Factor)').triggered.connect(self.treeView.filterResampleByFactor)
        menu_filters.addAction('CCMA Smoothing (Accuracy Focus)').triggered.connect(self.treeView.filterCCMASmoothing)
        menu_filters.addAction('B-Spline Smoothing (Motion Focus)').triggered.connect(self.treeView.filterBSplineSmoothing)

        menu_filters.addAction('Sort Curves by Distance').triggered.connect(self.treeView.filterSortCurves)
        menu_filters.addAction('Split/Group Discontinuous Curves').triggered.connect(self.treeView.filterSplitDiscontinuousCurves)

        #----------------------------------------
        # \ Utilities
        menu_utilities = menu_bar.addMenu("Utilities")
        menu_utilities.addAction('Convert to Targets').triggered.connect(self.treeView.convertToTargets)
        menu_utilities.addSeparator()
        menu_utilities.addAction('Import Program...').triggered.connect(self.treeView.loadProgram)
        menu_utilities.addAction('Import SVG...').triggered.connect(self.treeView.loadSVG)
        menu_utilities.addAction('Import DXF...').triggered.connect(self.treeView.loadDXF)

        self.setMenuBar(menu_bar)

        #====================================================
        # Toolbar
        #====================================================

        toolbar = QtWidgets.QToolBar("Feature")
        #toolbar.setFloatable(False)
        #toolbar.setMovable(False)
        # TODO toolbar.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)

        #-------------------------------------
        # Move points or curves
        toolbar.addSeparator()
        action_moveUp = toolbar.addAction('↑')
        action_moveDown = toolbar.addAction('↓')
        action_moveUp.setToolTip("Move Up")
        action_moveDown.setToolTip("Move Down")
        action_moveUp.triggered.connect(self.treeView.moveUp)
        action_moveDown.triggered.connect(self.treeView.moveDown)

        # Sort and merge curves
        toolbar.addSeparator()
        action_reverse = toolbar.addAction('⇵')
        action_merge = toolbar.addAction('⧉')
        action_reverse.setToolTip("Reverse Curve")
        action_merge.setToolTip("Merge Curves")
        action_reverse.triggered.connect(self.treeView.reverseCurve)
        action_merge.triggered.connect(self.treeView.mergeCurves)

        # Remove duplicates in curves
        toolbar.addSeparator()
        action_duplicates = toolbar.addAction('≈')
        action_duplicates.setToolTip("Remove duplicates")
        action_duplicates.triggered.connect(self.treeView.filterRemoveDuplicates)

        # Project points on surface
        action_project = toolbar.addAction('⭳')  # ⤢
        action_project.setToolTip("Project on surface")
        action_project.triggered.connect(self.treeView.filterProjectPoints)

        #-------------------------------------
        # Clipboard
        toolbar.addSeparator()
        copy_action = toolbar.addAction('Copy')
        copy_action.setToolTip("Copy")
        copy_action.triggered.connect(self.treeView.copySelection)

        paste_action = toolbar.addAction('Paste')
        paste_action.setToolTip("Paste")
        paste_action.triggered.connect(self.treeView.pasteToSelection)

        #-------------------------------------
        # Delete points or curves
        toolbar.addSeparator()
        action_delete = toolbar.addAction('X')
        action_delete.setToolTip("Delete")
        action_delete.triggered.connect(self.treeView.deleteSelection)

        #-------------------------------------
        layout = QtWidgets.QVBoxLayout(centralWidget)
        layout.addWidget(toolbar)
        layout.addWidget(self.treeView)
        self.setCentralWidget(centralWidget)

        self.resizeToContent()

    def resizeToContent(self):
        screenSize = QtGui.QGuiApplication.instance().primaryScreen().availableGeometry()
        w, h = min(screenSize.width(), 600), int(screenSize.height() * 0.97)  # magic number for the taskbar that might not be universal
        self.setGeometry(0, 0, w, h)
        self.move(screenSize.right() - w, screenSize.top())

    def closeEvent(self, event):  # override
        self.selection_thread.requestInterruption()
        self.selection_thread.wait(500)

        for cmd, value in self._user_settings.items():
            print(self.RDK.Command(cmd, value))

        super().closeEvent(event)

    def selectionChanged(self, selection):
        items = [robolink.Item(self.RDK, x) for x in selection]
        items = [x for x in items if x.Valid(True)]
        self.model.from_items(items)
        self.treeView.expandAll()


class SelectionThread(QtCore.QThread):

    selection_changed = QtCore.Signal(list)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    def run(self) -> None:
        RDK = robolink.Robolink()
        selected_items_prev = []
        active_station = RDK.ActiveStation()
        while True:
            robomath.pause(0.01)
            if self.isInterruptionRequested():
                return

            # Force clear selection if we change the active station
            if active_station != RDK.ActiveStation():
                if DEBUG_LEVEL:
                    print(f'Selection: Active station changed!')
                active_station = RDK.ActiveStation()
                selected_items_prev = []
                self.selection_changed.emit([])
                continue

            selection = [x for x in RDK.Selection() if x.type == robolink.ITEM_TYPE_OBJECT]
            selected_items = [str(x.item) for x in selection]
            if selected_items_prev != selected_items:
                if DEBUG_LEVEL:
                    print(f'Selection: {[x.Name() for x in selection]}')
                selected_items_prev = selected_items
                self.selection_changed.emit(selected_items)  # item.item must be send as a str to avoid int overflow


class BulkEditDialog(QtWidgets.QDialog):

    def __init__(self, title='Bulk Edit', show_ijk=True, parent=None):
        super(BulkEditDialog, self).__init__(parent)

        self.setWindowTitle(title)
        self._show_ijk = show_ijk
        self.initUI()

    def initUI(self):

        form_layout = QtWidgets.QFormLayout(self)

        # Create line edits and checkboxes for each field
        self.x_edit = create_spinbox(self, "X")
        self.y_edit = create_spinbox(self, "Y")
        self.z_edit = create_spinbox(self, "Z")

        if self._show_ijk:
            self.i_edit = create_spinbox(self, "I")
            self.j_edit = create_spinbox(self, "J")
            self.k_edit = create_spinbox(self, "K")

        self.x_check = QtWidgets.QCheckBox("X:", self)
        self.y_check = QtWidgets.QCheckBox("Y:", self)
        self.z_check = QtWidgets.QCheckBox("Z:", self)

        if self._show_ijk:
            self.i_check = QtWidgets.QCheckBox("I:", self)
            self.j_check = QtWidgets.QCheckBox("J:", self)
            self.k_check = QtWidgets.QCheckBox("K:", self)

        form_layout.addRow(self.x_check, self.x_edit)
        form_layout.addRow(self.y_check, self.y_edit)
        form_layout.addRow(self.z_check, self.z_edit)
        if self._show_ijk:
            form_layout.addRow(self.i_check, self.i_edit)
            form_layout.addRow(self.j_check, self.j_edit)
            form_layout.addRow(self.k_check, self.k_edit)

        ok_button = QtWidgets.QPushButton("OK", self)
        ok_button.clicked.connect(self.accept)
        form_layout.addRow(ok_button)

    def getValues(self):
        if self._show_ijk:
            return [
                self.x_edit.value() if self.x_check.isChecked() else None,
                self.y_edit.value() if self.y_check.isChecked() else None,
                self.z_edit.value() if self.z_check.isChecked() else None,
                self.i_edit.value() if self.i_check.isChecked() else None,
                self.j_edit.value() if self.j_check.isChecked() else None,
                self.k_edit.value() if self.k_check.isChecked() else None,
            ]
        else:
            return [
                self.x_edit.value() if self.x_check.isChecked() else None,
                self.y_edit.value() if self.y_check.isChecked() else None,
                self.z_edit.value() if self.z_check.isChecked() else None,
                None,
                None,
                None,
            ]


if __name__ == '__main__':

    app = roboapps.get_qt_app()
    ex = CurveEditor()
    ex.show()
    sys.exit(app.exec_())
