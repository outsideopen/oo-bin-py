import os
from subprocess import DEVNULL, PIPE, Popen
import re


class TunnelProcess:
    def __init__(self, type, pid_file):
        self.type = type
        self.pid_file = pid_file
        self.pid = self.__pid_from_pid_file__(pid_file)
        self.jump_host = self.__jump_host_from_pid_file__(pid_file)
        self.profile = self.__profile_from_pid_file__(pid_file)

    def is_running(self):
        if self.__ps_output__(self.pid_file):
            return True
        else:
            return False

    def stop(self):
        if self.pid:
            Popen(["kill", self.pid], stdout=DEVNULL)

        self.pid_file.unlink(missing_ok=True)

    def __ps_output__(self, pid_file):
        try:
            with open(pid_file, "r") as f:
                pid = f.read()
                ps_output = Popen(["ps", "-f", "-p", pid], stdout=PIPE).communicate()

                ps_utf8 = ps_output[0].decode("utf-8") if len(ps_output[0]) > 0 else ""

                return ps_utf8.split("\n")[1] if len(ps_utf8.split("\n")) > 1 else None

        except FileNotFoundError:
            return None

    def __pid_from_pid_file__(self, pid_file):
        ps_output = self.__ps_output__(pid_file)

        if not ps_output:
            return None

        ps_pid = ps_output.split()[1].strip()

        if ps_pid:
            return ps_pid
        else:
            pid_file.unlink(missing_ok=True)
            return None

    def __jump_host_from_pid_file__(self, pid_file):
        ps_output = self.__ps_output__(pid_file)

        if not ps_output:
            return None

        ps_host = ps_output.split()[-1].strip()

        if ps_host:
            return ps_host
        else:
            pid_file.unlink(missing_ok=True)
            return None

    def __profile_from_pid_file__(self, pid_file):
        m = re.search(r"(.*?)(_Socks.*|_Rdp.*|_Vnc.*)", pid_file.name)
        return str(m.group(1)) if m else None
