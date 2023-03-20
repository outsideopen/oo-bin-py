from platform import uname


def is_wsl():
    return "microsoft-standard" in uname().release
