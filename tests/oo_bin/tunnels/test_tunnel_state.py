import pytest
from oo_bin.tunnels import TunnelState, TunnelType
import json
from pathlib import Path
import tempfile


class TestTunnelState:
    def test_profile_not_found(self):
        with pytest.raises(FileNotFoundError):
            TunnelState("non_existing_profile")

    def test_new_profile(self):
        (_, state_file) = tempfile.mkstemp()

        with open(state_file, "w") as f:
            json.dump({}, f)

        state = TunnelState("new_profile", state_file=state_file)

        assert state.name == "new_profile"

    def test_delete(self):
        (_, state_file) = tempfile.mkstemp()
        file = Path(state_file)

        state = TunnelState("profile", state={"pid": 1}, state_file=state_file)

        assert file.is_file()

        state.delete()

        assert file.is_file() is False

    def test_pid(self):
        (_, state_file) = tempfile.mkstemp()

        state = TunnelState("profile", state={"pid": 5}, state_file=state_file)

        assert state.pid == 5

        state.pid = 7

        assert state.pid == 7

        with open(state_file, "r") as f:
            file_state = json.load(f)

            assert file_state["pid"] == 7

    def test_type(self):
        (_, state_file) = tempfile.mkstemp()

        state = TunnelState(
            "profile", state={"type": TunnelType.SOCKS.value}, state_file=state_file
        )

        assert state.type == TunnelType.SOCKS.value

        state.type = TunnelType.RDP.value

        assert state.type == TunnelType.RDP.value

        with open(state_file, "r") as f:
            file_state = json.load(f)

            assert file_state["type"] == TunnelType.RDP.value
