import math
import os
import platform
import time
import sys
import wmi
def is_hand_centered(palm_x, palm_y, frame_width, frame_height):
    # Calculate box boundaries (arbitrary, subject to change/removal)
    left = 0.35 * frame_width
    right = 0.85 * frame_width
    top = 0.35 * frame_height
    bottom = 0.85 * frame_height

    # Check if palm is inside the box
    return (left <= palm_x <= right) and (top <= palm_y <= bottom)


def set_volume_from_distance(handPos, frame_width, frame_height):
    
    for landmark in handPos:

        land_x, land_y = landmark[0], landmark[1]
   
        if not is_hand_centered(land_x, land_y, frame_width, frame_height):
            print(f"landmark at position {landmark[0]} , {landmark[1]} not centered. Ignoring input.")
            return

    # Tip of index finger (8), tip of thumb (4)
    x1, y1 = handPos[4]
    x2, y2 = handPos[8]

    distance = math.hypot(x2 - x1, y2 - y1) - 65
    max_possible_distance = frame_width // 2  # heuristic numbers based on hand size

    # Clamp to [0, 100]
    volume = min(100, max(0, int((distance / max_possible_distance) * 2.5 * 100)))
    print(f"Setting volume to {volume} (distance: {distance})")

    # Platform-specific volume control
    if platform.system() == "Windows":
        try:
            import pycaw
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL

            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_interface = cast(interface, POINTER(IAudioEndpointVolume))

            min_vol, max_vol = volume_interface.GetVolumeRange()[:2]
            new_vol = min_vol + (volume / 100.0) * (max_vol - min_vol)
            volume_interface.SetMasterVolumeLevel(new_vol, None)

            #sleeps prevent wild fluctuation, we don't want to update hardware setting every frame
            time.sleep(0.10)
        except ImportError:
            print("pycaw not installed. Install with `pip install pycaw`")
    else:
        print("Volume control not implemented for this OS.")

def set_brightness_from_distance(handPos, frame_width, frame_height):
    # distance between thumb tip and middle finger finger tip
    thumb_tip = handPos[4]
    middle_tip = handPos[12]
    
    dx = abs(thumb_tip[0] - middle_tip[0])
    dy = abs(thumb_tip[1] - middle_tip[1])
    distance = (dx**2 + dy**2)**0.5 - 65

    max_possible_distance = frame_width // 2  # heuristic

    
    brightness = min(100, max(0, int((distance / max_possible_distance) * 3 * 100)))


    try:
        wmi_interface = wmi.WMI(namespace='wmi')
        methods = wmi_interface.WmiMonitorBrightnessMethods()[0]
        methods.WmiSetBrightness(brightness, 0)
    except Exception as e:
        print(f"Failed to set brightness: {e}")
    #sleeps prevent wild fluctuation, we don't want to update hardware setting every frame
    time.sleep(0.05)

    
def close_application(*args):
    print("Fist detected. Closing application.")
    sys.exit(0)

