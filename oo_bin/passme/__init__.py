import random

import colorama
import pyperclip as pc
import requests


class Passme:
    def __str__(self):
        return self.__fetch_password()

    def __fetch_password(self):
        SPECIALS = "*@#$%&~"

        URL = "https://outsideopen.com/api/pw/"
        pw = None

        try:
            response = requests.get(URL)

            response.raise_for_status()  # Raises exception for 4xx/5xx status codes

            pw = response.text.strip()
            pw += random.choice(SPECIALS)

            pc.copy(pw)

            return f"{colorama.Fore.GREEN}Password copied to clipboard: {colorama.Style.BRIGHT}{pw}"

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
