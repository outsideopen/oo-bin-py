import os
import pickle
import sys
from pathlib import Path

import tabulate as t
from colorama import Fore, Style
from singleton_decorator import singleton
from xdg import BaseDirectory

from oo_bin.config import main_config
from oo_bin.errors import BrowserProfileUnavailableError
from oo_bin.tunnels.browser_profile import BrowserProfile
from oo_bin.tunnels.socks import Socks


@singleton
class TunnelManager:
    def __init__(self, state_directory=None):
        state_directory = (
            state_directory
            if state_directory
            else Path(BaseDirectory.save_data_path("oo_bin"))
        )
        self.__tunnels = self.__load_tunnels(state_directory)

    def __load_tunnels(self, state_directory):
        tunnels = []
        for data_path in sorted(state_directory.glob("*.pkl"), key=os.path.getmtime):
            with open(data_path, "rb") as f:
                tunnel = pickle.load(f)

                if tunnel.is_running():
                    tunnels.append(tunnel)
                else:
                    tunnel.stop()

        return tunnels

    def add(self, tunnel):
        if isinstance(tunnel, Socks):
            (next_profile_name, next_profile_path) = self.next_browser_profile()
            tunnel.browser_profile_name = next_profile_name
            tunnel.browser_profile_path = next_profile_path
            tunnel.save()

        self.__tunnels.append(tunnel)
        return tunnel

    def tunnel(self, profile):
        tunnels = [x for x in self.__tunnels if x.name == profile]

        return tunnels[0] if len(tunnels) > 0 else None

    def tunnels(self, type=None):
        if type:
            return [x for x in self.__tunnels if isinstance(x, type)]
        else:
            return [x for x in self.__tunnels]

    def print_table(self, tunnels, no_data_msg="No tunnels running!"):
        headers = [
            "Profile",
            "Type",
            "Jump Host",
            "PID",
            "Forward Port",
            "Browser Profile",
        ]

        table = []

        for tunnel in tunnels:
            if tunnel.pid:
                el = []
                el.append(tunnel.name)
                el.append(type(tunnel).__name__)
                el.append(tunnel.jump_host)
                el.append(tunnel.pid)
                el.append(tunnel.forward_port) if isinstance(
                    tunnel, Socks
                ) else el.append(tunnel.local_port)
                el.append(tunnel.browser_profile_name) if isinstance(
                    tunnel, Socks
                ) else el.append("N/A")
                table.append(el)

        if table:
            print(t.tabulate(table, headers, tablefmt="grid"))
        else:
            print(f"\n{Style.BRIGHT}{no_data_msg}")

    def status(self, type=None):
        self.print_table(self.tunnels(type))

    def stop_all(self, type=None):
        if type:
            self.stop([x.name for x in self.__tunnels if isinstance(x, type)])
        else:
            self.stop([x.name for x in self.__tunnels])

    def stop(self, profiles):
        tunnels = []
        stopped = []
        for profile in profiles:
            tunnels.append(self.tunnel(profile))

        for tunnel in tunnels:
            try:
                tunnel.stop()
                stopped.append(tunnel)

            except FileNotFoundError:
                print(f"{Fore.YELLOW}autossh is not running", file=sys.stderr)

        if len(tunnels) > 0:
            print(f"{Style.BRIGHT}The following processes were stopped")
            self.print_table(stopped)
        else:
            print(f"{Style.BRIGHT}No processes were stopped")

    def next_browser_profile(self):
        multiple_profiles = (
            main_config().get("tunnels", {}).get("socks", {}).get("multiple", False)
        )

        if multiple_profiles:
            profiles_dir = Path(
                os.path.join(BaseDirectory.save_data_path("oo_bin"), "profiles")
            )

            all_profiles = [str(x) for x in profiles_dir.glob("*")]
        else:
            profiles_dir = BrowserProfile.primary_profile_path()
            all_profiles = [str(x) for x in profiles_dir.glob("*.Tunnels")]

        running_profiles = [
            x.browser_profile_path for x in self.__tunnels if isinstance(x, Socks)
        ]

        available_profiles = list(set(all_profiles) - set(running_profiles))

        if len(available_profiles) == 0:
            if multiple_profiles:
                error_message = """No Browser Profile is available.

    You can create a new profile by running:      `oo tunnels profile new`
    You can clone an existing profile by running: `oo tunnels profile clone <ProfileName>`"""
            else:
                error_message = "A Socks tunnel is already running. If you want to run multiple tunnels, you can enable it in the configuration."

            raise BrowserProfileUnavailableError(error_message)

        return (os.path.basename(available_profiles[0]), str(available_profiles[0]))
