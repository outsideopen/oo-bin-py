from xdg import BaseDirectory
import os
import json
from pathlib import Path

from subprocess import PIPE, DEVNULL, Popen
from oo_bin.errors import InvalidProfileError


class TunnelState:
    def __init__(self, profile, state=None, state_file=None):
        if not profile:
            raise InvalidProfileError("No profile name given")
        if state_file:
            self.__state_file__ = Path(state_file)
        else:
            self.__state_file__ = Path(
                os.path.join(BaseDirectory.save_data_path("oo_bin"), f"{profile}.json")
            )

        if not state:
            try:
                with open(self.__state_file__, "r") as f:
                    self.__state__ = json.load(f)
                    self.name = profile
            except FileNotFoundError:
                self.__state__ = {"profile": profile}

        else:
            self.__state__ = state
            self.name = profile

    def delete(self):
        self.__state_file__.unlink(missing_ok=True)

    def stop(self):
        if self.pid:
            Popen(["kill", str(self.pid)], stdout=DEVNULL)

        self.delete()

    def is_running(self):
        if self.pid:
            ps_output = Popen(
                ["ps", "-f", "-p", str(self.pid)], stdout=PIPE
            ).communicate()

            ps_utf8 = ps_output[0].decode("utf-8") if len(ps_output[0]) > 0 else ""

            return True if len(ps_utf8.split("\n")) > 2 else False
        else:
            return False

    def __save__(self):
        with open(self.__state_file__, "w") as f:
            json.dump(self.__state__, f)

    @property
    def name(self):
        return self.__state__["profile"]

    @name.setter
    def name(self, value):
        self.__state__["profile"] = value
        self.__save__()

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

    def __repr__(self):
        return str(self.__state__)
