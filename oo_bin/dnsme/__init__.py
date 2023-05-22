import re
import shutil
from datetime import datetime

import dns.resolver
import dns.reversename
import whois
from colorama import Style

from oo_bin.errors import DependencyNotMetError, DomainNotExistError


class Dnsme:
    def __init__(self, domain):
        self.domain = domain

        if not shutil.which("whois"):
            raise DependencyNotMetError("whois is not installed, or is not in the path")

        if not self.__whois__:
            raise DomainNotExistError(f"The domain {self.domain} does not exist")

        self.a = None
        self.mx = None
        self.ns = None
        self.txt = None

    @property
    def __whois__(self):
        return whois.query(self.domain)

    @property
    def __a_lookup__(self):
        try:
            if not self.a:
                self.a = sorted(dns.resolver.resolve(self.domain, "A"))
            return self.a
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            return []

    @property
    def __mx_lookup__(self):
        try:
            if not self.mx:
                self.mx = sorted(
                    dns.resolver.resolve(self.domain, "MX"),
                    key=lambda d: (d.preference, d.exchange),
                )
            return self.mx
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            return []

    @property
    def __ns_lookup__(self):
        try:
            if not self.ns:
                self.ns = sorted(dns.resolver.resolve(self.domain, "NS"))
            return self.ns
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            return []

    @property
    def __reverse_lookup__(self):
        reverse = []
        for a_record in self.__a_lookup__:
            try:
                a = dns.reversename.from_address(f"{a_record}")
                for ptr in dns.resolver.query(a, "PTR"):
                    reverse.append(ptr)
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                pass

        return reverse

    @property
    def __spf_lookup__(self):
        spf_entries = []
        for txt_entry in self.__txt_lookup__:
            if re.search(r"spf", f"{txt_entry}"):
                spf_entries.append(txt_entry)

        return spf_entries

    @property
    def __dmarc_lookup__(self):
        try:
            return sorted(dns.resolver.resolve(f"_dmarc.{self.domain}", "TXT"))
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            return []

    @property
    def __dkim_lookup__(self):
        dkims = []
        try:
            selector1 = dns.resolver.resolve(
                f"selector1._domainkey.{self.domain}", "CNAME"
            )
            for dkim_entry in selector1:
                dkims.append(dkim_entry)
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            pass

        try:
            selector2 = dns.resolver.resolve(
                f"selector2._domainkey.{self.domain}", "CNAME"
            )
            for dkim_entry in selector2:
                dkims.append(dkim_entry)
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            pass

        return dkims

    @property
    def __txt_lookup__(self):
        if not self.txt:
            try:
                self.txt = sorted(dns.resolver.resolve(self.domain, "TXT"))
            except dns.resolver.NoAnswer:
                self.txt = ""

        return self.txt

    def __str__(self):
        s = f"{Style.BRIGHT}Registrar Info\n"
        s += f"{Style.RESET_ALL}Registrar: {self.__whois__.registrar}\n"
        s += f"{self.domain} expires in {(self.__whois__.expiration_date - datetime.now()).days} \
days on {self.__whois__.expiration_date.astimezone()}\n"

        s += "\n"

        s += f"{Style.BRIGHT}A Records\n"
        for a_entry in self.__a_lookup__:
            s += f"{Style.RESET_ALL}{a_entry}\n"
        s += "\n"

        s += f"{Style.BRIGHT}MX Records\n"
        for mx_entry in self.__mx_lookup__:
            s += f"{Style.RESET_ALL}{mx_entry.preference: <2} {mx_entry.exchange}\n"
        s += "\n"

        s += f"{Style.BRIGHT}NS Records\n"
        for ns_entry in self.__ns_lookup__:
            s += f"{Style.RESET_ALL}{ns_entry}\n"
        s += "\n"

        s += f"{Style.BRIGHT}Reverse DNS\n"
        for reverse_entry in self.__reverse_lookup__:
            s += f"{Style.RESET_ALL}{reverse_entry}\n"
        s += "\n"

        s += f"{Style.BRIGHT}SPF Records\n"
        for spf_entry in self.__spf_lookup__:
            s += f"{Style.RESET_ALL}{spf_entry}\n"
        s += "\n"

        s += f"{Style.BRIGHT}DMARC Record\n"
        for dmarc_entry in self.__dmarc_lookup__:
            s += f"{Style.RESET_ALL}{dmarc_entry}\n"
        s += "\n"

        s += f"{Style.BRIGHT}DKIM Records (Office 365 only)\n"
        for dkim_entry in self.__dkim_lookup__:
            s += f"{Style.RESET_ALL}{dkim_entry}\n"
        s += "\n"

        s += f"{Style.BRIGHT}TXT Records\n"
        for txt_entry in self.__txt_lookup__:
            s += f"{Style.RESET_ALL}{txt_entry}\n"

        return s
