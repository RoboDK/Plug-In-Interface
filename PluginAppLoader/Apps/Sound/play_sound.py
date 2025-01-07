import os
import sys
import time

from multiprocessing import shared_memory

def runmain():
    try:
        request = shared_memory.ShareableList(name = "rdk_sound_request")
        response = shared_memory.ShareableList(name = "rdk_sound_response")
    except Exception:
        request = None
        response = None
        print("Unable to connect to the Sound Emitter")

    if not request or not response:
        return

    index = 0
    command = "PlayBlocking"
    blocking = False
    filename = ""
    repeat = 0
    left_volume = 1.0
    right_volume = 1.0

    # Arguments order:
    #   [0] Script Name
    #   [1] Item Pointer
    #   [2] Sound File
    #   [3] (optional) Command: [PlayBlocking, Play, Status, Stop, StopAll]
    #   [4] (optional) Repeat (-1 means forever)
    #   [5] (optional) Left Volume (-1.0 means determine from the station)
    #   [6] (optional) Right Volume (-1.0 means determine from the station)
    if len(sys.argv) < 3:
        print("Not enough input arguments")
        return

    try:
        index = int(sys.argv[1])
    except ValueError:
        index = 0

    filename = str(sys.argv[2])

    if len(sys.argv) > 3:
        command = str(sys.argv[3])

    if command == "PlayBlocking":
        command = "Play"
        blocking = True

    if command == "Status":
        blocking = True

    if len(sys.argv) > 4:
        try:
            repeat = int(sys.argv[4])
        except ValueError:
            repeat = 0

        # Prevent to block forever
        if repeat < 0 and blocking:
            repeat = 0

    if len(sys.argv) > 5:
        try:
            left_volume = float(sys.argv[5])
        except ValueError:
            left_volume = 1.0
        right_volume = left_volume

    if len(sys.argv) > 6:
        try:
            right_volume = float(sys.argv[6])
        except ValueError:
            right_volume = left_volume


    if left_volume < 0.0:
        left_volume = 1.0
    if right_volume < 0.0:
        right_volume = 1.0

    response[0] = ""

    request[1] = filename
    request[2] = index
    request[3] = repeat
    request[4] = left_volume
    request[5] = right_volume
    request[0] = command

    counter = 0
    timeout = True
    while counter < 10:
        status = response[0]
        if status in ["Playing", "Finished", "Error"]:
            timeout = False
            if status == "Playing" and blocking:
                response[0] = ""
                request[0] = "Status"
            else:
                break
        else:
            counter = counter + 1

        time.sleep(0.1)

    if timeout:
        print("Request timeout")
        return

if __name__ == "__main__":
    runmain()