import signal
import socket
from xbox360controller import Xbox360Controller
import datetime
import time
import requests

ip = "192.168.1.113"
standbyIP = "192.168.1.110"


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

class Cam:
    actions = dict(
        up="03 01",
        down="03 02",
        left="01 03",
        right="02 03",
        upleft="01 01",
        upright="02 01",
        downleft="01 02",
        downright="02 02",
        stop="03 03",
        zoomin="2",
        zoomout="3",
    )
    
    def __init__(self, ip, port=1259):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    
    def send(self, msg):
        self.sock.sendto(msg, (self.ip, self.port))
        recvMsg = 0
        while True:
            nextBytes = self.sock.recv(50)
            recvMsg = int(nextBytes.hex(), 16)
            if 9461759 >= recvMsg >= 9457919:
                recvMsg = 0
                continue
            elif 9457663 >= recvMsg >= 9453823:
                break
    
    def zoom(self, action, speed):
        act = Cam.actions.get(action, Cam.actions["zoomin"])
        msg = bytearray.fromhex(f"81 01 04 07 {act}{speed} FF")
        self.send(msg)
     
    def move(self, action, panSpeed, tiltSpeed):
        act = Cam.actions.get(action, Cam.actions["stop"])
        msg = bytearray.fromhex(f"81 01 06 01 01 01 {act} FF")
        self.send(msg)
        
    def set_preset(self, preset):
        msg = bytearray.fromhex(f"81 01 04 3F 01 {preset} FF")
        self.send(msg)

    def call_preset(self, preset):
        msg = bytearray.fromhex(f"81 01 04 3F 02 {preset} FF")
        self.send(msg)

def panTilt(axis):
    global lastUrl
    direction = ""
    if axis.x > 0.2:
        direction += "right"
    elif axis.x < -0.2:
        direction += "left"
    if axis.y > 0.2:
        direction += "down"
    elif axis.y < -0.2:
        direction += "up"

    pan = int(abs(axis.x) * maxPanSpeed)
    tilt = int(abs(axis.y) * maxTiltSpeed)


    if 0.19 > axis.x > -0.19 and 0.19 > axis.y > -0.19:
        direction = "ptzstop"

    if direction == "":
        return
    url = f"http://{ip}/cgi-bin/ptzctrl.cgi?ptzcmd&{direction}&{pan}&{tilt}"
    if lastUrl == url:
        return
    lastUrl = url
    r = requests.get(f"http://{ip}/cgi-bin/ptzctrl.cgi?ptzcmd&{direction}&{pan}&{tilt}")
    print(f"{datetime.datetime.now()} - {r.url}")


def zoomin(button):
    r = requests.get(f"http://{ip}/cgi-bin/ptzctrl.cgi?ptzcmd&zoomin&{zoomspeed}")
    print(f"{datetime.datetime.now()} - {r.url}")

def zoomout(button):
    r = requests.get(f"http://{ip}/cgi-bin/ptzctrl.cgi?ptzcmd&zoomout&{zoomspeed}")
    print(f"{datetime.datetime.now()} - {r.url}")


def zoomstop(button):
    r = requests.get(f"http://{ip}/cgi-bin/ptzctrl.cgi?ptzcmd&zoomstop&{zoomspeed}")
    print(f"{datetime.datetime.now()} - {r.url}")

def switchIP(button):
    global ip, standbyIP
    controller.set_rumble(1, 1, 80)
    ip, standbyIP = standbyIP, ip
    
def handlePresetStart(button):
    global presets
    presets[button.name].lastPressed = time.time()

def handlePreset(button):
    if time.time() - presets[button.name].lastPressed > 1:
        action = "posset"
        controller.set_rumble(1, 1, 150)
    else:
        action = "poscall"

    r = requests.get(f"http://{ip}/cgi-bin/ptzctrl.cgi?ptzcmd&{action}&{presets[button.name].position}")
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
    cam = Cam("192.168.1.110")
    cam.move("left", "01", "01")
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
