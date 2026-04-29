import configparser
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from oo_bin.tunnels.command.tunnels import tunnels


@patch("oo_bin.tunnels.command.tunnels.generate_name")
@patch("oo_bin.tunnels.command.tunnels.BaseDirectory")
def test_new_creates_profile(mock_base_directory, mock_generate_name, tmp_path):
    expected_path = f"{tmp_path}/profiles/kakaw"

    runner = CliRunner()

    mock_base_directory.save_data_path.return_value = str(tmp_path)
    mock_generate_name.return_value = "kakaw"

    result = runner.invoke(tunnels, ["profile", "new"])
    assert result.exit_code == 0
    assert f"Profile created at: {expected_path}" in result.output
    assert os.path.exists(expected_path)


@patch("oo_bin.tunnels.command.tunnels.BrowserProfile")
def test_clone_fails_without_profile(mock_browser_profile, tmp_path):
    runner = CliRunner()

    mock_browser_profile.primary_profile_path.return_value = str(tmp_path)

    result = runner.invoke(tunnels, ["profile", "clone", "parent"])
    assert result.exit_code == -1
    assert (
        f"ERROR: No profiles found, please use `oo tunnels profile new` first."
        in result.output
    )

    Path(tmp_path / "profiles.ini").touch()
    result = runner.invoke(tunnels, ["profile", "clone", "parent"])
    assert result.exit_code == -1
    assert (
        f"ERROR: profile `parent` not found, please use `oo tunnels profile new` first."
        in result.output
    )


@patch("oo_bin.tunnels.command.tunnels.generate_name")
@patch("oo_bin.tunnels.command.tunnels.BrowserProfile.primary_profile_path")
@patch("oo_bin.tunnels.command.tunnels.BaseDirectory")
def test_clone_profile_ok(
    mock_base_directory, mock_browser_profile, mock_generate_name, tmp_path
):
    profiles = tmp_path / "profiles"
    profiles.mkdir()
    parent = profiles / "parent"
    parent.mkdir()

    expected_path = f"{tmp_path}/profiles/kakaw"

    config = configparser.ConfigParser()
    config["Profile0"] = {"Name": "parent", "Path": "parent", "IsRelative": "1"}
    with Path(profiles / "profiles.ini").open(mode="w") as f:
        config.write(f)

    runner = CliRunner()

    mock_browser_profile.return_value = str(profiles)
    mock_base_directory.save_data_path.return_value = str(tmp_path)
    mock_generate_name.return_value = "kakaw"

    result = runner.invoke(tunnels, ["profile", "clone", "parent"])

    expected_output = "\n".join(
        [
            f'Profile cloned from:    {profiles / "parent"}',
            f"Created new profile at: {expected_path}",
        ]
    )

    assert result.exit_code == 0
    assert f"{expected_output}\n" == result.output
    assert os.path.exists(expected_path)
