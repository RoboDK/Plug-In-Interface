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

import os


def save_curves(curves, file_path=None):
    if not curves:
        return

    if not file_path:
        file_path = robodialogs.getSaveFileName(strfile="Curves.csv", defaultextension='.csv', filetypes=[('Text Files', '.txt .csv')])
        if not file_path:
            return

    # X, Y, Z, I, J, K, "Curve", Curve ID, Reverse
    with open(file_path, 'w') as f:
        for ic, curve in enumerate(curves):
            for ip, point in enumerate(curve):
                x, y, z = point[:3]
                i, j, k = [0, 0, 1]
                if len(point) > 3:
                    i, j, k = point[3:6]
                s = f'{x:.5f},{y:.5f},{z:.5f},{i:.5f},{j:.5f},{k:.5f}'
                if ip == 0:
                    s += f',Curve,{ic}'
                f.write(s + "\n")


def load_curves(file_path=None):

    if not file_path or not os.path.exists(file_path):
        file_path = robodialogs.getOpenFileName(strfile="Curves.csv", defaultextension='.csv', filetypes=[('Text Files', '.txt .csv')])
        if not file_path or not os.path.exists(file_path):
            return None

    # X, Y, Z, I, J, K, "Curve", Curve ID, Reverse
    curves_str = []
    with open(file_path, 'r') as f:
        curves_str = f.readlines()

    def to_pod(val_str):
        try:
            val = float(val_str)
            if int(val) == val:
                return int(val)
            return val
        except ValueError as e:
            pass
        return val_str

    curves = []
    ic = 0
    for ip, point_str in enumerate(curves_str):
        point = [to_pod(x.strip()) for x in point_str.split(',')]

        x, y, z, i, j, k = point[:6]
        if len(point) > 6:
            # Start of a curve
            if point[6] == 'Curve':
                if len(point) > 7:
                    ic = int(point[7])  # Curve ID

        while (len(curves) - 1) < ic:
            curves.append([])

        curves[ic].append([x, y, z, i, j, k])

    return curves


def save_points(points, file_path=None):
    if not points:
        return

    if not file_path:
        file_path = robodialogs.getSaveFileName(strfile="Points.csv", defaultextension='.csv', filetypes=[('Text Files', '.txt .csv')])
        if not file_path:
            return

    # X, Y, Z, I, J, K, "Curve", Curve ID, Reverse
    with open(file_path, 'w') as f:
        for ip, point in enumerate(points):
            x, y, z = point[:3]
            i, j, k = [0, 0, 1]
            if len(point) > 3:
                i, j, k = point[3:6]
            s = f'{x:.5f},{y:.5f},{z:.5f},{i:.5f},{j:.5f},{k:.5f}'
            f.write(s + "\n")


def load_points(file_path=None):

    if not file_path or not os.path.exists(file_path):
        file_path = robodialogs.getOpenFileName(strfile="Points.csv", defaultextension='.csv', filetypes=[('Text Files', '.txt .csv')])
        if not file_path or not os.path.exists(file_path):
            return None

    # X, Y, Z, I, J, K
    curves_str = []
    with open(file_path, 'r') as f:
        curves_str = f.readlines()

    def to_pod(val_str):
        try:
            val = float(val_str)
            if int(val) == val:
                return int(val)
            return val
        except ValueError as e:
            pass
        return val_str

    points = []
    for ip, point_str in enumerate(curves_str):
        point = [to_pod(x.strip()) for x in point_str.split(',')]

        x, y, z, i, j, k = point[:6]
        points.append([x, y, z, i, j, k])

    return points


def load_svg(file_path=None):
    robolink.import_install('svgpathtools')
    import svgpathtools as spt
    import urllib.request

    if not file_path or not os.path.exists(file_path):
        file_path = robodialogs.getOpenFileName(defaultextension='.svg', filetypes=[('SVG Files', '.SVG .svg')])
        if not file_path or not os.path.exists(file_path):
            return None

    if file_path and file_path.startswith('http') and file_path.endswith('.svg'):
        r = urllib.request.urlretrieve(file_path, os.path.basename(file_path))
        file_path = os.path.basename(r[0])

    if not file_path or not os.path.exists(os.path.abspath(file_path)):
        return None

    paths, path_attribs, svg_attribs = spt.svg2paths2(file_path)

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

    def dialog_svg():

        inputs = {
            "Size of the imported SVG (w, h) [mm]": (1000.0, 1000.0),
            "Step size [mm]": 2.0,
            "Keep segments smaller that the step size": True,
        }

        outputs = robodialogs.InputDialog("Project points on the object's surface, and recalculate position and normal accordingly.", inputs, 'Project Points')
        if outputs is None:
            # User cancelled
            return None
        return outputs

    settings = dialog_svg()
    if settings is None:
        return None

    SVG_SIZE, SVG_STEP, SVG_KEEP_SMALLER_STEP = list(settings.values())

    width, height = SVG_SIZE
    SCALE = min(height / bbox_height, width / bbox_width)
    svg_height, svg_width = bbox_height * SCALE, bbox_width * SCALE
    svg_height_min, svg_width_min = ymin * SCALE, xmin * SCALE
    TRANSLATE = complex((width - svg_width) / 2 - svg_width_min, (height - svg_height) / 2 - svg_height_min)

    #-------------------------------------------
    print(f"Importing {file_path}..", False)

    curves = []
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

        print(f"Importing path {attrib['id'] if 'id' in attrib else path_count}", False)

        for segment in path.scaled(SCALE).translated(TRANSLATE):
            points = []
            segment_len = segment.length()
            steps = int(segment_len / SVG_STEP)
            if steps < 1:
                if not SVG_KEEP_SMALLER_STEP:
                    continue
                elif segment_len < 1e-3:
                    print(f'Segment is too small, skipping ({segment_len:.6f}).', False)
                    continue
                else:
                    print(f'Recovering small segment ({segment_len:.6f}).', False)
                    steps = 1

            for i in range(steps + 1):
                t = 1.0
                if i < steps:
                    # We need this check to prevent numerical accuracy going over 1, as t must be bound to [0,1]
                    i_len = segment_len * i / steps
                    t = segment.ilength(i_len)

                point = segment.point(t)
                py, px = point.real, point.imag

                points.append([px, py, 0, 0, 0, 1])

            if points:
                curves.append(points)

    return curves


def LoadDXF(file_path=None, merge_continuous_segments=True, resolution=0.01, orient_closed_curves=False, create_machining_project=False):
    # Please also maintain:
    # - RoboDK-API/Python/Scripts/Import_DXF.py
    # - Apps-Private/Public/ImportDXF
    """
    Load a DXF file, extract geometry, and import it into RoboDK.

    This supports recursive block resolution, unit scaling, and optional merging of
    connected segments. Geometry is grouped by DXF layer and imported accordingly.

    :param file_path: Path to the DXF file. If None, prompts the user.
    :type file_path: str or None
    :param merge_continuous_segments: Whether to merge connected curves. If None, user is prompted.
    :type merge_continuous_segments: bool or None
    :param resolution: Segment resolution. If None, user is prompted.
    :type resolution: bool or None
    :param orient_closed_curves: Make outermost closed curves clockwise and alternate by nesting depth. If None, user is prompted.
    :type orient_closed_curves: bool or None
    :param create_machining_project: Create a Curve Follow Project after importation. If None, user is prompted.
    :type create_machining_project: bool or None
    :return: The main RoboDK object created from the DXF, or None on failure.
    :rtype: robolink.Item or None
    """

    from robodk import robolink, robomath, robodialogs

    from collections import OrderedDict
    import sys
    from pathlib import Path

    robolink.import_install('ezdxf')  # >= 1.4.1

    import ezdxf
    from ezdxf import recover, path
    from ezdxf.math import Matrix44
    import math

    def insert_transform(ins):
        """
        Compute the transformation matrix for a DXF INSERT entity.

        This includes scaling and rotation. Translation is excluded so that
        parent matrices can handle positioning recursively.

        :param ins: The INSERT entity from the DXF.
        :type ins: ezdxf.entities.Insert
        :return: Transformation matrix (excluding translation).
        :rtype: ezdxf.math.Matrix44
        """
        location = ins.dxf.insert
        rotation = ins.dxf.rotation
        xscale = getattr(ins.dxf, 'xscale', 1.0)
        yscale = getattr(ins.dxf, 'yscale', 1.0)
        zscale = getattr(ins.dxf, 'zscale', 1.0)
        return Matrix44.chain(
            Matrix44.scale(xscale, yscale, zscale),
            Matrix44.z_rotate(math.radians(rotation)),
            #Matrix44.translate(location.x, location.y, location.z),
        )

    def traverse_entity(layout_or_block, parent_matrix=Matrix44(), factor_mm=1.0, resolution=0.01):
        """
        Recursively traverse a DXF layout or block and extract geometry.

        This function handles nested INSERTs, applying cumulative transforms. Supported
        entity types include LINE, ARC, CIRCLE, LWPOLYLINE, SPLINE and POINT.

        :param layout_or_block: DXF layout or block to traverse.
        :type layout_or_block: ezdxf.layouts.Layout or ezdxf.blocks.BlockRecord
        :param parent_matrix: Transformation matrix accumulated from parent INSERTs.
        :type parent_matrix: ezdxf.math.Matrix44
        :param factor_mm: Unit scaling factor to convert to millimeters.
        :type factor_mm: float
        :return: List of tuples with (layer name, list of 3D points).
        :rtype: list[tuple[str, list[list[float]]]]
        """
        entities = []

        for entity in layout_or_block:
            dxftype = entity.dxftype()
            print(dxftype)

            if dxftype == 'INSERT':
                print(f"INSERT {entity.dxf.name} at {entity.dxf.insert}, rotation {entity.dxf.rotation}")

                block_name = entity.dxf.name
                if block_name not in entity.doc.blocks:
                    return []

                m = parent_matrix @ insert_transform(entity)
                block = entity.doc.blocks[block_name]
                entities += traverse_entity(block, parent_matrix=m, factor_mm=factor_mm, resolution=resolution)

            elif dxftype in ['LINE', 'ARC', 'CIRCLE', 'LWPOLYLINE', 'SPLINE']:
                try:
                    spath = path.make_path(entity)
                    spath = spath.transform(parent_matrix)
                    curve = [list(v.xyz) for v in spath.flattening(distance=resolution, segments=4)]

                    if len(curve) > 0:
                        if factor_mm != 1.0:
                            curve = [robomath.mult3(p, factor_mm) for p in curve]

                        layer = str(entity.dxf.layer)
                        entities.append((layer, curve))

                except Exception as e:
                    print(f"Skipped entity {entity.dxftype()}: {e}")

            elif dxftype in ['POINT']:
                try:
                    location = entity.dxf.location
                    curve = [[location.x, location.y, location.z]]

                    if len(curve) > 0:
                        if factor_mm != 1.0:
                            curve = [robomath.mult3(p, factor_mm) for p in curve]

                        layer = str(entity.dxf.layer)
                        entities.append((layer, curve))

                except Exception as e:
                    print(f"Skipped entity {entity.dxftype()}: {e}")

        return entities

    def merge_connected_curves(curves, tol=0.001):
        """
        Merge open curves that are end-to-end connected within a distance tolerance.

        This detects continuous sequences of curves and joins them into a single curve,
        reversing point order when necessary to ensure smooth joining.
        Closed curves are preserved as-is.

        :param curves: List of curves, each defined by a list of 3D points.
        :type curves: list[list[list[float]]]
        :param tol: Distance tolerance for endpoint matching.
        :type tol: float
        :return: Curves with connected segments merged.
        :rtype: list[list[list[float]]]
        """
        closed_curves = []
        open_curves = []

        # Find closed vs. open forms in individual curves
        for curve in curves:
            if robomath.distance((curve[0])[:3], (curve[-1])[:3]) < tol:
                closed_curves.append(curve)
            else:
                open_curves.append(curve)

        # Find closed forms across multiple segments/curves (permutate)
        merged_curves = []
        while open_curves:
            base = open_curves.pop(0)
            merged = True
            while merged:
                merged = False
                for i, other in enumerate(open_curves):
                    s1, e1 = base[0][:3], base[-1][:3]
                    s2, e2 = other[0][:3], other[-1][:3]

                    if robomath.distance(e1, e2) < tol:
                        base += other[-2::-1]  # reverse
                    elif robomath.distance(s1, s2) < tol:
                        base = other[::-1] + base[1:]  # reverse
                    elif robomath.distance(s1, e2) < tol:
                        base = other[:-1] + base
                    elif robomath.distance(e1, s2) < tol:
                        base += other[1:]
                    else:
                        continue

                    del open_curves[i]
                    merged = True
                    break

            merged_curves.append(base)

        return closed_curves + merged_curves

    def _is_closed(curve, tol=0.001):
        return robomath.distance(curve[0][:3], curve[-1][:3]) < tol

    def _signed_area2d(points):
        xy = _xy_no_dup_last(points)
        a = 0.0
        n = len(xy)
        if n < 3:
            return 0.0
        for i in range(n):
            x1, y1 = xy[i]
            x2, y2 = xy[(i + 1) % n]
            a += x1 * y2 - x2 * y1
        return 0.5 * a  # >0 CCW, <0 CW

    def _is_clockwise(points):
        return _signed_area2d(points) < 0.0

    def _xy_no_dup_last(points):
        # Return list of (x,y) without duplicating the last point if equal to first
        if len(points) >= 2 and points[0][:2] == points[-1][:2]:
            pts = points[:-1]
        else:
            pts = points
        return [(p[0], p[1]) for p in pts]

    def _bbox(points):
        xy = _xy_no_dup_last(points)
        if not xy:
            return 0.0, 0.0, 0.0, 0.0
        xs = [p[0] for p in xy]
        ys = [p[1] for p in xy]
        return min(xs), min(ys), max(xs), max(ys)

    def _bbox_contains(inner_points, outer_points, tol=0.001):
        ix0, iy0, ix1, iy1 = _bbox(inner_points)
        ox0, oy0, ox1, oy1 = _bbox(outer_points)
        return (ix0 >= ox0 - tol and iy0 >= oy0 - tol and ix1 <= ox1 + tol and iy1 <= oy1 + tol)

    def _orient_nested_curves(curves, tol=0.001):
        """
        For closed polygons only.
        Depth 0 (not inside any) -> clockwise.
        Depth 1 -> counterclockwise.
        Depth 2 -> clockwise. And so on.
        """
        # Separate closed from open
        closed = []
        open_curves = []
        for c in curves:
            if _is_closed(c, tol):
                closed.append(c)
            else:
                open_curves.append(c)

        if not closed:
            return curves

        # Build containment depth for each closed polygon using bounding boxes
        depths = []
        for i, pi in enumerate(closed):
            depth = 0
            for j, pj in enumerate(closed):
                if i == j:
                    continue
                if _bbox_contains(pi, pj, tol):
                    depth += 1
            depths.append(depth)

        # Reorient based on depth parity
        reoriented_closed = []
        for poly, depth in zip(closed, depths):
            should_be_cw = (depth % 2 == 0)  # even depth
            is_cw = _is_clockwise(poly)
            if should_be_cw != is_cw:
                poly = poly[::-1]
            reoriented_closed.append(poly)

        return reoriented_closed + open_curves

    if not file_path and len(sys.argv) >= 2:
        file_path = sys.argv[1]

    if not file_path or not Path(file_path).is_file():
        file_path = robodialogs.getOpenFileName(defaultextension='.dxf', filetypes=[('DXF files', '.DXF .dxf')])

    if not file_path or not Path(file_path).is_file():
        print("Invalid file:")
        print(file_path)
        RDK.ShowMessage("Could not open the provided DXF file.\n"
                        "Please check the file path and try again.")
        return None

    RDK = robolink.Robolink()
    RDK.ShowMessage("Loading DXF file: " + file_path, False)

    if resolution is None:
        resolution = robodialogs.InputDialog("Specify the segment resolution", DEFAULT_RESOLUTION + 1e-10)
        if resolution is None:
            RDK.ShowMessage("Operation cancelled")
            return None

    doc, auditor = ezdxf.recover.readfile(file_path)
    factor_mm = ezdxf.units.conversion_factor(doc.units, 4) if doc.units > 0 else 1.0

    entities = traverse_entity(doc.modelspace(), factor_mm=factor_mm, resolution=resolution)
    layer_objects = OrderedDict()
    for layer, curve in entities:
        layer_objects.setdefault(layer, []).append(curve)

    if len(layer_objects) == 0:
        RDK.ShowMessage("No valid geometry found for: " + file_path, False)
        return None

    if merge_continuous_segments is None:
        merge_continuous_segments = robodialogs.ShowMessageYesNo("Do you want to merge connected curve segments into continuous contours?\n"
                                                                 "This can help simplify geometry, but it may reverse the direction of some curves.")

    if orient_closed_curves is None:
        orient_closed_curves = robodialogs.ShowMessageYesNo("Do you want to make nested closed curves consistent? Outer clockwise, inner counterclockwise.")

    if create_machining_project is None:
        create_machining_project = robodialogs.ShowMessageYesNo("Do you want to create a Curve Follow Project after import?")

    RDK.Render(False)

    objects = []
    base_name = Path(file_path).stem
    for layer, curves in layer_objects.items():
        layer_objects = []

        if merge_continuous_segments:
            curves = merge_connected_curves(curves)

        if orient_closed_curves:
            curves = _orient_nested_curves(curves)

        # Import in RoboDK
        for curve in curves:
            if len(curve) == 1:
                layer_objects.append(RDK.AddPoints(curve))
            else:
                layer_objects.append(RDK.AddCurve(curve))
            layer_objects[-1].setVisible(False)
            layer_objects[-1].setVisible(True)  # Force toggle from Object to Curve Object
        dxf = RDK.MergeItems(layer_objects)
        dxf.setName(base_name + " - " + layer)
        dxf.setVisible(False)  # Force toggle from Object to Curve Object
        dxf.setVisible(True)
        objects.append(dxf)

    RDK.Render(True)

    if len(objects) > 1:
        if robodialogs.ShowMessageYesNo("Multiple layers or shapes were imported.\n"
                                        "Do you want to merge them into a single object in RoboDK?"):
            RDK.Render(False)
            dxf = RDK.MergeItems(objects)
            dxf.setName(base_name)
            RDK.Render(True)

    RDK.ShowMessage("Done loading: " + file_path, False)

    if create_machining_project:
        RDK.Render(False)
        cfp = RDK.AddMachiningProject(dxf.Name())
        cfp.setMachiningParameters(part=dxf, params="ReorderAuto=0")
        RDK.Render(True)

    return dxf


def load_program(RDK=None, progs=None):
    """
    Convert RoboDK program(s) to curve(s).
    """

    def inst_pose(inst: str) -> robomath.Mat:
        from robodk.robomath import transl
        import math

        def rotx(deg):
            from robodk.robomath import rotx as rotx_rad
            return rotx_rad(math.radians(deg))

        def roty(deg):
            from robodk.robomath import roty as roty_rad
            return roty_rad(math.radians(deg))

        def rotz(deg):
            from robodk.robomath import rotz as rotz_rad
            return rotz_rad(math.radians(deg))

        try:
            return eval(inst)
        except:
            return None

    def get_item_from_inst_ptr(inst_ptr, RDK):
        """Get an item from an instruction pointer, typically a TargetPtr, FramePtr, ToolPtr, etc."""
        if inst_ptr == '0' or inst_ptr == 0:
            return None

        item = robolink.Item(RDK, str(inst_ptr))
        if not item.Valid(True) or str(item.item) != str(inst_ptr):
            return None

        return item

    if RDK is None:
        RDK = robolink.Robolink()

    if progs is None:
        progs = RDK.ItemUserPick('Select program to convert to a curve', RDK.ItemList(robolink.ITEM_TYPE_PROGRAM))
        if not progs.Valid():
            return None
        progs = [progs]
    else:
        progs = [x for x in progs if x.type in [robolink.ITEM_TYPE_PROGRAM]]
        if not progs:
            return None

    RDK.Render(False)
    curves = []
    for prog_item in progs:

        curve = []
        pose_frame = robomath.eye(4)
        for i in range(prog_item.InstructionCount()):
            inst_dict = prog_item.setParam(i)

            if inst_dict['Type'] == robolink.INS_TYPE_CHANGEFRAME:
                frame_item = get_item_from_inst_ptr(inst_dict['FramePtr'], RDK)
                if not frame_item:
                    pose_frame = inst_pose(inst_dict['Pose'])
                else:
                    pose_frame = frame_item.PoseAbs()

            if inst_dict['Type'] != robolink.INS_TYPE_MOVE:
                continue

            pose = inst_pose(inst_dict['Pose'])
            pose_abs = pose_frame * pose

            xyz = pose_abs.Pos()
            ijk = pose_abs.VZ()

            curve.append(xyz + ijk)

        if not curve:
            continue
        curves.append(curve)

    return curves


def transform_xyzijk(pose: robomath.Mat, xyzijk):
    new_xyz = pose * xyzijk[:3]
    if len(xyzijk) < 6:
        return new_xyz

    new_ijk = robomath.normalize3(pose.Rot33() * robomath.normalize3(xyzijk[3:6]))
    return new_xyz + new_ijk


def transform_curve(pose: robomath.Mat, curve):
    return [transform_xyzijk(pose, p) for p in curve]


def add_curve(reference_object, curve_points, add_to_ref=False, projection_type=robolink.PROJECTION_ALONG_NORMAL_RECALC, original_object_item=None):
    """
    Adds a curve (list of points) to an object, taking into consideration the object pose.
    Optionally, pass the original source object of the curve to transpose the points automatically to the new object.
    """
    # Curves/points are relative to the object origin (with no regard to the object pose), while AddCurve is relative to the object pose
    offset_pose_from = reference_object.Pose()
    if original_object_item is not None and original_object_item != reference_object:
        # Pose is the transformation matrix from the original object to the new object
        offset_pose_from = (original_object_item.PoseAbs().inv() * reference_object.Parent().PoseAbs()) * reference_object.Pose()

    offset_curve = transform_curve(offset_pose_from, curve_points)
    reference_object.AddCurve(offset_curve, add_to_ref, projection_type)


def add_points(reference_object, points, add_to_ref=False, projection_type=robolink.PROJECTION_ALONG_NORMAL_RECALC, original_object_item=None):
    """
    Adds points (list of points) to an object, taking into consideration the object pose.
    Optionally, pass the original source object of the points to transpose the points automatically to the new object.
    """
    # Curves/points are relative to the object origin (with no regard to the object pose), while AddPoints is relative to the object pose
    offset_pose_from = reference_object.Pose()
    if original_object_item is not None and original_object_item != reference_object:
        # Pose is the transformation matrix from the original object to the new object
        offset_pose_from = (original_object_item.PoseAbs().inv() * reference_object.Parent().PoseAbs()) * reference_object.Pose()

    offset_curve = transform_curve(offset_pose_from, points)
    reference_object.AddPoints(offset_curve, add_to_ref, projection_type)


def project_points(points, object: robolink.Item, project_on_surface=True, project_along_normal=True, recalculate_normals=True):
    """Projects a list of points to an object."""
    if not points:
        return []

    project_type = robolink.PROJECTION_NONE

    if project_on_surface and project_along_normal:
        project_type = robolink.PROJECTION_ALONG_NORMAL
        if recalculate_normals:
            project_type = robolink.PROJECTION_ALONG_NORMAL_RECALC
    elif project_on_surface and not project_along_normal:
        project_type = robolink.PROJECTION_CLOSEST
        if recalculate_normals:
            project_type = robolink.PROJECTION_CLOSEST_RECALC
    elif not project_on_surface and recalculate_normals:
        project_type = robolink.PROJECTION_RECALC
        if project_along_normal:
            project_type = robolink.PROJECTION_ALONG_NORMAL_RECALC
            # This adds an extra step as we need to revert the XYZ

    if project_type == robolink.PROJECTION_NONE:
        return points

    proj_points = object.ProjectPoints(points, project_type)
    if not project_on_surface and recalculate_normals and project_along_normal:
        for i in range(len(points)):
            proj_points[i][:3] = points[i][:3]

    return proj_points


def filter_straight_lines(points, tolerance_line_rad=0.01, check_normals=True, tolerance_normals_rad=0.01):
    """
    Remove intermediary points in what is considered a straight line.
    The normal of subsequent points must be equal to count as a line, unless specified otherwise.
    The first and last point will never be altered.
    """
    if len(points) < 3:
        # We need at least 3 points to simplify a straight line
        return points

    points_filtered = []

    # Find segments of straight lines across all the points
    i = 0
    while True:
        if i >= len(points) - 1:
            if i < len(points):
                points_filtered.append(points[i])
            break

        # Find the orientation vector from point A to point B
        pa = points[i]
        pb = points[i + 1]

        vab = robomath.subs3(pa, pb)
        if robomath.norm(vab) < 1e-6:
            # A and B are equal points, thus we can't determine the orientation vector
            points_filtered.append(pa)
            i += 1
            continue

        vab = robomath.normalize3(vab)

        # Group next points that share the same orientation vector as A to B
        j = i + 1
        segment = []
        while True:
            j += 1  # purposely starting at i+2

            if j >= len(points):
                break

            # Find the orientation vector from point A to point J. Note: as we get further from A, the apparent tolerance will decrease.
            pj = points[j]
            if robomath.distance(pa, pj) < 1e-6:
                # Points are overlapping. Check normals!
                if check_normals and len(pa) > 3 and len(pj) > 3 and abs(robomath.angle3(pa[3:6], pj[3:6])) > tolerance_normals_rad:
                    break
                segment.append(pj)
                continue

            vaj = robomath.normalize3(robomath.subs3(pa, pj))
            delta = abs(robomath.angle3(vab, vaj))
            if delta > tolerance_line_rad:
                break
            if check_normals and len(pa) > 3 and len(pj) > 3 and abs(robomath.angle3(pa[3:6], pj[3:6])) > tolerance_normals_rad:
                break
            segment.append(pj)

        if len(segment) > 0:
            # A, B and all points in the segment are a straight line! Add A and the last point in the line.
            points_filtered.append(pa)
            points_filtered.append(segment[-1])
            i = i + len(segment) + 1
        else:
            # A and B are not the beginning of a straight line. Try again with B as a start point.
            points_filtered.append(pa)
            i += 1

    return points_filtered


def filter_subsequent_duplicated_points(points, tolerance_mm=0.002, check_normals=False, tolerance_normals_rad=0.01):
    """Remove subsequent duplicated points. It does not wraps around (point 1 is not compared against point N-1)."""

    if len(points) < 2:
        # We need at least 2 points to remove duplicates
        return points

    points_filtered = []

    # Find segments of duplicated points across all the points
    i = 0
    while True:
        if i >= len(points) - 1:
            if i < len(points):
                points_filtered.append(points[i])
            break

        point = points[i]

        # Find a cluster
        j = i
        cluster = []
        while True:
            j += 1

            if j >= len(points):
                break

            # Two points are considered in the same cluster if they are bound to the same "circle" (distance from the first point)
            # This could lead to issues if you have a spiral curve and the cluster size is larger than the bounding area
            point_next = points[j]
            if robomath.distance(point[:3], point_next[:3]) > tolerance_mm:
                break

            # Two points can have the same XYZ but different normals (IJK), i.e. in a sharp corner
            if check_normals:
                if len(point) > 3 and len(point_next) > 3 and robomath.angle3(point[3:6], point_next[3:6]) > tolerance_normals_rad:
                    break

            cluster.append(point_next)

        if len(cluster) > 0:
            # We have a cluster! Keep the original point and move on to the next point after the cluster
            points_filtered.append(point)
            i = i + len(cluster) + 1
        else:
            # No duplicates, try again with the next point
            points_filtered.append(point)
            i += 1

    return points_filtered


def merge_curves(curves):
    """Merge a list of curves into one single curve (a curve is a list of points)."""
    merged_curve = []
    for curve in curves:
        merged_curve.extend(curve)
    return merged_curve


def get_curve(object_item, curve_id=0):
    """Retrieve the curve of an object item, as specified by the curve ID."""
    if object_item.type != robolink.ITEM_TYPE_OBJECT:
        return []
    return object_item.GetPoints(robolink.FEATURE_CURVE, curve_id)[0]


def get_curves(object_item):
    """Retrieve all the curves of an object item. Points are relative to the object origin."""
    object_curves = []
    i = 0
    while True:
        curve = get_curve(object_item, i)
        if not curve:
            break
        object_curves.append(curve)
        i += 1
    return object_curves


def get_points(object_item):
    if object_item.type != robolink.ITEM_TYPE_OBJECT:
        return []

    return object_item.GetPoints(robolink.FEATURE_POINT)[0]


def sort_curve_segments(segments, start=None, reverse_segments=False):
    """
    Sort the order of segments (list of curves) by distance from the end of a segment to the start of the next segment.
    Optionally, check both ends of the segments and reverse the order of the matched segment.
    Returns a sorted copy.
    """
    if start is None:
        start = segments[0]

    pass_by = segments.copy()
    sorted_segments = [start]

    delete_start = False
    if start in pass_by:
        pass_by.remove(start)
    else:
        delete_start = True

    while pass_by:

        if reverse_segments:
            # Check both ends of the segment, and reverse it if its a match
            nearest = min(pass_by, key=lambda x: min(robomath.distance(sorted_segments[-1][-1][:3], x[0][:3]), robomath.distance(sorted_segments[-1][-1][:3], x[-1][:3])))
            path_nearest = nearest.copy()
            if robomath.distance(sorted_segments[-1][-1][:3], nearest[-1][:3]) < robomath.distance(sorted_segments[-1][-1][:3], nearest[0][:3]):
                path_nearest.reverse()
        else:
            # Check only the first point
            nearest = min(pass_by, key=lambda x: robomath.distance(sorted_segments[-1][-1][:3], x[0][:3]))
            path_nearest = nearest.copy()

        sorted_segments.append(path_nearest)
        pass_by.remove(nearest)

    if delete_start:
        sorted_segments.remove(start)

    return sorted_segments


def split_discontinuous_curves(segments, tolerance_mm=50.0, start=None):
    """
    Split/group segments into separate curves objects based on continuity.
    """
    if start is None:
        start = segments[0]

    pass_by = segments.copy()
    grouped_segments = [[start]]

    delete_start = False
    if start in pass_by:
        pass_by.remove(start)
    else:
        delete_start = True

    while pass_by:

        nearest = min(pass_by, key=lambda x: robomath.distance(grouped_segments[-1][-1][-1][:3], x[0][:3]))
        distance = robomath.distance(grouped_segments[-1][-1][-1][:3], nearest[0][:3])
        if distance > tolerance_mm:
            grouped_segments.append([])

        path_nearest = nearest.copy()
        grouped_segments[-1].append(path_nearest)
        pass_by.remove(nearest)

    if delete_start:
        grouped_segments[0].pop(0)

    return grouped_segments


def closest_point(point_list, point):
    """
    Find the point in a list of points (a curve) that is the closest to another point.
    """
    return min(point_list, key=lambda x: robomath.distance(point[:3], x[:3]))


def closest_point_index(point_list, point):
    """
    Find the index of a point in a list of points (a curve) that is the closest to another point.
    """
    return point_list.index(closest_point(point_list, point))


def get_start_point(object_item, show_message=''):
    """
    Ask the user to click on the start point of a curve.
    Optionally, add a message to the user.
    Returns a point on the object, relative to the object origin.
    """
    RDK = object_item.RDK()
    RDK.setSelection([])

    if show_message:
        RDK.ShowMessage(str(show_message))
        RDK.ShowMessage(str(show_message), False)

    xyzijk = []
    APP = roboapps.RunApplication()
    while APP.Run():

        robomath.pause(0.01)

        is_selected, feature_type, feature_id = object_item.SelectedFeature()
        if not is_selected:
            continue

        # Clear the selection so that we get rising edge
        RDK.setSelection([])

        # If the user click on a surface, take the mouse point
        if feature_type == robolink.FEATURE_SURFACE:
            point_mouse, _ = object_item.GetPoints(robolink.FEATURE_SURFACE)
            if not point_mouse:
                continue
            xyzijk = point_mouse[0][:6]

        # If the user click on a curve, retrieve the curve and find the point closest to the mouse point
        elif feature_type == robolink.FEATURE_CURVE:
            point_mouse, _ = object_item.GetPoints(robolink.FEATURE_SURFACE)
            if not point_mouse:
                continue
            curve, _ = get_curve(object_item, feature_id)
            xyzijk = closest_point(curve, point_mouse[0][:6])
            print('Selection error: %.3f mm' % robomath.distance(xyzijk[:3], point_mouse[0][:3]))

        # If the user click on a point, use the point
        elif feature_type == robolink.FEATURE_POINT:
            point_mouse, _ = object_item.GetPoints(robolink.FEATURE_POINT)
            if not point_mouse:
                continue
            xyzijk = point_mouse[0][:6]

        print("Mouse on: '" + object_item.Name() + "', Feature type:" + str(feature_type) + ", Feature ID:" + str(feature_id) + ", Mouse point: " + str(point_mouse[0]))
        print("Point: " + str(xyzijk))
        break

    return xyzijk


def set_curve_ijk(curve, ijk):
    """
    Set the points normal (IJK) of a list of points (curve) to a fixed value.
    """
    return [point[:3] + ijk for point in curve]


def flip_curve_ijk(curve):
    """
    Flip the points normal (IJK) of a list of points (curve) to the opposite direction.
    """
    return [point[:3] + robomath.mult3(point[3:6], -1) if len(point) >= 6 else point for point in curve]


def offset_curve_fixed(curve, offset_xyz):
    """
    Add a fixed offset in XYZ on a list of points (curve)
    """
    return [robomath.add3(point[:3], offset_xyz) + point[3:6] if len(point) >= 6 else robomath.add3(point[:3], offset_xyz) for point in curve]


def offset_curve_ijk(curve, offset_distance):
    """Offsets a curve along the IJK vectors.

    Args:
        curve (list): A list of points, each point is a list or tuple [x, y, z, i, j, k].
        offset_distance (float): The distance to offset the curve.

    Returns:
        list: A new list of points with the curve offset.
    """
    offset_curve = []

    for idx in range(len(curve)):
        # Current point
        x, y, z = curve[idx][:3]
        i, j, k, = [0, 0, 1]
        if len(curve[i]) >= 6:
            i, j, k = curve[idx][3:6]

        # Calculate the new point offset
        offset_x = x + offset_distance * i
        offset_y = y + offset_distance * j
        offset_z = z + offset_distance * k

        # Append the new point to the offset curve
        offset_curve.append([offset_x, offset_y, offset_z, i, j, k])

    return offset_curve


def offset_curve_sideways(curve, offset_distance):
    """Offsets a curve sideways based on the cross product of direction and IJK vectors.

    Args:
        curve (list): A list of points, each point is a list or tuple [x, y, z, i, j, k].
        offset_distance (float): The distance to offset the curve sideways.

    Returns:
        list: A new list of points with the curve offset sideways.
    """
    offset_curve = []
    last_valid_direction = None

    for idx in range(len(curve)):
        # Current point
        x, y, z = curve[idx][:3]
        i, j, k, = [0, 0, 1]
        if len(curve[i]) >= 6:
            i, j, k = curve[idx][3:6]

        # If it's the last point, use the last valid direction
        direction = None
        if idx == len(curve) - 1 and last_valid_direction is not None:
            direction = last_valid_direction
        else:
            # Look ahead for the next distinct point to calculate the direction vector
            for lookahead_idx in range(idx + 1, len(curve)):
                next_x, next_y, next_z = curve[lookahead_idx][:3]
                direction = [next_x - x, next_y - y, next_z - z]
                if robomath.norm(direction) > 1e-6:  # Check if it's a distinct point
                    direction = robomath.normalize3(direction)  # Normalize the direction vector
                    last_valid_direction = direction
                    break

        if direction is None:
            # If no valid direction was found, use the original point
            offset_curve.append([x, y, z, i, j, k])
            continue

        # Calculate the cross product to find the "side" direction
        side_direction = robomath.normalize3(robomath.cross([i, j, k], direction))

        # Calculate the new point offset sideways
        offset_x = x + offset_distance * side_direction[0]
        offset_y = y + offset_distance * side_direction[1]
        offset_z = z + offset_distance * side_direction[2]

        # Append the new point to the offset curve
        offset_curve.append([offset_x, offset_y, offset_z, i, j, k])

    return offset_curve


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """
    pass


if __name__ == '__main__':
    runmain()
