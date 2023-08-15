import requests


class Macme:
    def __init__(self, mac_address):
        self.mac_address = mac_address

    def __lookup__(self):
        try:
            with requests.get(f"http://api.macvendors.com/{self.mac_address}") as r:
                r.raise_for_status()
                return r.text
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print("The vendor could not be identified.")
            else:
                raise e
            return ""

    def __str__(self):
        return self.__lookup__()
