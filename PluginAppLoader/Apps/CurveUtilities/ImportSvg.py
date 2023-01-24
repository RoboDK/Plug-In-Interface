# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Import an SVG file as a curve(s) or point(s) object.
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# More information on RoboDK Apps here:
#     https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader
#
# --------------------------------------------

from robodk import robolink, robomath, roboapps, robodialogs

robolink.import_install('svgpathtools')
import svgpathtools as spt
import urllib.request
import os

import Settings


def ImportSvg(RDK=None, S=None, file=None):
    """
    Import an SVG file as a curve(s) or point(s) object.
    """

    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = Settings.Settings()
        S.Load(RDK)

    #-------------------------------------------
    # Retrieve and load the SVG file
    if not file:
        file = robodialogs.getOpenFileName(strtitle='Open SVG File', defaultextension='.svg', filetypes=[('SVG files', '.svg')])
        if not file:
            roboapps.Exit()

    if file and file.startswith('http') and file.endswith('.svg'):
        r = urllib.request.urlretrieve(file, os.path.basename(file))
        file = os.path.basename(r[0])

    if not file or not os.path.exists(os.path.abspath(file)):
        RDK.ShowMessage('Unable to load the SVG file.')
        roboapps.Exit()

    item_name = os.path.basename(file).split('.svg')[0]
    paths, path_attribs, svg_attribs = spt.svg2paths2(file)

    #-------------------------------------------
    # Scale the SVG
    xmin, xmax, ymin, ymax = 9e9, 0, 9e9, 0
    for path in paths:
        _xmin, _xmax, _ymin, _ymax = path.bbox()
        xmin = min(_xmin, xmin)
        xmax = max(_xmax, xmax)
        ymin = min(_ymin, ymin)
        ymax = max(_ymax, ymax)
    bbox_height, bbox_width = ymax - ymin, xmax - xmin

    width, height = S.SVG_SIZE
    SCALE = min(height / bbox_height, width / bbox_width)
    svg_height, svg_width = bbox_height * SCALE, bbox_width * SCALE
    svg_height_min, svg_width_min = ymin * SCALE, xmin * SCALE
    TRANSLATE = complex((width - svg_width) / 2 - svg_width_min, (height - svg_height) / 2 - svg_height_min)

    #-------------------------------------------
    RDK.ShowMessage(f"Importing {file}..", False)
    RDK.Render(False)

    curves = []
    colors = []
    for path_count, (path, attrib) in enumerate(zip(paths, path_attribs)):
        styles = {}

        if 'style' not in attrib:
            if 'fill' in attrib:
                styles['fill'] = attrib['fill']
            if 'stroke' in attrib:
                styles['stroke'] = attrib['stroke']
        else:
            for style in attrib['style'].split(';'):
                style_pair = style.split(':')
                if len(style_pair) != 2:
                    continue
                styles[style_pair[0].strip()] = style_pair[1].strip()

        if 'fill' in styles and not styles['fill'].startswith('#'):
            styles.pop('fill')
        if 'stroke' in styles and not styles['stroke'].startswith('#'):
            styles.pop('stroke')

        draw_color = S.SVG_DEFAULT_COLOR  # 0-255
        if S.SVG_IMPORT_COLOR:
            hex_color = None
            if S.SVG_STROKE_OVER_FILL_COLOR:
                if 'stroke' in styles:
                    hex_color = styles['stroke']
                elif 'fill' in styles:
                    hex_color = styles['fill']
            else:
                if 'fill' in styles:
                    hex_color = styles['fill']
                elif 'stroke' in styles:
                    hex_color = styles['stroke']

            if hex_color:
                draw_color = spt.misctools.hex2rgb(hex_color)  # 0-255

        draw_color = [round(x / 255, 4) for x in draw_color]  # 0-1

        RDK.ShowMessage(f"Importing path {attrib['id'] if 'id' in attrib else path_count} with color {draw_color}", False)

        for segment in path.scaled(SCALE).translated(TRANSLATE):
            points = []
            segment_len = segment.length()
            steps = int(segment_len / S.SVG_STEP)
            if steps < 1:
                if not S.SVG_KEEP_SMALLER_STEP:
                    continue
                elif segment_len < 1e-3:
                    RDK.ShowMessage(f'Segment is too small, skipping ({segment_len:.6f}).', False)
                    continue
                else:
                    RDK.ShowMessage(f'Recovering small segment ({segment_len:.6f}).', False)
                    steps = 1

            for i in range(steps + 1):
                t = 1.0
                if i < steps:
                    # We need this check to prevent numerical accuracy going over 1, as t must be bound to [0,1]
                    i_len = segment_len * i / steps
                    t = segment.ilength(i_len)

                point = segment.point(t)
                py, px = point.real, point.imag

                points.append([px, py, 0, 0, 0, -1 if S.SVG_INVERT_NORMAL else 1])

            if points:
                curves.append(points)
                colors.append(draw_color)

    if curves:
        RDK.Render(False)

        if not S.SVG_AS_POINTS:
            # Curves can have different colors in the same object
            curve_item = RDK.AddCurve(curves[0], reference_object=0, add_to_ref=False, projection_type=robolink.PROJECTION_NONE)
            curve_item.setName(item_name)
            curve_item.setColorCurve(colors[0])
            for i in range(1, len(curves)):
                curve_item.AddCurve(curves[i], add_to_ref=True, projection_type=robolink.PROJECTION_NONE)
                curve_item.setColorCurve(colors[i], i)
        else:
            # Individual segments and colors are lost with points
            curve_item = RDK.AddPoints([p for c in curves for p in c], reference_object=0, add_to_ref=False, projection_type=robolink.PROJECTION_NONE)
            curve_item.setName(item_name)

        if S.SVG_CENTER_OBJECT_FRAME:
            curve_item.setGeometryPose(pose=robomath.xyzrpw_2_pose([-width / 2, -height / 2, 0, 0, 0, 0]), apply=True)

        curve_item.setVisible(False)
        curve_item.setVisible(True)

    RDK.ShowMessage(f"Done importing {file}!", False)


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        ImportSvg()


if __name__ == '__main__':
    runmain()