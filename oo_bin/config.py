import os
from os.path import exists
from shutil import copyfile

from xdg import BaseDirectory

from oo_bin.errors import ConfigNotFoundError

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

__package_name__ = "oo_bin"

config_path = BaseDirectory.save_config_path(__package_name__)
main_config_path = os.path.join(
    BaseDirectory.save_config_path(__package_name__), "config.toml"
)
tunnels_local_config_path = os.path.join(
    BaseDirectory.save_config_path(__package_name__), "tunnels_local.toml"
)
tunnels_config_path = os.path.join(
    BaseDirectory.save_config_path(__package_name__), "tunnels.toml"
)
ssh_config_path = os.path.join(
    BaseDirectory.save_config_path(__package_name__), "ssh_config"
)


def __get_config__(path):
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
            return data
    except FileNotFoundError:
        return {}


def main_config():
    return __get_config__(main_config_path)


def backup_tunnels_config():
    if exists(tunnels_config_path):
        tunnels_bak = os.path.join(
            BaseDirectory.save_config_path(__package_name__), "tunnels.toml.bak"
        )
        copyfile(tunnels_config_path, tunnels_bak)

    if exists(ssh_config_path):
        ssh_bak = os.path.join(
            BaseDirectory.save_config_path(__package_name__), "ssh_config.bak"
        )
        copyfile(ssh_config_path, ssh_bak)


def tunnels_config():
    local_config = __get_config__(tunnels_local_config_path)
    config = __get_config__(tunnels_config_path)
    config.update(local_config)

    return config


def __config_by_type__(type="socks", profile=None):
    config = tunnels_config()
    typed_config = {k: v for k, v in config.items() if v.get("type", "socks") == type}

    if not profile:
        return typed_config
    else:
        section = typed_config.get(profile, {})

        if not section:
            raise ConfigNotFoundError(
                f"{profile} could not be found in your configuration file"
            )
        return section


def socks_config(profile=None):
    return __config_by_type__(type="socks", profile=profile)


def rdp_config(profile=None):
    return __config_by_type__(type="rdp", profile=profile)


def vnc_config(profile=None):
    return __config_by_type__(type="vnc", profile=profile)
