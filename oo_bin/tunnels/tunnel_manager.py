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

    def status(self):
        headers = [
            "Profile",
            "Jump Host",
            "Forward Port",
            # "Type",
            "PID",
            # "Browser Profile",
        ]

        table = []

        for tunnel in self.tunnels():
            if tunnel.pid:
                table.append(
                    [
                        tunnel.name,
                        tunnel.jump_host,
                        tunnel.forward_port,
                        tunnel.pid,
                        # tunnel.state.browser_profile_name,
                    ]
                )

        if table:
            print(t.tabulate(table, headers, tablefmt="grid"))
        else:
            print(f"\n{Style.BRIGHT}No tunnels running!")

    def stop_all(self):
        self.stop([x.name for x in self.__tunnels])

    def stop(self, profiles):
        headers = ["Profile", "Jump Host", "PID", "Browser Profile"]
        table = []

        tunnels = []
        for profile in profiles:
            tunnels.append(self.tunnel(profile))

        for tunnel in tunnels:
            try:
                tunnel.stop()
                table.append(
                    [
                        tunnel.name,
                        tunnel.jump_host,
                        # tunnel.state.type,
                        tunnel.pid,
                        # tunnel.state.browser_profile_name,
                    ]
                )

            except FileNotFoundError:
                print(f"{Fore.YELLOW}autossh is not running", file=sys.stderr)

        if len(tunnels) > 0:
            print(f"{Style.BRIGHT}The following processes were stopped")
            print(t.tabulate(table, headers, tablefmt="grid"))
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

        running_profiles = [x.browser_profile_path for x in self.__tunnels]

        available_profiles = list(set(all_profiles) - set(running_profiles))

        if len(available_profiles) == 0:
            raise BrowserProfileUnavailableError(
                """No Browser Profile is available.

You can create a new profile by running:      `oo tunnels profile new`
You can clone an existing profile by running: `oo tunnels profile clone <ProfileName>`"""
            )

        return (os.path.basename(available_profiles[0]), str(available_profiles[0]))
