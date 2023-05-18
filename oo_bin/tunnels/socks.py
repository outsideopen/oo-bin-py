import os
import shutil
import time
from pathlib import Path
from subprocess import DEVNULL, Popen

from colorama import Fore
from progress.bar import IncrementalBar
from xdg import BaseDirectory

from oo_bin.config import socks_config
from oo_bin.errors import (
    ConfigNotFoundError,
    DependencyNotMetError,
    ProcessFailedError,
    SystemNotSupportedError,
)
from oo_bin.tunnels.browser_profile import BrowserProfile
from oo_bin.tunnels.tunnel import Tunnel
from oo_bin.tunnels.tunnel_type import TunnelType
from oo_bin.utils import is_linux, is_mac, is_wsl, update_tunnels_config


class Socks(Tunnel):
    def __init__(self, profile=None):
        super().__init__(profile)

        self.forward_port = self.open_port()

        self.__browser_bin__ = self.__browser_bin__()

        if profile:
            self.__browser_profile__ = BrowserProfile(
                proxy_host=self.config["forward_host"],
                proxy_port=self.config["forward_port"],
            )

        data_path = BaseDirectory.save_data_path("oo_bin")
        self.__pid_file__ = os.path.join(
            data_path, f"{self.profile}_{TunnelType.SOCKS.value}_autossh_pid"
        )

        self.__firefox_pid_file__ = os.path.join(
            data_path, f"{self.profile}_firefox_pid"
        )

    @property
    def config(self):
        config = socks_config()

        section = config.get(self.profile, {})

        if not section:
            raise ConfigNotFoundError(
                f"{self.profile} could not be found in your configuration file"
            )

        return {
            "jump_host": section.get("jump_host", None),
            "forward_host": section.get("forward_host", "127.0.0.1"),
            "forward_port": section.get("forward_port", self.forward_port),
            "urls": section.get("urls", None),
        }

    def __browser_bin__(self):
        if is_wsl():
            return shutil.which(
                "firefox.exe",
                path="/mnt/c/Program Files/Mozilla Firefox:/mnt/c/Program Files (x86)/Mozilla Firefox",
            )

        elif is_linux():
            return shutil.which("firefox")
        elif is_mac():
            bin = shutil.which("firefox")
            return (
                bin
                if bin
                else shutil.which(
                    "firefox", path="/Applications/Firefox.app/Contents/MacOS"
                )
            )
        SystemNotSupportedError("Your system is not supported")

    def stop(self):
        super().stop(self.profile)

        if not is_wsl():
            self.__kill_browser__(self.profile)

    def start(self):
        super().start()

        cmd = [
            self.__autossh_bin__,
            "-N",
            "-M",
            "0",
            "-D",
            f"{self.config['forward_port']}",
            "-o",
            "ServerAliveInterval=3",
            "-o",
            "ServerAliveCountMax=30",
            "-F",
            f"{self.__ssh_config__}",
            f"{self.config['jump_host']}",
        ]
        with open(self.__cache_file__, "a") as f1:
            process = Popen(cmd, stdout=DEVNULL, stderr=f1)
            pid = process.pid

            with open(self.__pid_file__, "w") as f2:
                f2.write(f"{pid}")

            bar = IncrementalBar(
                f"Starting {self.profile}", max=20, suffix="%(percent)d%%"
            )
            for i in range(0, 20):
                time.sleep(0.1)
                bar.next()
                if process.poll():
                    print("")
                    msg = f"autossh failed after {(i * 0.1):.2g}s.\
You can view the logs at {self.__cache_file__}"

                    raise ProcessFailedError(msg)
            bar.finish()

        urls = self.config["urls"]
        if urls:
            self.__launch_browser__(urls)
            print(f"Launching Firefox with tabs: {', '.join(urls)}")
        else:
            print(
                Fore.YELLOW
                + "The tunnel has been started, but you have no urls configured"
            )

    def __launch_browser__(self, urls):
        cmd = [
            self.__browser_bin__,
            "--profile",
            self.__browser_profile__.normalized_path,
        ] + urls

        with open(self.__cache_file__, "a") as f1:
            pid = Popen(cmd, stdout=DEVNULL, stderr=f1).pid

            with open(self.__firefox_pid_file__, "w") as f2:
                f2.write(f"{pid}\n{self.__browser_profile__.path}")

    def __kill_browser__(self, profile=None):
        data_path = BaseDirectory.save_data_path("oo_bin")

        pid_files = []

        if profile:
            pid_files = [os.path.join(data_path, f"{profile}_firefox_pid")]
        else:
            pid_files = Path(data_path).glob("*_firefox_pid")

        try:
            for pid_file in pid_files:
                with open(pid_file, "r") as f1:
                    file_content = f1.read().split("\n", 2)
                    pid = file_content[0] if len(file_content) > 0 else None
                    profile_path = file_content[0] if len(file_content) > 1 else None
                    profile = BrowserProfile(profile_path=profile_path, clone=False)

                    with open(self.__cache_file__, "a") as f2:
                        Popen(["kill", "-9", pid], stdout=DEVNULL, stderr=f2)
                    os.remove(pid_file)
                    profile.destroy()

        except FileNotFoundError:
            return False

        return True

    def runtime_dependencies_met(self):
        if not self.__autossh_bin__:
            raise DependencyNotMetError(
                "autossh is not installed, or is not in the path"
            )

        if not self.__browser_bin__:
            raise DependencyNotMetError(
                "firefox is not installed, or is not in the path"
            )

    def run(self, args):
        if args["update"]:
            update_tunnels_config()
        else:
            self.start()
