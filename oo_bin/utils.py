from platform import uname


def is_wsl():
    return "microsoft-standard" in uname().release


def is_mac():
    return "Darwin" in uname().system


def is_linux():
    return "Linux" in uname().system
