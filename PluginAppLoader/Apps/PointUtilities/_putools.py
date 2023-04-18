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

from robodk import robolink, robomath


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
            vaj = robomath.normalize3(robomath.subs3(pa, pj))
            delta = abs(robomath.angle3(vab, vaj))
            if delta > tolerance_line_rad:
                break
            if check_normals:
                if len(pa) > 3 and len(pj) > 3 and abs(robomath.angle3(pa[3:6], pj[3:6])) > tolerance_normals_rad:
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


def get_points(object_item):
    """Retrieve the curve of an object item, as specified by the curve ID."""
    return object_item.GetPoints(robolink.FEATURE_POINT)[0]


def sort_points(segments, start=None):
    """
    Sort the order of points by distance from the from the previous point.
    Returns a sorted copy.
    """
    if start is None:
        start = segments[0]
    else:
        if start not in segments:
            start = min(segments, key=lambda x: robomath.distance(start, x[:3]))

    pass_by = segments.copy()
    sorted_segments = [start]

    print(pass_by)

    if start in pass_by:
        pass_by.remove(start)

    print(pass_by)

    while pass_by:
        prev = sorted_segments[-1][:3]
        nearest = min(pass_by, key=lambda x: robomath.distance(prev, x[:3]))
        path_nearest = nearest.copy()

        sorted_segments.append(path_nearest)
        pass_by.remove(nearest)

    return sorted_segments


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """
    pass


if __name__ == '__main__':
    runmain()