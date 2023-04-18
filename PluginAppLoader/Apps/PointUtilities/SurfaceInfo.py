# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Click an object's surface to print its geometry features.
# Best-fit planes, spheres and cylinders.
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

import Settings

robolink.import_install('numpy')
import numpy as np
from enum import Enum


class Geometry(Enum):
    Unknown = 0  # Make sure these matches with RDK.Command('FitGeometry')
    Plane = 1
    Cylinder = 2
    Sphere = 3


def get_object_mesh(object_item, feature_id=-1):
    if feature_id != -1:
        return [object_item.GetPoints(robolink.FEATURE_OBJECT_MESH, feature_id)[0]]

    object_mesh = []
    i = 0
    while True:
        feature_mesh = object_item.GetPoints(robolink.FEATURE_OBJECT_MESH, i)[0]
        if not feature_mesh:
            break
        object_mesh.append(feature_mesh)
        i += 1
    return object_mesh


def get_object_point_cloud(object_item, feature_id=-1, include_normals=True):
    return mesh_to_point_cloud(get_object_mesh(object_item, feature_id), include_normals)


def mesh_to_point_cloud(object_mesh, include_normals=True):
    point_cloud = [point for feature in object_mesh for point in feature]
    if include_normals:
        return np.unique(point_cloud, axis=0).tolist()
    return np.unique(np.array(point_cloud)[:, :3], axis=0).tolist()


def print_geometry(selected_object, point_mouse, feature_id, geometry_data):
    if not geometry_data:
        return

    geo_type = Geometry(int(geometry_data[0]))
    point = tuple(geometry_data[1:4])  # Point on plane or point on cylinder axis (typically center point)
    axis = tuple(geometry_data[4:7])  # Plane normal or cylinder axis
    mean_err = float(geometry_data[7])
    max_err = float(geometry_data[8])
    radius = 0.0
    if geo_type in [Geometry.Cylinder, Geometry.Sphere]:
        radius = float(geometry_data[9])

    px, py, pz = point
    ax, ay, az = axis
    mx, my, mz = point_mouse[0][:3]
    selected_object.RDK().ShowMessage(f"'{selected_object.Name()}' [{feature_id}]@[{mx:.3g}, {my:.3g}, {mz:.3g}] mm : {geo_type.name} | Center: [{px:.3g}, {py:.3g}, {pz:.3G}] | Axis: [{ax:.3g}, {ay:.3g}, {az:.3g}] mm | Radius: [{radius:.3g}] mm | Mean/Max Error: [{mean_err:.3g}/{max_err:.3g}] mm", False)


def SurfaceInfo(RDK=None, S=None):
    """
    Click an object's surface to print its geometry features.
    Best-fit planes, spheres and cylinders.
    """

    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = Settings.Settings()
        S.Load(RDK)

    # Clear the selection so that we get a 'rising edge'
    RDK.setSelection([])

    selected_object_prev = None
    point_mouse_prev = None
    feature_id_prev = None
    geometry_data_prev = None

    APP = roboapps.RunApplication()
    while APP.Run():

        robomath.pause(0.3)

        # Get the object under the mouse
        selected_object, feature_type, _, _, _ = RDK.GetPoints(robolink.FEATURE_HOVER_OBJECT)
        if feature_type != robolink.FEATURE_SURFACE or not selected_object.Valid() or selected_object.Type() not in [robolink.ITEM_TYPE_OBJECT]:
            continue

        # Get the point on the object under the mouse (last click)
        point_mouse, _ = selected_object.GetPoints(robolink.FEATURE_SURFACE)
        if not point_mouse:
            continue

        # Avoid doing repeated calls
        if selected_object_prev == selected_object and point_mouse_prev == point_mouse:
            print_geometry(selected_object, point_mouse, feature_id_prev, geometry_data_prev)
            continue

        # Get the feature ID of the surface
        mesh_stats = selected_object.setParam("ClosestMesh", robomath.Mat(point_mouse))
        if type(mesh_stats) != robomath.Mat:
            # Requires RoboDK 5.5.5+
            RDK.ShowMessage('This version of RoboDK does not support this feature. Please update RoboDK.')
            break
        mesh_stats = mesh_stats.tolist()
        proj_point = mesh_stats[:3]
        proj_normal = mesh_stats[3:6]
        distance = mesh_stats[6]
        feature_id = int(mesh_stats[7])
        if distance > 3:
            continue

        # Avoid doing repeated calls
        if selected_object_prev == selected_object and feature_id_prev == feature_id:
            print_geometry(selected_object, point_mouse, feature_id, geometry_data_prev)
            continue

        # Get the mesh of the feature
        feature_mesh = get_object_point_cloud(selected_object, feature_id, False)
        if len(feature_mesh) > 10000:
            # RoboDK will hand on larges mesh (and this is unlikely a primitive)
            continue

        # Best-fit it
        points_mat = robomath.Mat(feature_mesh)[:, :3].tr()
        geometry_data = RDK.Command("FitGeometry", points_mat)
        if len(geometry_data) <= 0:
            continue
        geometry_data = geometry_data[0].tolist()
        if not geometry_data:
            continue

        # Show it
        print_geometry(selected_object, point_mouse, feature_id, geometry_data)

        selected_object_prev = selected_object
        point_mouse_prev = point_mouse
        feature_id_prev = feature_id
        geometry_data_prev = geometry_data


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        SurfaceInfo()


if __name__ == '__main__':
    runmain()