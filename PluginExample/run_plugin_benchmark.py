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
import time
import urllib.request

from robodk import robolink

STATION_URL = "https://cdn.robodk.com/downloads-library/library-stations/Welding-with-Comau-Smart5-NJ-130-2-6.rdk"
PLUGIN_NAME = "PluginExample"  # Matches PluginExample.pro's TARGET, used to load the plugin
PLUGIN_ID = "Example Plugin"  # Matches PluginExample::PluginName(), used to target PluginCommand
PROGRAM_NAME = "MainProg"  # Program to run the collision check against


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


def main():
    station_path = download_station(STATION_URL)

    # Start a new, headless RoboDK instance.
    # -DEBUG is required for qDebug()-based plugin console output (such as the benchmark
    # report) to actually be printed; Robolink relays RoboDK's stdout to ours automatically.
    print("Starting a new headless RoboDK instance...")
    RDK = robolink.Robolink(args=["-NEWINSTANCE", "-NOUI", "-EXIT_LAST_COM", "-SKIPINI", "-Settings=LicenseLoad"])

    print("Loading plugin: %s" % PLUGIN_NAME)
    if False:#not RDK.PluginLoad(PLUGIN_NAME):
        msg = "Failed to load plugin: %s. Are you using the latest version? Is the plugin properly installed?" % PLUGIN_NAME
        print(msg)
        sys.exit(msg)

    print("Opening station: %s" % station_path)
    station = RDK.AddFile(station_path)
    if not station.Valid():
        msg = "Failed to open station: %s" % station_path
        print(msg)
        sys.exit(msg)

    print("=" * 70)
    print("Running BenchmarkInfo=%s (output below is streamed live from RoboDK)" % PROGRAM_NAME)
    print("=" * 70)
    result = RDK.PluginCommand(PLUGIN_ID, "BenchmarkInfo", PROGRAM_NAME)

    # Give RoboDK's console output a moment to reach us before we close the connection
    time.sleep(9)
    print("=" * 70)
    print("PluginCommand result: %s" % result)

    print("Closing RoboDK...")
    RDK.CloseRoboDK()


if __name__ == "__main__":
    main()
