# Run some performance tests of RoboDK using the RoboDK API for Python
# Note: for best performance you should use the API through the plug-in interface. Check the README.md file to learn more.

# You can also use the new version of the API:
from robodk import robolink    # RoboDK API
from robodk import robomath    # Robot toolbox
import random
import time
import platform
import os

robolink.import_install("psutil")

# Detailed CPU frequency/usage and RAM stats need psutil (pip install psutil).
# Without it we still report what the standard library exposes (CPU name and logical core count).
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


def print_hardware_info():
    """Print CPU and RAM information about this PC."""
    print("---- Hardware information ----")
    print("OS: %s %s (%s)" % (platform.system(), platform.release(), platform.machine()))
    print("CPU: %s" % (platform.processor() or platform.machine()))
    print("CPU cores (logical): %s" % os.cpu_count())

    if HAS_PSUTIL:
        print("CPU cores (physical): %s" % psutil.cpu_count(logical=False))
        try:
            # Not implemented by psutil on some platforms (e.g. Apple Silicon Macs)
            freq = psutil.cpu_freq()
        except Exception:
            freq = None
        if freq:
            print("CPU frequency: %.0f MHz (max: %.0f MHz)" % (freq.current, freq.max))
        print("CPU usage: %.1f %%" % psutil.cpu_percent(interval=0.1))
        mem = psutil.virtual_memory()
        print("RAM total: %.2f GB" % (mem.total / (1024 ** 3)))
        print("RAM available: %.2f GB (%.1f %% used)" % (mem.available / (1024 ** 3), mem.percent))
    else:
        print("Tip: install 'psutil' (pip install psutil) to also report CPU frequency/usage and RAM size.")
    print("-------------------------------")


print_hardware_info()

# Start the RoboDK API
RDK = robolink.Robolink()

robot = RDK.Item("", robolink.ITEM_TYPE_ROBOT_ARM)

print("Using robot: %s" % robot.Name())

# Retrieve the joint limits as a list to retrieve random sets of robot joints
j_low, j_high, _ = robot.JointLimits()
j_low = j_low.list()
j_high = j_high.list()
def joints_rand():
    jnts = [random.uniform(l, h) for l, h in zip(j_low, j_high)]
    return jnts


def run_benchmark(name, func, n_tests=10000):
    """Run func() n_tests times and print the average time per call, in microseconds."""
    t_start = time.perf_counter()
    for _ in range(n_tests):
        func()
    t_end = time.perf_counter()
    t_avg_us = (t_end - t_start) * 1e6 / n_tests
    print("%s: %.3f microseconds/call (%d samples)" % (name, t_avg_us, n_tests))
    return t_avg_us


def solve_fk_once():
    """Compute the forward kinematics for a random set of joints. Some random joints
    can be unreachable/singular and make SolveFK raise an exception: skip those samples."""
    try:
        return robot.SolveFK(joints_rand())
    except Exception:
        return None


def solve_ik_once(pose):
    """Compute the inverse kinematics for a given pose. Some poses can be unreachable
    and make SolveIK raise an exception: skip those samples."""
    try:
        return robot.SolveIK(pose)
    except Exception:
        return None


print("\n---- Kinematics performance ----")

# Test the SolveFK function (robot.SolveFK on random joints)
run_benchmark("Forward Kinematics (SolveFK)", solve_fk_once)

# Test the SolveIK function (robot.SolveIK on random joints)
pose_fk = robot.SolveFK(joints_rand())
run_benchmark("Inverse Kinematics (SolveIK)", lambda: solve_ik_once(pose_fk))


# Test collisions: run for a fixed amount of time and collect statistics
print("\n---- Collision check performance ----")

t_start = time.perf_counter()
t_check = t_start + 4
count = 0
n_with_collision = 0
n_without_collision = 0

# Turn off automatic rendering (usualy immediately after a call that updates the scene)
RDK.Render(False)
# Turn collisions off on each setJoints, we'll retrieve the collision status using Collisions()
RDK.setCollisionActive(robolink.COLLISION_OFF)
while time.perf_counter() < t_check:
    joints = joints_rand()
    robot.setJoints(joints)

    # Provokes an update to refresh the position of every robot, tool, object in the scene without rendering
    RDK.Update()

    # Calculate collisions and collect how many samples were in collision vs not
    n_collisions = RDK.Collisions()
    if n_collisions > 0:
        n_with_collision += 1
    else:
        n_without_collision += 1

    count = count + 1

t_end = time.perf_counter()

# Show metrics
t_delta = t_end - t_start
print("Total samples: %d" % count)
print("Total time: %.3f s" % t_delta)
print("Collision check time: %.3f ms/sample" % ((t_delta / count) * 1e3))
print("Collision check throughput: %.2f samples/sec" % (count / t_delta))
print("Samples with collisions (nCollisions>0): %d" % n_with_collision)
print("Samples without collisions (nCollisions<=0): %d" % n_without_collision)
