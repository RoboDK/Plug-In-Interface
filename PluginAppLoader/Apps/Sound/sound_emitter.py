import os
import math

from multiprocessing import shared_memory
from pathlib import Path
from pygame import mixer, time
from robodk import robolink, robomath, roboapps

g_vr_mode = False

def adjust_channel_volume(RDK, channel, item):
    global g_vr_mode

    if g_vr_mode:
        pose_head_str = RDK.Command("ViewPoseVR")
        values = []
        for valstr in pose_head_str.split(","):
            values.append(float(valstr))
        pose_head_inv = robomath.TxyzRxyz_2_Pose(values)
    else:
        pose_head_inv = RDK.ViewPose()

    distance_max = 10000
    angle_max = math.pi/2

    pos_sound = item.PoseAbs().Pos()
    head2sound = pose_head_inv * pos_sound
    distance = robomath.norm(head2sound)
    angle_left = robomath.angle3([-1, 0, 0], head2sound)
    angle_right = robomath.angle3([1, 0, 0], head2sound)
    volume = max(0, (distance_max - distance) / distance_max)
    volume_left = volume * max(0.2, (angle_max - angle_left) / angle_max)
    volume_right = volume * max(0.2, (angle_max - angle_right) / angle_max)
    channel.set_volume(volume_left, volume_right)

def search_item(RDK, index):
    if index < 1:
        return None

    bindings = []
    bindings.extend(RDK.ItemList(robolink.ITEM_TYPE_ROBOT))
    bindings.extend(RDK.ItemList(robolink.ITEM_TYPE_FRAME))
    bindings.extend(RDK.ItemList(robolink.ITEM_TYPE_TOOL))
    bindings.extend(RDK.ItemList(robolink.ITEM_TYPE_OBJECT))

    for binding in bindings:
        suid = binding.getParam("SUID")
        if suid and int.from_bytes(suid, 'little') == index:
            return binding

    return None


def runmain():
    if roboapps.Unchecked():
        return
    else:
        roboapps.SkipKill()

    current_folder = Path(__file__).absolute().parent
    sound_folder = current_folder / "sounds"
    if not sound_folder.exists() or not sound_folder.is_dir():
        sound_folder = current_folder.parent / "sounds"

    RDK = robolink.Robolink()
    APP = roboapps.RunApplication()

    mixer.init(channels = 2)

    # Request pipe: [
    #   (str) Command,
    #   (str) Path to Sound File,
    #   (int) Item Pointer
    #   (int) Repeat,
    #   (float) Left Volume,
    #    (float) Right Volume
    # ]
    # Available commands: Play Status Stop StopAll
    request = shared_memory.ShareableList([" " * 20, " " * 260, 0, 0, 0.0, 0.0], name = "rdk_sound_request")

    # Response pipe: [(str) Response, (str) Path to sound file]
    # Possible responses: Playing Finished Error
    response = shared_memory.ShareableList([" " * 20, " " * 260], name = "rdk_sound_response")

    playlist = {}

    while APP.Run():
        command = request[0]
        if not command:
            for entry in playlist.values():
                if entry[2]:
                    adjust_channel_volume(RDK, entry[1], entry[2])
            time.wait(50)
            continue

        filename = request[1]
        index = request[2]
        repeat = request[3]
        left_volume = request[4]
        right_volume = request[5]

        request[0] = ""
        response[1] = filename

        if command == "Play":
            # Is this file playing already? Stop it then
            if filename in playlist:
                (sound, channel, item) = playlist[filename]
                channel.stop()
                playlist.pop(filename)

            file_path = Path(filename)
            if not file_path.is_absolute():
                file_path = sound_folder / file_path

            try:
                sound = mixer.Sound(file_path)
                channel = sound.play(loops = repeat)
            except TypeError:
                sound = None
                channel = None
            if sound and channel:
                item = search_item(RDK, index)
                if item:
                    adjust_channel_volume(RDK, channel, item)
                else:
                    channel.set_volume(left_volume, right_volume)
                playlist[filename] = (sound, channel, item)
                response[0] = "Playing"
            else:
                response[0] = "Error"

        elif command == "Status":
            if filename in playlist:
                (sound, channel, item) = playlist[filename]
                if channel.get_busy() and channel.get_sound() == sound:
                    response[0] = "Playing"
                else:
                    playlist.pop(filename)
                    response[0] = "Finished"
            else:
                response[0] = "Error"

        elif command == "Stop":
            if filename in playlist:
                (sound, channel, item) = playlist[filename]
                channel.stop()
                playlist.pop(filename)
                response[0] = "Finished"
            else:
                response[0] = "Error"

        elif command == "StopAll":
            for (sound, channel, item) in playlist.values():
                channel.stop()
            playlist.clear()
            response[1] = ""
            response[0] = "Finished"

    mixer.quit()

if __name__ == "__main__":
    runmain()
