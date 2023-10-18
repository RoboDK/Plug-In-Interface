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

from robodk import robolink, robomath, roboapps


def project_points(points, object: robolink.Item, project_on_surface=True, project_along_normal=True, recalculate_normals=True):
    """Projects a list of points to an object."""
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
    return object_item.GetPoints(robolink.FEATURE_CURVE, curve_id)[0]


def get_curves(object_item):
    """Retrieve all the curves of an object item. Points are relative to the object origin."""
    object_curves = []
    i = 0
    while True:
        curve = object_item.GetPoints(robolink.FEATURE_CURVE, i)[0]
        if not curve:
            break
        object_curves.append(curve)
        i += 1
    return object_curves


def sort_curve_segments(segments, start=None, reverse_segments=False):
    """
    Sort the order of segments (list of curves) by distance from the end of a segment to the start of the next segment.
    Optionally, check both ends of the segments reverse the order of the matched segment.
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
            curve, _ = object_item.GetPoints(robolink.FEATURE_CURVE, feature_id)
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


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """
    pass


if __name__ == '__main__':
    runmain()