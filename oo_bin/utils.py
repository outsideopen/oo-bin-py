import os
import shutil
from datetime import datetime, timedelta
from platform import uname

import requests
from colorama import Fore
from xdg import BaseDirectory

from oo_bin.config import backup_tunnels_config, main_config, tunnels_config_path

data_path = BaseDirectory.save_data_path("oo_bin")
last_update_file = os.path.join(data_path, "last_update")


def is_wsl():
    return "microsoft-standard" in uname().release


def is_mac():
    return "Darwin" in uname().system


def is_linux():
    return "Linux" in uname().system


def update_tunnels_config():
    config = main_config()

    update = config.get("tunnels", {}).get("update", {})
    enabled = update.get("enabled", True)

    if enabled:
        backup_tunnels_config()

        url = update.get("url")
        username = update.get("username")
        password = update.get("password")

        with requests.get(url, auth=(username, password), stream=True) as r:
            r.raise_for_status()
            with open(tunnels_config_path, "wb") as f:
                shutil.copyfileobj(r.raw, f)
        print(Fore.GREEN + f"Your configuration has been updated from {url}")
    else:
        print(Fore.RED + "Remote updates are disabled in your configuration")


def __set_last_updated_time__():
    with open(last_update_file, "w") as f:
        f.write(str(datetime.now()))


def __get_last_updated_time__():
    try:
        with open(last_update_file, "r") as f:
            line = f.readline().strip()
            return datetime.strptime(line, "%Y-%m-%d %H:%M:%S.%f")
    except FileNotFoundError:
        return datetime.min


def auto_update():
    config = main_config()
    update = config.get("tunnels", {}).get("update", {})
    auto_update = update.get("auto_update", False)

    if auto_update:
        last_updated = __get_last_updated_time__()
        if last_updated < datetime.today() - timedelta(days=1):
            update_tunnels_config()
            __set_last_updated_time__()
