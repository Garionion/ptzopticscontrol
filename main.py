import signal
import threading
from xbox360controller import Xbox360Controller
import datetime
import time
import requests

ip = "192.168.1.113"
standbyIP = "192.168.1.110"


zoomspeed = 5

class Axis:
    x = 0
    y = 0


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

    pan = int(abs(axis.x) * 24)
    tilt = int(abs(axis.y) * 20)


    if 0.1 > axis.x > -0.1 and 0.1 > axis.y > -0.1:
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

axis = Axis()
lastUrl = ""

if __name__ == '__main__':
    #pt = threading.Thread(target=panTilt)
    #pt.start()
    try:
        with Xbox360Controller(0, axis_threshold=0) as controller:

            # Button A events
            controller.button_trigger_l.when_pressed = zoomout
            controller.button_trigger_r.when_pressed = zoomin
            controller.button_trigger_l.when_released = zoomstop
            controller.button_trigger_r.when_released = zoomstop

            controller.button_start.when_pressed = switchIP

            # Left and right axis move event
            #controller.axis_l.when_moved = on_axis_moved
            #controller.axis_r.when_moved = on_axis_moved
            while True:

                axis.x = controller.axis_l.x
                axis.y = controller.axis_l.y
                panTilt(axis)
                time.sleep(0.1)
            signal.pause()
    except KeyboardInterrupt:
        pass
