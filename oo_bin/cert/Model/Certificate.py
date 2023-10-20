import base64
import binascii
import typing
from dataclasses import InitVar, dataclass
from datetime import datetime
from typing import List, Union

import dns.resolver
from cryptography.x509 import oid
from OpenSSL.crypto import X509

T = typing.TypeVar("T", bound="Certificate")

KEY_TYPE_MAP = {6: "RSA"}

default_thresholds = {
    "error": {"days": 2, "opts": {"bg": "red"}},
    "warning": {"days": 7, "opts": {"bg": "yellow"}},
    "info": {"days": 14, "opts": {"fg": "yellow"}},
}


@dataclass
class Certificate:
    """Models an SSL Certificate"""

    id: str
    host: str
    subject: str
    issuer: str
    commonNames: List[str]
    keyAlg: str
    keyStrength: int
    serialNumber: Union[int | str]
    validFrom: datetime
    validUntil: datetime
    sha1Hash: str
    sha256Hash: str
    pinSha256: str
    dnsCaa: bool
    altNames: List[str] = None
    crlUris: List[str] = None
    sigAlg: str = None

    @staticmethod
    def parse(host: str, certificate: X509) -> T:
        def __toDate(value: str) -> datetime:
            return datetime.strptime(value, "%Y%m%d%H%M%SZ")

        key = certificate.get_pubkey()

        def pinSha256():
            return (
                base64.encodebytes(
                    binascii.unhexlify(
                        certificate.digest("sha256")
                        .decode("utf8")
                        .replace(":", "")
                        .lower()
                    )
                )
                .rstrip(b"\n")
                .decode("utf8")
            )

        # OpenSSL will throw an error if you attempt to get the extensions for a cert without a local issuer
        # i.e. - self-signed or private ca
        c = certificate.to_cryptography()

        altNames = []
        for value in c.extensions.get_extension_for_oid(
            oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
        ).value:
            altNames.append(value.value)

        subject = c.subject.rfc4514_string()
        caa = False
        try:
            caa = True if dns.resolver.resolve(host, "CAA") else False
        except Exception:
            pass

        return Certificate(
            id="kakaw",
            host=host,
            subject=subject,
            issuer=certificate.get_issuer().CN,
            commonNames=certificate.get_subject().CN,
            serialNumber=hex(certificate.get_serial_number()),
            validFrom=__toDate(certificate.get_notBefore().decode("utf8")),
            validUntil=__toDate(certificate.get_notAfter().decode("utf8")),
            sigAlg=certificate.get_signature_algorithm().decode("utf8"),
            keyStrength=key.bits(),
            keyAlg=str(key.type()),
            sha1Hash=certificate.digest("sha1").decode("utf8"),
            sha256Hash=certificate.digest("sha256").decode("utf8"),
            pinSha256=pinSha256(),
            dnsCaa=caa,
            altNames=altNames,
        )

    @property
    def expiresIn(self) -> int:
        return (self.validUntil - datetime.now()).days

    def status(self, thresholds: object = None) -> str:
        """Determines the status based on the given thresholds"""
        if not thresholds:
            thresholds = default_thresholds

        if self.expiresIn < 1:
            return "expired"

        if self.expiresIn <= thresholds["error"]["days"]:
            return "error"

        if self.expiresIn <= thresholds["warning"]["days"]:
            return "warning"

        if self.expiresIn <= thresholds["info"]["days"]:
            return "info"

        return "ok"
