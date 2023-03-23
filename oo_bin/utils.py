import shutil
from platform import uname

import requests
from colorama import Fore

from oo_bin.config import backup_tunnels_config, main_config, tunnels_config_path


def is_wsl():
    return "microsoft-standard" in uname().release


def is_mac():
    return "Darwin" in uname().system


def is_linux():
    return "Linux" in uname().system


def update_tunnels_config():
    config = main_config()

    update = config.get("tunnels", {}).get("update", None)

    if update:
        backup_tunnels_config()

        url = update.get("url")
        username = update.get("username")
        password = update.get("password")

        with requests.get(url, auth=(username, password), stream=True) as r:
            r.raise_for_status()
            with open(tunnels_config_path, "wb") as f:
                shutil.copyfileobj(r.raw, f)
        print(Fore.GREEN + f"Your configuration has been updated from {url}")
