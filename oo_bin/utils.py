import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from platform import uname

import requests
from colorama import Fore
from xdg import BaseDirectory

from oo_bin import __version__
from oo_bin.config import backup_tunnels_config, config_path, main_config
from oo_bin.errors import HttpError

data_path = BaseDirectory.save_data_path("oo_bin")
last_update_file = os.path.join(data_path, "last_update")


def is_wsl():
    return "microsoft-standard" in uname().release


def wsl_user():
    cmd = ["powershell.exe", "$env:UserName"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output = process.communicate()
    return output[0].decode("utf-8").strip()


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

        files = ["tunnels.toml", "ssh_config"]
        username = update.get("username")
        password = update.get("password")

        for file in files:
            try:
                with requests.get(
                    f"{update.get('url')}/{file}",
                    auth=(username, password),
                    stream=True,
                ) as r:
                    r.raise_for_status()
                    with open(f"{config_path}/{file}", "wb") as f:
                        shutil.copyfileobj(r.raw, f)
                print(
                    Fore.GREEN
                    + f"Your configuration has been updated from {update.get('url')}/{file}"
                )
            except requests.exceptions.HTTPError as e:
                raise HttpError(
                    f"Your configuration could not be automatically updated. See the error below for more details:\n\n{e}"
                )
    else:
        print(Fore.RED + "Remote updates are disabled in your configuration")


def __set_last_updated_time():
    with open(last_update_file, "w") as f:
        f.write(str(datetime.now()))


def __get_last_updated_time():
    try:
        with open(last_update_file, "r") as f:
            line = f.readline().strip()
            return datetime.strptime(line, "%Y-%m-%d %H:%M:%S.%f")
    except FileNotFoundError:
        return datetime.min


def __latest_release_info():
    with requests.get(
        "https://api.github.com/repos/outsideopen/oo-bin-py/releases/latest"
    ) as r:
        r.raise_for_status()
        response = r.json()

        return response


def __download_package(url):
    tmp_dir = tempfile.mkdtemp(dir=tempfile.gettempdir())
    tmp_file = Path(tmp_dir).joinpath(Path(url).name)

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(tmp_file, "wb") as f:
            for chunk in r.iter_content():
                f.write(chunk)

    return tmp_file


def update_package():
    release_info = __latest_release_info()

    tag = release_info.get("tag_name")

    if __version__ == "0.0.0":
        print("Updates are not supported on development versions of the project.")
        sys.exit(1)

    if tag != __version__:
        confirm = input(
            f"New version {tag} is available. Do you want to update now? [yN] "
        )

        if confirm in ["y", "Y"]:
            download_url = release_info.get("assets", [{}])[0].get(
                "browser_download_url", None
            )
            tmp_file = __download_package(download_url)

            cmd = ["pip3", "install", "--force-reinstall", str(tmp_file)]
            subprocess.run(cmd)


def auto_update():
    config = main_config()
    update = config.get("tunnels", {}).get("update", {})
    auto_update = update.get("auto_update", False)

    if auto_update:
        last_updated = __get_last_updated_time()
        if last_updated < datetime.today() - timedelta(days=1):
            update_tunnels_config()
            update_package()
            __set_last_updated_time()
