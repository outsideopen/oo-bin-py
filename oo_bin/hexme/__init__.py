import shutil
from math import ceil
from subprocess import PIPE, Popen

import pyperclip as pc
from colorama import Style

from oo_bin.errors import DependencyNotMetError


class Hexme:
    def __init__(self, chars):
        self.runtime_dependencies_met()
        self.__nr_of_chars__ = chars

    def runtime_dependencies_met(self):
        if not shutil.which("openssl"):
            raise DependencyNotMetError(
                "openssl is not installed, or is not in the path"
            )

    def __generate_random_hex__(self):
        nr_of_bytes = ceil(self.__nr_of_chars__ / 2)

        cmd = ["openssl", "rand", "-hex", f"{nr_of_bytes}"]
        process = Popen(cmd, stdout=PIPE)
        output, error = process.communicate(timeout=5)

        return output.strip().decode("utf-8")[0 : self.__nr_of_chars__]

    def __str__(self):
        hex = self.__generate_random_hex__()
        pc.copy(hex)

        return f"{self.__nr_of_chars__} character hex string generated and copied to the clipboard:\
\n{Style.BRIGHT}{hex}"
