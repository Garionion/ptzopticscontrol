import requests
import logging

logging.basicConfig(level=logging.INFO)


class Camera:
    defaults = dict(
        pan_speed=10,
        tilt_speed=10,
        zoom_speed=5
    )

    def __init__(self, ip: str, defaults: dict = dict()):
        self.ip = ip
        self.defaults = {**self.defaults, **defaults}
        self.last_url = ''

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

    def move(self, pan_speed: int, tilt_speed: int):
        action = ''
        if pan_speed:
            action += 'left' if pan_speed < 0 else 'right'
            pan_speed = abs(pan_speed)

        if tilt_speed:
            action += 'down' if tilt_speed < 0 else 'up'
            tilt_speed = abs(tilt_speed)

        if not action:
            action = 'ptzstop'

        return self._action(action, pan_speed=pan_speed, tilt_speed=tilt_speed)


if __name__ == "__main__":
    cam = Camera('')
    cam.ptzstop()
