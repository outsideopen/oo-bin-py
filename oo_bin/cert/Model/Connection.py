import typing
from dataclasses import dataclass
from typing import List

from OpenSSL import SSL

T = typing.TypeVar("T", bound="Connection")


@dataclass
class Connection:
    """Models the SSL connection information"""

    hostname: str
    ipAddress: str
    protocolName: str
    protocolVersion: int

    ciphers: List[str]
    cipherBits: str
    cipherName: str
    cipherVersion: str

    alpnProto: str

    def __post_init__(self):
        self.sigAlg = None
        self.crlUris = []
        self.altNames = []

    @property
    def dnsCaa(self) -> bool:
        return True

    @staticmethod
    def parse(host: str, ip: str, ssl: SSL.Connection) -> T:
        return Connection(
            hostname=host,
            ipAddress=ip,
            protocolName=ssl.get_protocol_version_name(),
            protocolVersion=ssl.get_protocol_version(),
            alpnProto=ssl.get_alpn_proto_negotiated(),
            ciphers=ssl.get_cipher_list(),
            cipherBits=ssl.get_cipher_bits(),
            cipherName=ssl.get_cipher_name(),
            cipherVersion=ssl.get_cipher_version(),
        )
