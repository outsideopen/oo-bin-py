import getpass
from pathlib import Path
from shutil import ignore_patterns

import mozfile
import wslPath
from mozprofile.profile import FirefoxProfile

from oo_bin.utils import is_linux, is_mac, is_wsl, wsl_user
import os


class BrowserProfile:
    def __init__(self, browser_profile):
        if Path(browser_profile).exists():
            self.profile = FirefoxProfile(profile=browser_profile, restore=True)
        else:
            self.profile = FirefoxProfile(profile=browser_profile, restore=False)

    def set_socks_proxy(self, host, port):
        with open(os.path.join(self.path, "user.js"), "w") as f:
            f.write(f'user_pref("network.proxy.socks", "{host}");\n')
            f.write(f'user_pref("network.proxy.socks_port", {port});\n')
            f.write('user_pref("network.proxy.socks_remote_dns", true);\n')
            f.write('user_pref("network.proxy.type", 1);\n')
            f.write('user_pref("network.trr.blocklist_cleanup_done", true);\n')
            f.write('user_pref("network.trr.mode", 5);')

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

    @staticmethod
    def clone(primary_profile_path=None, profile_path=None):
        # primary_profile_path = (
        #     primary_profile_path
        #     if primary_profile_path
        #     else self.__find_primary_profile_path__()
        # )

        return FirefoxProfile.clone(
            primary_profile_path,
            path_to=profile_path,
            ignore=ignore_patterns(
                "cache2", "lock", "places.sqlite", "startupCache", "storage"
            ),
            restore=False,
        )

    @staticmethod
    def primary_profile_path():
        if is_wsl():
            user = wsl_user()
            return Path(
                f"/mnt/c/Users/{user}/AppData/Roaming/Mozilla/Firefox/Profiles/"
            )
        elif is_linux():
            user = getpass.getuser()
            return Path(f"/home/{user}/.mozilla/firefox/")
        elif is_mac():
            user = getpass.getuser()
            return Path(f"/Users/{user}/Library/Application Support/Firefox/Profiles/")
