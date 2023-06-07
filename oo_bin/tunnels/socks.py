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
    def __init__(self, state):
        super().__init__(state)

        self.state.type = TunnelType.SOCKS.value

        self.forward_port = self.open_port()

    @property
    def config(self):
        config = socks_config()

        section = config.get(self.state.name, {})

        if not section:
            raise ConfigNotFoundError(
                f"{self.state.name} could not be found in your configuration file"
            )

        return {
            "jump_host": section.get("jump_host", None),
            "forward_host": section.get("forward_host", "127.0.0.1"),
            "forward_port": section.get("forward_port", self.forward_port),
            "urls": section.get("urls", None),
        }

    @property
    def __browser_bin(self):
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
        Popen(["kill", str(self.state.pid)], stdout=DEVNULL)

        if not is_wsl():
            self.__kill_browser()

        self.state.delete()

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

            self.state.pid = pid
            self.state.jump_host = self.config["jump_host"]
            self.state.forward_port = self.config["forward_port"]

            bar = IncrementalBar(
                f"Starting {self.state.name}", max=20, suffix="%(percent)d%%"
            )
            for i in range(0, 20):
                time.sleep(0.15)
                bar.next()
                if process.poll():
                    print("")
                    msg = f"autossh failed after {(i * 0.15):.2g}s.\
You can view the logs at {self.__cache_file__}"

                    raise ProcessFailedError(msg)
            bar.finish()

        urls = self.config["urls"]
        if urls:
            self.__launch_browser(urls)
            print(f"Launching Firefox with tabs: {', '.join(urls)}")
        else:
            print(
                Fore.YELLOW
                + "The tunnel has been started, but you have no urls configured"
            )

    def __launch_browser(self, urls):
        browser_profile = BrowserProfile(self.state.browser_profile_path)
        browser_profile.set_socks_proxy(
            self.config["forward_host"], self.config["forward_port"]
        )

        cmd = [
            self.__browser_bin,
            "--profile",
            self.state.browser_profile_path,
        ] + urls

        with open(self.__cache_file__, "a") as f1:
            pid = Popen(cmd, stdout=DEVNULL, stderr=f1).pid

            self.state.browser_pid = pid

    def __kill_browser(self):
        with open(self.__cache_file__, "a") as f:
            Popen(["kill", "-9", str(self.state.browser_pid)], stdout=DEVNULL, stderr=f)

        return True

    def runtime_dependencies_met(self):
        if not self.__autossh_bin__:
            raise DependencyNotMetError(
                "autossh is not installed, or is not in the path"
            )

        if not self.__browser_bin:
            raise DependencyNotMetError(
                "firefox is not installed, or is not in the path"
            )

    def run(self, args):
        if args["update"]:
            update_tunnels_config()
        else:
            self.start()
