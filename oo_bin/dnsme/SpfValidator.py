import typing
from dataclasses import dataclass

import dns.resolver

T = typing.TypeVar("T", bound="SpfValidator")


@dataclass
class SpfValidator:
    version: int
    ips: dict[str, T]
    includes: list[str]
    state: str

    @staticmethod
    def parse(record) -> T | None:
        recs = record.strip('"').split(" ")
        state = recs.pop()
        try:
            version = recs[0]
        except Exception:
            return None

        ips = []
        includes = {}
        for host in recs[1:]:
            (type, host) = host.split(":", 1)
            if type == "include":
                for row in dns.resolver.resolve(host, "TXT"):
                    data = row.strings[0].decode("utf8")
                    if data.startswith("v=spf"):
                        includes[host] = SpfValidator.parse(data)
            else:
                ips.append((type, host))

        return SpfValidator(version=version[-1], includes=includes, ips=ips, state=state)

    def lookups(self) -> int:
        """Returns how many lookups occurred"""
        total = len(self.includes)
        for include in self.includes:
            total += self.includes[include].lookups()
        return total
