import signal
from xbox360controller import Xbox360Controller
import datetime
import time
import requests
from camera import Camera

cam = Camera("192.168.1.113")
secondCam = Camera("192.168.1.110")


zoomspeed = 5
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
    panSpeed = int(axis.x*maxPanSpeed) if abs(axis.x) > 0.19 else 0
    tiltSpeed = int(axis.y*maxTiltSpeed) if abs(axis.y) > 0.19 else 0
    cam.move(panSpeed=panSpeed, tiltSpeed=tiltSpeed)

def zoomin(button):
    cam.zoom("zoomin", zoomspeed=None)


def zoomout(button):
    cam.zoom("zoomout", zoomspeed=None)


def zoomstop(button):
    cam.zoom("zoomstop", zoomspeed=0)

def switchIP(button):
    global cam, secondCam
    controller.set_rumble(1, 1, 80)
    cam, secondCam = secondCam, cam
    
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


def on_button_released(button):
    print('Button {0} was released'.format(button.name))

axis = Axis()
lastUrl = ""


presets = {
    "button_a": Preset(1),
    "button_b": Preset(2),
    "button_x": Preset(3),
    "button_y": Preset(4),
}

if __name__ == '__main__':
    try:
        with Xbox360Controller(0, axis_threshold=0) as controller:

            # Button A events
            controller.button_trigger_l.when_pressed = zoomout
            controller.button_trigger_r.when_pressed = zoomin
            controller.button_trigger_l.when_released = zoomstop
            controller.button_trigger_r.when_released = zoomstop

            controller.button_start.when_pressed = switchIP

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

                axis.x = controller.axis_l.x
                axis.y = controller.axis_l.y
                panTilt(axis)
                time.sleep(0.15)
            signal.pause()
    except KeyboardInterrupt:
        pass
