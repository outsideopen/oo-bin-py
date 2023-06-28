import shutil
from subprocess import DEVNULL, Popen

from colorama import Fore

from oo_bin.errors import DependencyNotMetError, SystemNotSupportedError
from oo_bin.tunnels.browser_profile import BrowserProfile
from oo_bin.tunnels.tunnel import Tunnel
from oo_bin.utils import is_linux, is_mac, is_wsl, port_available


class Socks(Tunnel):
    def __init__(self, name):
        super().__init__(name)

        self.__forward_port = self.open_port()
        self.__browser_profile_name = None
        self.__browser_profile_path = None
        self.__browser_pid = None

        config_port = self._config.get("forward_port", None)
        self.__forward_port = (
            config_port
            if config_port and port_available(int(config_port), self.forward_host)
            else self.open_port()
        )

    @property
    def forward_host(self):
        return self._config.get("forward_host") or "127.0.0.1"

    @property
    def forward_port(self):
        return self.__forward_port

    @property
    def urls(self):
        return self._config.get("urls") or None

    @property
    def browser_profile_name(self):
        return self.__browser_profile_name

    @browser_profile_name.setter
    def browser_profile_name(self, value):
        self.__browser_profile_name = value
        # self._save()

    @property
    def browser_profile_path(self):
        return self.__browser_profile_path

    @browser_profile_path.setter
    def browser_profile_path(self, value):
        self.__browser_profile_path = value
        # self._save()

    @property
    def browser_pid(self):
        return self.__browser_pid

    @browser_pid.setter
    def browser_pid(self, value):
        self.__browser_pid = value
        # self._save()

    # @property
    # def config(self):
    #     config = tunnels_config()

    #     section = config.get(self.name, {})

    #     if not section:
    #         raise ConfigNotFoundError(
    #             f"{self.name} could not be found in your configuration file"
    #         )

    #     return {
    #         "jump_host": section.get("jump_host", None),
    #         "forward_host": section.get("forward_host", "127.0.0.1"),
    #         "forward_port": section.get("forward_port", self.forward_port),
    #         "urls": section.get("urls", None),
    #     }

    @property
    def _cmd(self):
        return [
            self._autossh_bin,
            "-N",
            "-M",
            "0",
            "-D",
            f"{self.forward_port}",
            "-o",
            "ServerAliveInterval=3",
            "-o",
            "ServerAliveCountMax=30",
            "-F",
            f"{self._ssh_config}",
            f"{self.jump_host}",
        ]

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
        super().stop()

        if not is_wsl() and self.is_running(self.browser_pid):
            self.__kill_browser()

    def start(self):
        super().start()

        if self.urls:
            self.__launch_browser(self.urls)
            print(f"Launching Firefox with tabs: {', '.join(self.urls)}")
        else:
            print(
                Fore.YELLOW
                + "The tunnel has been started, but you have no urls configured"
            )

    def __launch_browser(self, urls):
        browser_profile = BrowserProfile(self.browser_profile_path)
        browser_profile.set_socks_proxy(self.forward_host, self.forward_port)

        cmd = [
            self.__browser_bin,
            "--profile",
            self.browser_profile_path,
        ] + urls

        with open(self._cache_file, "a") as f1:
            pid = Popen(cmd, stdout=DEVNULL, stderr=f1).pid

            self.browser_pid = pid
            self.save()

    def __kill_browser(self):
        with open(self._cache_file, "a") as f:
            Popen(["kill", "-9", str(self.browser_pid)], stdout=DEVNULL, stderr=f)

        return True

    def runtime_dependencies_met(self):
        super().runtime_dependencies_met()

        if not self.__browser_bin:
            raise DependencyNotMetError(
                "firefox is not installed, or is not in the path"
            )
