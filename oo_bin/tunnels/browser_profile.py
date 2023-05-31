import getpass
from itertools import islice
from os import environ
from pathlib import Path
from shutil import ignore_patterns
from subprocess import DEVNULL, Popen

import mozfile
import wslPath
from mozprofile.profile import FirefoxProfile

from oo_bin.utils import is_linux, is_mac, is_wsl, wsl_user


class BrowserProfile:
    def __init__(self, browser_profile):
        if browser_profile:
            if Path(browser_profile).exists():
                self.profile = FirefoxProfile(profile=browser_profile, restore=True)
            else:
                self.profile = FirefoxProfile(profile=browser_profile, restore=False)
        else:
            self.clone(primary_profile_path=None, profile_path=None)

    def clone(self, primary_profile_path=None, profile_path=None):
        primary_profile_path = (
            primary_profile_path
            if primary_profile_path
            else self.__find_primary_profile_path__()
        )

        self.profile = FirefoxProfile.clone(
            primary_profile_path,
            path_to=profile_path,
            ignore=ignore_patterns(
                "cache2", "lock", "places.sqlite", "startupCache", "storage"
            ),
            restore=False,
        )

    def set_socks_proxy(self, host, port):
        preferences = {
            "network.proxy.socks": host,
            "network.proxy.socks_port": port,
            "network.proxy.socks_remote_dns": True,
            "network.proxy.type": 1,
            "network.trr.blocklist_cleanup_done": True,
            "network.trr.mode": 5,
        }
        self.profile.set_preferences(preferences)

    @property
    def path(self):
        return self.profile.profile

    @property
    def normalized_path(self):
        if is_wsl():
            return wslPath.toWindows(self.path)
        return self.path

    def destroy(self):
        mozfile.remove(self.path)

    def __find_primary_profile_path__(self):
        if is_wsl():
            user = wsl_user()
            profiles = [
                x
                for x in Path(
                    f"/mnt/c/Users/{user}/AppData/Roaming/Mozilla/Firefox/Profiles/"
                ).glob("*.Tunnels")
            ]
            return profiles[0] if len(profiles) > 0 else None

        elif is_linux():
            user = getpass.getuser()
            profiles = [
                x for x in Path(f"/home/{user}/.mozilla/firefox/").glob("*.Tunnels")
            ]
            return profiles[0] if len(profiles) > 0 else None

        elif is_mac():
            user = getpass.getuser()
            profiles = [
                x
                for x in Path(
                    f"/Users/{user}/Library/Application Support/Firefox/Profiles/"
                ).glob("*.Tunnels")
            ]
            return profiles[0] if len(profiles) > 0 else None
