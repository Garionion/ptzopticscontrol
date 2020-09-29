import signal
from xbox360controller import Xbox360Controller
import threading
import datetime
import time
import string
from camera import Camera
import difflib
from enum import Enum

class CamPosition(Enum):
    right = 1
    left = 2


cam = Camera(ip="192.168.1.113", position=CamPosition.left)
secondCam = Camera(ip="192.168.1.110", position=CamPosition.right)

maxZoomSpeed = 7
maxFocusSpeed= 3
maxPanSpeed = 10
maxTiltSpeed = 10

class Axis:
    x = 0
    y = 0

class Preset:
    position = 0
    lastPressed = time.time()
    
    def __init__(self, pos):
        self.position = pos

def panTilt(axis: Axis):
    panSpeed = int(axis.x * maxPanSpeed) if abs(axis.x) > 0.19 else 0
    tiltSpeed = int(axis.y * maxTiltSpeed) if abs(axis.y) > 0.19 else 0
    cam.move(panSpeed=panSpeed, tiltSpeed=tiltSpeed)
    time.sleep(0.15)

def focus(focus):
    focusspeed = int(focus * maxFocusSpeed) if abs(focus) > 0.19 else 0
    cam.focus(focusSpeed=focusspeed)

def zoom(zoom):
    zoomspeed = int(zoom * maxZoomSpeed) if abs(zoom) > 0.19 else 0
    cam.zoom(zoomSpeed=zoomspeed)

def zoomin(button):
    cam.zoom(zoomSpeed=cam.defaults["zoom_speed"])

def zoomout(button):
    cam.zoom(zoomSpeed=cam.defaults["zoom_speed"])

def zoomstop(button):
    cam.zoom(zoomSpeed=cam.defaults["zoom_speed"])

def switchCam(button):
    global cam, secondCam
    cam, secondCam = secondCam, cam
    if cam.position == CamPosition.right:
        controller.set_rumble(0, 1, 200)
    else:
        controller.set_rumble(1, 0, 200)

def toggleAF(button):
    cam.toggleAF()
    controller.set_rumble(1, 0, 120)
    time.sleep(0.2)
    controller.set_rumble(0, 1, 120)
    
def handlePresetStart(button):
    global presets
    presets[button.name].lastPressed = time.time()


def handlePreset(button):
    preset = presets[button.name].position

    if time.time() - presets[button.name].lastPressed > 0.4:
        controller.set_rumble(1, 1, 150)
        cam.set_preset(preset)
    else:
        cam.call_preset(preset)



axis = Axis()
lastUrl = ""


def on_axis_moved(axis):
    print('Axis {0} moved to {1} {2}'.format(axis.name, axis.x, axis.y))

presets = {
    "button_a": Preset(1),
    "button_b": Preset(2),
    "button_x": Preset(3),
    "button_y": Preset(4),
}

if __name__ == '__main__':
    try:
        name = ''.join([x if x in string.printable else '' for x in Xbox360Controller.get_available()[0].name])
        if name == "Logitech Logitech RumblePad 2 USB":
            switchAxisR = True
        else:
            switchAxisR = False
        print(switchAxisR)
        with Xbox360Controller(0, axis_threshold=0, switch_axis_r_with_trigger_l=switchAxisR) as controller:
            # Button A events
            controller.button_trigger_l.when_pressed = zoomout
            controller.button_trigger_r.when_pressed = zoomin
            controller.button_trigger_l.when_released = zoomstop
            controller.button_trigger_r.when_released = zoomstop

            controller.button_start.when_pressed = switchCam
            controller.button_select.when_pressed = toggleAF

            controller.button_a.when_pressed = handlePresetStart
            controller.button_b.when_pressed = handlePresetStart
            controller.button_x.when_pressed = handlePresetStart
            controller.button_y.when_pressed = handlePresetStart

            controller.button_a.when_released = handlePreset
            controller.button_b.when_released = handlePreset
            controller.button_x.when_released = handlePreset
            controller.button_y.when_released = handlePreset

            # Left and right axis move event
            #controller.axis_l.when_moved = on_axis_moved
            #controller.axis_r.when_moved = on_axis_moved

            while True:
                focusValue = controller.axis_r.x
                zoomValue = controller.axis_r.y

                axis.x = controller.axis_l.x
                axis.y = controller.axis_l.y
                panTilt(axis)
                focusValue = controller.axis_r.x
                zoomValue = controller.axis_r.y

                focus(focusValue)
                zoom(zoomValue)
                time.sleep(0.1)
            signal.pause()
    except KeyboardInterrupt:
        pass
