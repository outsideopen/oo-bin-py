import os
import pickle
import shutil
import socket
import time
from abc import ABC
from pathlib import Path
from subprocess import DEVNULL, PIPE, Popen

from progress.bar import IncrementalBar
from xdg import BaseDirectory

from oo_bin.config import main_config, ssh_config_path, tunnels_config
from oo_bin.errors import (
    DependencyNotMetError,
    ProcessFailedError,
    TunnelAlreadyStartedError,
)


class Tunnel(ABC):
    def __init__(self, name):
        self.__name = name
        self.__pid = None

        self._config = tunnels_config(profile=self.name)

        self.__jump_host = self._config.get("jump_host") or None

        self._cache_file = os.path.join(
            BaseDirectory.save_cache_path("oo_bin"), "tunnels.log"
        )
        # Clear logfile... we only save errors for the current session
        open(self._cache_file, "w").close()

        self._autossh_bin = "autossh" if shutil.which("autossh") else None

        self._ssh_config = (
            main_config().get("tunnels", {}).get("ssh_config", ssh_config_path)
        )

        self.__pickle_file = Path(
            os.path.join(BaseDirectory.save_data_path("oo_bin"), f"{self.name}.pkl")
        )

    @property
    def name(self):
        return self.__name

    @property
    def pid(self):
        return self.__pid

    @pid.setter
    def pid(self, value):
        self.__pid = value
        # self._save()

    @property
    def jump_host(self):
        return self.__jump_host

    @jump_host.setter
    def jump_host(self, value):
        self.__jump_host = value
        # self._save()

    def save(self, file=None):
        pickle_file = file if file else self.__pickle_file
        with open(pickle_file, "wb") as f:
            pickle.dump(self, f)

    def is_running(self, pid=None):
        if not pid:
            pid = self.pid

        if not pid:
            return False

        ps_output = Popen(["ps", "-f", "-p", str(pid)], stdout=PIPE).communicate()

        ps_utf8 = ps_output[0].decode("utf-8") if len(ps_output[0]) > 0 else ""

        return True if len(ps_utf8.split("\n")) > 2 else False

    def start(self):
        if self.is_running():
            raise TunnelAlreadyStartedError(
                f"Tunnel for profile {self.name} already running!"
            )

        with open(self._cache_file, "a") as f:
            process = Popen(self._cmd, stdout=DEVNULL, stderr=f)
            self.pid = process.pid
            self.save()

            bar = IncrementalBar(
                f"Starting {self.name}", max=20, suffix="%(percent)d%%"
            )
            for i in range(0, 20):
                time.sleep(0.15)
                bar.next()
                if process.poll():
                    print("")
                    msg = f"autossh failed after {(i * 0.15):.2g}s.\
You can view the logs at {self._cache_file}"

                    raise ProcessFailedError(msg)
            bar.finish()

    def stop(self):
        if self.is_running():
            Popen(["kill", str(self.pid)], stdout=DEVNULL)

        self.__pickle_file.unlink(missing_ok=True)

    def runtime_dependencies_met(self):
        if not self._autossh_bin:
            raise DependencyNotMetError(
                "autossh is not installed, or is not in the path"
            )

    def open_port(self):
        sock = socket.socket()
        sock.bind(("", 0))
        return sock.getsockname()[1]
