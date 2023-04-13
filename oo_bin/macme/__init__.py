import requests


class Macme:
    def __init__(self, mac_address):
        self.mac_address = mac_address

    def __lookup__(self):
        with requests.get(f"http://api.macvendors.com/{self.mac_address}") as r:
            r.raise_for_status()
            return r.text

    def __str__(self):
        return self.__lookup__()
