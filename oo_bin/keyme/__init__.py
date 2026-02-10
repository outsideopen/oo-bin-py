import os
import tomllib

import colorama
import pyperclip as pc
import tomli_w

from oo_bin.config import main_config, save_main_config


class Keyme:
    def __init__(self, file, save=False):
        config = main_config()
        self.file = None

        if file:
            self.file = file

            if save:
                self.__save_file_to_config()
        else:
            self.file = config.get("keyme", {}).get("file", None)

    def __str__(self):
        colorama.init(autoreset=True)
        if self.file:
            if os.path.isfile(self.file):
                with open(self.file, "r") as file:
                    content = file.read()
                    pc.copy(content)
                    return f"{colorama.Fore.GREEN}SSH public key copied to clipboard from {colorama.Style.BRIGHT}{self.file}"
            else:
                return f"{colorama.Fore.RED}Provided file does not exist: {colorama.Style.BRIGHT}{self.file}"

        else:
            return f"{colorama.Back.YELLOW}{colorama.Fore.BLACK}No key file provided. Add one with the {colorama.Style.BRIGHT}{colorama.Fore.BLUE}--file{colorama.Style.RESET_ALL}{colorama.Back.YELLOW}{colorama.Fore.BLACK} option. Save it for next time with the {colorama.Fore.BLUE}{colorama.Style.BRIGHT}--save{colorama.Style.RESET_ALL}{colorama.Back.YELLOW}{colorama.Fore.BLACK} flag."

        return ""

    def __save_file_to_config(self):
        data_to_save = {"file": self.file}
        config = main_config()
        config["keyme"] = data_to_save
        save_main_config(config)
