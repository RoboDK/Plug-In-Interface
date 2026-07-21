"""Runs the PluginExample benchmark headlessly against a sample RoboDK station.

This script:
  1. Downloads a sample station (.rdk) into a temp folder, skipping the download if it is
     already there.
  2. Starts a new, headless RoboDK instance.
  3. Makes sure PluginExample is loaded.
  4. Opens the downloaded station.
  5. Triggers the plugin's "BenchmarkInfo" command for a given program.
  6. Prints the resulting benchmark report, which RoboDK streams to its own console/stdout
     (Robolink automatically relays it to this script's stdout).

Usage:
    python run_plugin_benchmark.py
"""

import os
import sys
import tempfile
import urllib.request

from robodk import robolink

STATION_URL = "https://cdn.robodk.com/downloads-library/library-stations/Welding-with-Comau-Smart5-NJ-130-2-6.rdk"
PLUGIN_NAME = "PluginExample"  # Matches PluginExample.pro's TARGET, used to load the plugin
PLUGIN_ID = "Example Plugin"  # Matches PluginExample::PluginName(), used to target PluginCommand
PROGRAM_NAME = "main"  # Program to run the collision check against

from importlib.metadata import version, PackageNotFoundError

MIN_ROBODK_VERSION = "6.0.0"


def check_robodk_version(min_version=MIN_ROBODK_VERSION):
    """Make sure the installed robodk package meets the minimum required version."""
    try:
        installed_version = version("robodk")
    except PackageNotFoundError:
        sys.exit("Could not find the 'robodk' package version. Run: pip install --upgrade robodk")

    installed_tuple = tuple(int(part) for part in installed_version.split(".")[:3])
    min_tuple = tuple(int(part) for part in min_version.split(".")[:3])
    if installed_tuple < min_tuple:
        sys.exit("This script requires robodk >= %s (found %s). This is needed to show the results in the console. Run: pip install --upgrade robodk" % (min_version, installed_version))

    print("robodk package version: %s (OK, >= %s)" % (installed_version, min_version))


check_robodk_version()


def download_station(url: str) -> str:
    """Download a station file to a temp folder. Skips the download if it is already there."""
    temp_dir = os.path.join(tempfile.gettempdir(), "robodk_benchmark")
    os.makedirs(temp_dir, exist_ok=True)

    filepath = os.path.join(temp_dir, os.path.basename(url))
    if os.path.exists(filepath):
        print("Station already downloaded: %s" % filepath)
        return filepath

    print("Downloading %s ..." % url)
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(request) as response, open(filepath, "wb") as f:
            f.write(response.read())
    except Exception as e:
        # Clean up a partially written file so a retry does not mistake it for a full download
        if os.path.exists(filepath):
            os.remove(filepath)
        sys.exit("Failed to download %s: %s" % (url, e))

    print("Saved to: %s" % filepath)
    return filepath

def print_custom(txt):
    global do_print_stdout
    if do_print_stdout:
        print(txt)

def main():
    global do_print_stdout
    do_print_stdout = False

    station_path = download_station(STATION_URL)

    # Start a new, headless RoboDK instance.
    # -DEBUG is required for qDebug()-based plugin console output (such as the benchmark
    # report) to actually be printed; Robolink relays RoboDK's stdout to ours automatically.
    print("Starting a new headless RoboDK instance...")
    RDK = robolink.Robolink(args=["-NEWINSTANCE", "-NOUI", "-EXIT_LAST_COM", "-SKIPINI", "-Settings=LicenseLoad"], close_std_out=print_custom)

    if RDK.Command("LHasMaint") != "1":
        msg = "You need a license to run collision checking benchmarks"
        sys.exit(msg)

    print("Loading plugin: %s" % PLUGIN_NAME)
    if not RDK.PluginLoad(PLUGIN_NAME):
        msg = "Failed to load plugin: %s. Are you using the latest version? Is the plugin properly installed?" % PLUGIN_NAME
        sys.exit(msg)

    print("Opening station: %s" % station_path)
    station = RDK.AddFile(station_path)
    if not station.Valid():
        msg = "Failed to open station: %s" % station_path
        sys.exit(msg)

    print("=" * 70)
    print("Running BenchmarkInfo=%s (output below is streamed live from RoboDK)" % PROGRAM_NAME)
    print("=" * 70)
    do_print_stdout = True
    result = RDK.PluginCommand(PLUGIN_ID, "BenchmarkInfo", PROGRAM_NAME)
    do_print_stdout = False
    print("=" * 70)
    print("Plugin Command result: %s" % result)

    print("Closing RoboDK...")
    RDK.CloseRoboDK()


if __name__ == "__main__":
    main()
