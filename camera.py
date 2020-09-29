import requests
import logging
import socket

logging.basicConfig(level=logging.INFO)

def toHex(num: int):
    return hex(num)[2:].zfill(2)

class Camera:
    defaults = dict(
        pan_speed=10,
        tilt_speed=10,
        zoom_speed=5
    )

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
        zoomstop="0",
        focusin="2",
        focusout="3",
        focusstop="0",
    )

    def __init__(self, ip: str, port: int = 1259, defaults: dict = dict(), position=0):
        self.ip = ip
        self.defaults = {**self.defaults, **defaults}
        self.last_url = ''
        self.last_message = ''
        self.last_move = ''
        self.last_focus = ''
        self.last_zoom = ''
        self.port = port
        self.position = position
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    def send(self, msg, force=False):
        if msg == self.last_message and not force:
            return
        logging.debug(f"send {msg}")
        self.sock.sendto(msg, (self.ip, self.port))
        while True:
            nextBytes = self.sock.recv(50)
            recvMsg = int(nextBytes.hex(), 16)
            
            if 9461759 >= recvMsg >= 9457919:
                continue
            if 2423210495 >= recvMsg >= 2422211327:
                logging.error(hex(recvMsg))
                break
            elif 9457663 >= recvMsg >= 9453823:
                self.last_message = msg
                break
        logging.info("Send finished")

    def _action(self, action: str, *args, **kwargs):
        url = f"http://{self.ip}//cgi-bin/ptzctrl.cgi?ptzcmd&{action}"
        for arg in args:
            url += f"&{arg}"
        for arg in kwargs.values():
            url += f"&{arg}"

        if self.last_url == url:
            return

        self.last_url = url
        logging.info(url)
        try:
            requests.get(url)
        except Exception:
            logging.error("Request failed")
            logging.error(dict(
                action=action,
                args=args,
                kwargs=kwargs,
                url=url))

    def __getattr__(self, name):
        def cmd(*args, **kwargs):
            for k, v in kwargs.items():
                if v is None:
                    kwargs[k] = self.defaults.get(k)

            self._action(name, *args, **kwargs)

        return cmd

    def move(self, panSpeed: int, tiltSpeed: int):
        action = ''

        if tiltSpeed:
            action += 'down' if tiltSpeed > 0 else 'up'
            tiltSpeed = abs(tiltSpeed)

        if panSpeed:
            action += 'left' if panSpeed < 0 else 'right'
            panSpeed = abs(panSpeed)

        if not action:
            action = 'ptzstop'

        act = Camera.actions.get(action, Camera.actions["stop"])
        msg = bytearray.fromhex(f"81 01 06 01 {toHex(panSpeed)} {toHex(tiltSpeed)} {act} FF")
        if msg == self.last_move:
            return
        self.last_move = msg
        return self.send(msg)
    
    def focus(self, focusSpeed):
        action = ''

        if focusSpeed:
            action = 'focusin' if focusSpeed > 0 else 'focusout'
            focusSpeed = abs(focusSpeed)

        if not action:
            action = 'focusstop'

        act = Camera.actions.get(action, Camera.actions.get(action, Camera.actions["focusstop"]))

        msg = bytearray.fromhex(f"81 01 04 08 {act}{focusSpeed} FF")
        if msg == self.last_focus:
            return
        print(f"focus {action} - {focusSpeed}")
        self.last_focus = msg
        self.send(msg)
    
    def zoom(self, zoomSpeed):
        action = ''

        if zoomSpeed:
            action = 'zoomin' if zoomSpeed < 0 else 'zoomout'
            zoomSpeed = abs(zoomSpeed)

        if not action:
            action = 'zoomstop'

        act = Camera.actions.get(action, Camera.actions.get(action, Camera.actions["zoomstop"]))

        msg = bytearray.fromhex(f"81 01 04 07 {act}{zoomSpeed} FF")
        if msg == self.last_zoom:
            return 
        self.last_zoom = msg
        print(f"focus {action} - {zoomSpeed}")
        return self.send(msg)

    def set_preset(self, preset: int):
        msg = bytearray.fromhex(f"81 01 04 3F 01 {toHex(preset)} FF")
        self.send(msg)

    def call_preset(self, preset: int):
        msg = bytearray.fromhex(f"81 01 04 3F 02 {toHex(preset)} FF")
        self.send(msg)
    
    def toggleAF(self):
        msg = bytearray.fromhex("81 01 04 38 10 FF")
        self.send(msg, force=True)


if __name__ == "__main__":
    cam = Camera('')
    cam.move(0,0)
