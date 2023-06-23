import os
import sys
from os.path import exists
from shutil import copyfile

from colorama import Style
from xdg import BaseDirectory

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

__package_name = "oo_bin"

config_path = BaseDirectory.save_config_path(__package_name)
main_config_path = os.path.join(
    BaseDirectory.save_config_path(__package_name), "config.toml"
)
tunnels_local_config_path = os.path.join(
    BaseDirectory.save_config_path(__package_name), "tunnels_local.toml"
)
tunnels_config_path = os.path.join(
    BaseDirectory.save_config_path(__package_name), "tunnels.toml"
)
ssh_config_path = os.path.join(
    BaseDirectory.save_config_path(__package_name), "ssh_config"
)


def __get_config(path):
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
            return data
    except FileNotFoundError:
        return {}
    except tomllib.TOMLDecodeError as e:
        print(f"\nError at {Style.BRIGHT}{path}", file=sys.stderr)
        print(f"{e}", file=sys.stderr)
        sys.exit(1)


def main_config():
    return __get_config(main_config_path)


def tunnels_config(profile=None):
    local_config = __get_config(tunnels_local_config_path)
    config = __get_config(tunnels_config_path)
    config.update(local_config)

    if profile:
        return config.get(profile, {})

    return config


def backup_tunnels_config():
    if exists(tunnels_config_path):
        tunnels_bak = os.path.join(
            BaseDirectory.save_config_path(__package_name), "tunnels.toml.bak"
        )
        copyfile(tunnels_config_path, tunnels_bak)

    if exists(ssh_config_path):
        ssh_bak = os.path.join(
            BaseDirectory.save_config_path(__package_name), "ssh_config.bak"
        )
        copyfile(ssh_config_path, ssh_bak)
