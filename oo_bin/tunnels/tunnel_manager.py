import os
import pickle
import sys
from pathlib import Path
from subprocess import DEVNULL, Popen

import tabulate as t
from colorama import Fore, Style
from singleton_decorator import singleton
from xdg import BaseDirectory

from oo_bin.errors import BrowserProfileUnavailableError
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
            try:
                with open(data_path, "rb") as f:
                    tunnel = pickle.load(f)

                    if tunnel.is_running():
                        tunnels.append(tunnel)
                    else:
                        tunnel.stop()
            except (AttributeError, EOFError, ImportError, IndexError):
                print(f"{Style.BRIGHT}Inconsistent tunnel state detected.\n")
                print(f"Deleting state file: {Style.BRIGHT}{data_path}")
                data_path.unlink(missing_ok=True)

                if tunnel.pid:
                    print(
                        f"Stopping the offending tunnel, with PID: {Style.BRIGHT}{tunnel.pid}"
                    )
                    Popen(["kill", str(tunnel.pid)], stdout=DEVNULL, stderr=DEVNULL)

        return tunnels

    def add(self, tunnel):
        if isinstance(tunnel, Socks):
            if tunnel.multiple_profiles:
                (next_profile_name, next_profile_path) = self.next_browser_profile()
                tunnel.browser_profile_name = next_profile_name
                tunnel.browser_profile_path = next_profile_path

            else:
                if len(self.tunnels(type=Socks)) > 0:
                    raise BrowserProfileUnavailableError(
                        "Socks tunnel already in use. Please stop the existing tunnel before starting a new one."
                    )

                tunnel.browser_profile_name = "Tunnels"
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

    def print_table(self, tunnels, no_data_msg="No tunnels are running!"):
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
                table.append(
                    [
                        tunnel.name,
                        type(tunnel).__name__,
                        tunnel.jump_host,
                        tunnel.pid,
                        (
                            tunnel.forward_port
                            if isinstance(tunnel, Socks)
                            else tunnel.local_port
                        ),
                        (
                            tunnel.browser_profile_name
                            if isinstance(tunnel, Socks)
                            else "N/A"
                        ),
                    ]
                )

        if table:
            print(t.tabulate(table, headers, tablefmt="grid"))
        else:
            print(f"\n{Style.BRIGHT}{no_data_msg}")

    def status(self, type=None):
        self.print_table(self.tunnels(type))

    def stop_all(self, type=None):
        if type:
            self.stop([x for x in self.__tunnels if isinstance(x, type)])
        else:
            self.stop([x for x in self.__tunnels])

    def stop(self, tunnels):
        stopped = []

        for tunnel in tunnels:
            try:
                tunnel.stop()
                stopped.append(tunnel)
                self.__tunnels.remove(tunnel)

            except FileNotFoundError:
                print(f"{Fore.YELLOW}autossh is not running", file=sys.stderr)

        if len(stopped) > 0:
            profile_names = ", ".join([el.name for el in stopped])
            print(
                f"The following tunnels were stopped: {Style.BRIGHT}{profile_names}\n"
            )
        else:
            print(f"{Style.BRIGHT}No tunnels were stopped.\n")

        if len(self.__tunnels) > 0:
            print(f"{Style.BRIGHT}Running Tunnels:")
            self.print_table(self.__tunnels)
        else:
            print(f"{Style.BRIGHT}No tunnels are running.")

    def next_browser_profile(self):
        profiles_dir = Path(
            os.path.join(BaseDirectory.save_data_path("oo_bin"), "profiles")
        )

        all_profiles = [str(x) for x in profiles_dir.glob("*")]

        running_profiles = [
            x.browser_profile_path for x in self.__tunnels if isinstance(x, Socks)
        ]

        available_profiles = list(set(all_profiles) - set(running_profiles))

        if len(available_profiles) == 0:
            if self.multiple_profiles:
                error_message = """No Browser Profile is available.

    You can create a new profile by running:      `oo tunnels profile new`
    You can clone an existing profile by running: `oo tunnels profile clone <ProfileName>`"""
            else:
                error_message = "A Socks tunnel is already running. If you want to run multiple tunnels, you can enable it in the configuration."

            raise BrowserProfileUnavailableError(error_message)

        return (os.path.basename(available_profiles[0]), str(available_profiles[0]))
