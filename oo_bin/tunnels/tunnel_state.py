from xdg import BaseDirectory
import os
import json
from pathlib import Path


class TunnelState:
    def __init__(self, profile, state=None, state_file=None):
        self.__profile__ = profile

        if state_file:
            self.__state_file__ = Path(state_file)
        else:
            self.__state_file__ = Path(
                os.path.join(BaseDirectory.save_data_path("oo_bin"), f"{profile}.json")
            )

        if not state:
            with open(self.__state_file__, "r") as f:
                self.__state__ = json.load(f)

        else:
            self.__state__ = state
            self.__save__()

    def delete(self):
        self.__state_file__.unlink(missing_ok=True)

    def __save__(self):
        with open(self.__state_file__, "w") as f:
            json.dump(self.__state__, f)

    @property
    def name(self):
        return self.__profile__

    @property
    def pid(self):
        return self.__state__.get("pid", None)

    @pid.setter
    def pid(self, value):
        self.__state__["pid"] = value
        self.__save__()

    @property
    def type(self):
        return self.__state__.get("type", None)

    @type.setter
    def type(self, tunnel_type):
        self.__state__["type"] = tunnel_type
        self.__save__()

    @property
    def jump_host(self):
        return self.__state__.get("jump_host", None)

    @jump_host.setter
    def jump_host(self, value):
        self.__state__["jump_host"] = value
        self.__save__()

    @property
    def browser_profile(self):
        return self.__state__.get("browser_profile", None)

    @browser_profile.setter
    def browser_profile(self, value):
        self.__state__["browser_profile"] = value
        self.__save__()

    @property
    def browser_pid(self):
        return self.__state__.get("browser_pid", None)

    @browser_pid.setter
    def browser_pid(self, value):
        self.__state__["browser_pid"] = value
        self.__save__()
