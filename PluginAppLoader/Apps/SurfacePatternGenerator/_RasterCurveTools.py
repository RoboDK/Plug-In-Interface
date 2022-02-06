from robodk import robolink, robomath

# Set other constants:
TOL_PROJ_Z = robomath.sqrt(2)  # Tolerance to ignore a point as a ratio (if it falls through a window for example)


# Show message through the GUI, RoboDK and the console
def ShowMsg(msg):
    #print(msg)
    #NotifyGUI.set(msg)
    #root.update_idletasks()
    RDK = robolink.Robolink()
    RDK.ShowMessage(msg, False)


def Pose_x_XYZijk(pose, xyzijk):
    """ Function to change the coordinates of a point and a normal given a pose. The point and the normal must be in xyzijk format."""
    new_xyz = pose * xyzijk[0:3]
    new_ijk = pose[:3, :3] * xyzijk[3:6]
    return new_xyz + new_ijk


def GridPoints(ref, size_x, size_y, step_x, step_y, cover_all=False, even_distribution=False, continuous=False, angle_triangle=0.0):
    """
    Generates a list of lines, each containing a list of xyzijk points, from a grid size.
    By default, this will generate (size / step) "horizontal" lines along the y axis of the reference.

    ref: reference pose to apply to the points, corresponding to the origin
    size_x: size of the grid along the x axis of the reference
    size_y: size of the grid along the y axis of the reference
    step_x: step size between points along the x axis of the reference. If size / step is not a integer, the generated grid will be cropped.
    step_y: step size between points along the y axis of the reference. If size / step is not a integer, the generated grid will be cropped.
    continuous: If true, each "horizontal" lines will be connected to the next in a zig-zag pattern, resulting in one single line
    """
    lines = []
    flip = 1  # 1 => Y+  -1 => Y-
    index_x = 0
    index_y = 0
    limit_inf_y = 0
    limit_sup_y = size_y
    if even_distribution:
        if size_x % step_x:
            step_x = size_x / (int(size_x / step_x) + 1)

    while index_x <= size_x:
        line = []

        # Left to right?
        if flip > 0:
            index_y = limit_inf_y
        else:
            index_y = limit_sup_y

        # Create points along the y axis
        while index_y <= limit_sup_y and index_y >= limit_inf_y:
            xyzijk = Pose_x_XYZijk(ref, [index_x, index_y, 0, 0, 0, -1])
            line.append(xyzijk)
            index_y = index_y + flip * step_y
        # Make sure points are covering the surface from along the Y axis
        if index_y < limit_inf_y and index_y + step_y != limit_inf_y:
            xyzijk = Pose_x_XYZijk(ref, [index_x, limit_inf_y, 0, 0, 0, -1])
            line.append(xyzijk)
        elif index_y > limit_sup_y and index_y - step_y != limit_sup_y:
            xyzijk = Pose_x_XYZijk(ref, [index_x, limit_sup_y, 0, 0, 0, -1])
            line.append(xyzijk)

        line = [[round(val, 15) for val in pt] for pt in line]  # fix attempt
        lines.append(line)

        # Move to the next X index
        index_x = index_x + step_x
        if index_x == size_x:
            cover_all = False
        if index_x >= size_x and cover_all:
            cover_all = False
            index_x = size_x

        if angle_triangle:
            limit_inf_y = index_x * robomath.sin(angle_triangle / 180 * robomath.pi) / robomath.sin((90 - angle_triangle) / 180 * robomath.pi)
            limit_sup_y = size_y - (index_x * robomath.sin(angle_triangle / 180 * robomath.pi) / robomath.sin((90 - angle_triangle) / 180 * robomath.pi))
        flip = -1 * flip

    if continuous:
        # Merge lines into a single line
        lines = [[points for line in lines for points in line]]

    return lines


#---------------------------------------------
# Function definition to offset a list of points
def PointsOffset(points, offset):
    points_offset = []
    for pi in points:
        x, y, z, i, j, k = pi
        xyz2 = robomath.add3([x, y, z], robomath.mult3([i, j, k], offset))
        xyzijk2 = xyz2 + [i, j, k]
        points_offset.append(xyzijk2)
    return points_offset


#---------------------------------------------
# Main program call that will project the path to a surface
def CreatePaths(REF, PART, SIZE_X, SIZE_Y, STEP_X, STEP_Y, REPEAT_TIMES=1, REPEAT_OFFSET=2, cover_all=False, even_distribution=False, continuous=False, angle_triangle=0.0):
    """
    Create an object containing the curves
    REF: Reference frame item
    PART: Object item
    """

    if not REF.Valid() or not PART.Valid() or REF.Type() != robolink.ITEM_TYPE_FRAME or PART.Type() != robolink.ITEM_TYPE_OBJECT:
        return

    RDK = PART.RDK()

    # Retrieve the reference name
    REF_NAME = REF.Name()

    ShowMsg("Working with %s ..." % REF_NAME)

    # Get the pose of the reference with respect to the part:
    pose_ref_wrt_part = robomath.invH(PART.Parent().PoseAbs()) * REF.PoseAbs()

    # For later: calculate the inverse pose (part with respect to the reference)
    pose_part_wrt_ref = robomath.invH(pose_ref_wrt_part)

    # Generate the curve path
    # IMPORTANT: the point coordinates must be relative to the part reference
    lines = GridPoints(pose_ref_wrt_part, SIZE_X, SIZE_Y, STEP_X, STEP_Y, cover_all, even_distribution, continuous, angle_triangle)
    if len(lines) == 0:
        ShowMsg("No points found for: " + REF_NAME)
        return

    # Remove any previously generated objects with the same name as the reference frame:
    obj_delete = RDK.Item(REF_NAME, robolink.ITEM_TYPE_OBJECT)
    if obj_delete.Valid():
        obj_delete.Delete()

    ShowMsg("Projecting %s to surface..." % REF_NAME)

    # Project the points on the object surface
    projected_lines = [PART.ProjectPoints(robomath.Mat(line).tr(), robolink.PROJECTION_ALONG_NORMAL_RECALC).tr().rows for line in lines]

    import numpy as np
    lines = np.array(lines).round(6).tolist()
    projected_lines = np.array(projected_lines).round(6).tolist()

    points_object = None
    for line, line_projected in zip(lines, projected_lines):

        line_projected_filtered = []

        if len(line) != len(line_projected):
            print("Projection failed on some points!")

        # Remember the last valid projection
        pti_last = None
        for i in range(len(line_projected)):
            # retrieve projected and non projected points, with respect to the reference frame
            # retrieve the next point to test if the projection went too far

            point = line[i]
            proj_point = line_projected[i]
            pti = Pose_x_XYZijk(pose_part_wrt_ref, point)
            pti_proj = Pose_x_XYZijk(pose_part_wrt_ref, proj_point)

            if abs(pti_proj[2]) < 1e-3:
                # There is an bug with ProjectPoints, and sometimes points are not projected correctly.
                # Try to recover the point by using the closest method.
                # Note: if the ref is exactly on the surface.. this might break
                print("Point not projected correctly! Ignoring..")
                continue

            # Check if we have the first valid projected point
            if pti_last is None:
                line_projected_filtered.append(pti_proj)
                pti_last = pti
                pti_proj_last = pti_proj
                continue

            # Check if the projection falls through a "window" or "climbs" a wall with respect to the previous pointS
            if robomath.distance(pti_proj, pti_proj_last) > TOL_PROJ_Z * robomath.distance(pti, pti_last):
                #print("Point falls through or climbs, skipping")
                continue

            # List the point as valid
            line_projected_filtered.append(pti_proj)

            # Remember the last valid projection
            pti_last = pti
            pti_proj_last = pti_proj

        # TODO: This is temporary code to fix the normals that sometimes break
        # This needs to be done once all invalid projected points are removed
        import numpy as np
        ijk_array = np.array(np.array(line_projected_filtered)[:, 3:6]).round(8)
        mean_ijk = ijk_array.mean(axis=0).round(8)
        std_ijk = ijk_array.std(axis=0).round(8)
        if sum(std_ijk) > 0:
            ijk_range = [mean_ijk - std_ijk, mean_ijk + std_ijk]
            filtered_ijk_array = np.array([ijk for ijk in ijk_array if all(np.greater_equal(ijk, ijk_range[0])) and all(np.less_equal(ijk, ijk_range[1]))])
            mean_ijk = filtered_ijk_array.mean(axis=0)
        mean_ijk = list(mean_ijk)

        for pt in line_projected_filtered:
            pt[3:6] = mean_ijk

        if len(line_projected_filtered) == 0:
            # no projection found. Skip
            continue

        if points_object is None:
            ShowMsg("Creating object for %s..." % REF_NAME)
            # Add the points as an object in the RoboDK station tree
            points_object = RDK.AddCurve(line_projected_filtered, projection_type=robolink.PROJECTION_NONE)
            # Add the points to the reference and set the reference name
            points_object.setParent(REF)
            points_object.setName(REF_NAME)
        else:
            # Add curve to existing object
            RDK.AddCurve(line_projected_filtered, points_object, True, projection_type=robolink.PROJECTION_NONE)

        for rep in range(1, round(REPEAT_TIMES)):
            # Calculate a new curve with respect to the reference curve
            points_projected_filtered_rep = PointsOffset(line_projected_filtered, REPEAT_OFFSET * rep)

            #  Add the shifted curve without projecting it
            points_object = RDK.AddCurve(points_projected_filtered_rep, points_object, True, robolink.PROJECTION_NONE)

    return points_object


def CreateProgram(REF, SPEED_OPERATION, ANGLE_TCP_X, ANGLE_TCP_Y):
    # Retrieve the reference name
    REF_NAME = REF.Name()

    RDK = REF.RDK()

    ShowMsg("Working with %s ..." % REF_NAME)

    # Remove any previously generated objects with the same name as the reference frame:
    points_object = RDK.Item(REF_NAME, robolink.ITEM_TYPE_OBJECT)
    if not points_object.Valid():
        print("No projection found for %s" % REF_NAME)
        return

    curve_follow = RDK.Item(REF_NAME, robolink.ITEM_TYPE_MACHINING)
    if not curve_follow.Valid():
        curve_follow = RDK.AddMachiningProject(REF_NAME)

    ShowMsg("Solving toolpath for %s" % REF_NAME)

    # Use the current reference frame:
    curve_follow.setPoseFrame(REF)

    # RoboDK 3.3.7 or later required:
    curve_follow.setSpeed(SPEED_OPERATION)
    curve_follow.setPoseTool(robomath.rotx(ANGLE_TCP_X * robomath.pi / 180.0) * robomath.roty(ANGLE_TCP_Y * robomath.pi / 180.0))

    #TODO: This call is causing RoboDK to hang until this process is killed..
    prog, status = curve_follow.setMachiningParameters(part=points_object)
    print(status)
    if status == 0:
        ShowMsg("Program %s generated successfully" % REF_NAME)
    else:
        ShowMsg("Issues found generating program %s!" % REF_NAME)

    # get the program name
    if prog.Valid():
        return prog
    return None


def CreateMainProgram(PART, prog_name_list):

    # Create a new program that calls the auto generated program
    # Make sure we delete any previously generated programs with the same name

    RDK = PART.RDK()

    ShowMsg("Creating Main program ...")
    prog_main_name = "Main" + PART.Name()
    prog_main = RDK.Item(prog_main_name, robolink.ITEM_TYPE_PROGRAM)
    if prog_main.Valid():
        prog_main.Delete()
    prog_main = RDK.AddProgram(prog_main_name)

    # Add a number of program calls to the first program by providing inline code
    #prog_main.RunCodeCustom("FOR i=1 TO 5", INSTRUCTION_INSERT_CODE)
    #prog_main.RunCodeCustom(prog_name, INSTRUCTION_CALL_PROGRAM)
    #prog_main.RunCodeCustom("NEXT", INSTRUCTION_INSERT_CODE)
    #for i in range(4):
    for pr_name in prog_name_list:
        prog_main.RunCodeCustom(pr_name, robolink.INSTRUCTION_CALL_PROGRAM)

    # Start the program simulation:
    #prog_main.RunProgram() # This will freeze the UI
    ShowMsg("Done!!")
