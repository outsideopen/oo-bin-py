import os
from pathlib import Path

from oo_bin.ssh import Ssh


def test_profile_connect(mocker, tmp_path):
    ssh_config_path = "/home/runner/.config/oo_bin/ssh_config"

    mocker.patch(
        "oo_bin.config.tunnels_config_path",
        os.path.join(
            Path(__file__).parent.parent.parent, "test_config", "tunnels.toml"
        ),
    )
    mocker.patch("oo_bin.ssh.ssh_config_path", ssh_config_path)
    mocker.patch("os.spawnvpe", return_value=True)
    ssh = Ssh()

    command = ssh.connect("foo")
    assert command == ["ssh", "-F", ssh_config_path, "foo.example.com"]

    command2 = ssh.connect("foo", "second_ssh")
    assert command2 == [
        "ssh",
        "-F",
        ssh_config_path,
        "-J",
        "foo.example.com",
        "-p",
        "2222",
        "192.168.2.2",
    ]

    command3 = ssh.connect("foo", "192.168.3.1")
    assert command3 == [
        "ssh",
        "-F",
        ssh_config_path,
        "-J",
        "foo.example.com",
        "-p",
        "22",
        "192.168.3.1",
    ]

    command4 = ssh.connect("foo", "192.168.3.1:2323")
    assert command4 == [
        "ssh",
        "-F",
        ssh_config_path,
        "-J",
        "foo.example.com",
        "-p",
        "2323",
        "192.168.3.1",
    ]
