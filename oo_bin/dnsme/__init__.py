import re
import shutil
from datetime import datetime

import colorama
import dns.resolver
import dns.reversename
import whois

from oo_bin.dnsme.SpfValidator import SpfValidator
from oo_bin.errors import DependencyNotMetError, DomainNotExistError


class Dnsme:
    def __init__(self, domain):
        self.domain = domain

        self.__whois = whois.whois(self.domain)

        if not shutil.which("whois"):
            raise DependencyNotMetError("whois is not installed, or is not in the path")

        # self.__whois_failed = False
        # try:
        if not self.__whois:
            raise DomainNotExistError(f"The domain {self.domain} does not exist")
        # except whois.exceptions.WhoisCommandFailed:
        #     self.__whois_failed = True

        self.a = None
        self.mx = None
        self.ns = None
        self.txt = None

    @property
    def __expiration_date(self):
        if (
            type(self.__whois.expiration_date) is list
            and len(self.__whois.expiration_date) > 0
        ):
            return self.__whois.expiration_date[0].astimezone()
        elif type(self.__whois.expiration_date) is datetime:
            return self.__whois.expiration_date.astimezone()
        else:
            return "Unknown"

    @property
    def __days_to_expiration(self):
        if type(self.__expiration_date) is datetime:
            return (self.__expiration_date - datetime.now().astimezone()).days
        else:
            return "Unknown"

    @property
    def __a_lookup(self):
        try:
            if not self.a:
                self.a = sorted(dns.resolver.resolve(self.domain, "A"))
            return self.a
        except (
            dns.resolver.LifetimeTimeout,
            dns.resolver.NXDOMAIN,
            dns.resolver.YXDOMAIN,
            dns.resolver.NoAnswer,
            dns.resolver.NoNameservers,
        ):
            return []

    @property
    def __mx_lookup(self):
        try:
            if not self.mx:
                self.mx = sorted(
                    dns.resolver.resolve(self.domain, "MX"),
                    key=lambda d: (d.preference, d.exchange),
                )
            return self.mx
        except (
            dns.resolver.LifetimeTimeout,
            dns.resolver.NXDOMAIN,
            dns.resolver.YXDOMAIN,
            dns.resolver.NoAnswer,
            dns.resolver.NoNameservers,
        ):
            return []

    @property
    def __ns_lookup(self):
        try:
            if not self.ns:
                self.ns = sorted(dns.resolver.resolve(self.domain, "NS"))
            return self.ns
        except (
            dns.resolver.LifetimeTimeout,
            dns.resolver.NXDOMAIN,
            dns.resolver.YXDOMAIN,
            dns.resolver.NoAnswer,
            dns.resolver.NoNameservers,
        ):
            return []

    @property
    def __reverse_lookup(self):
        reverse = []
        for a_record in self.__a_lookup:
            try:
                a = dns.reversename.from_address(f"{a_record}")
                for ptr in dns.resolver.query(a, "PTR"):
                    reverse.append(ptr)
            except (
                dns.resolver.LifetimeTimeout,
                dns.resolver.NXDOMAIN,
                dns.resolver.YXDOMAIN,
                dns.resolver.NoAnswer,
                dns.resolver.NoNameservers,
            ):
                pass

        return reverse

    @property
    def __spf_lookup(self):
        spf_entries = []
        for txt_entry in self.__txt_lookup:
            if re.search(r"spf", f"{txt_entry}"):
                spf_entries.append(txt_entry)

        return spf_entries

    @property
    def __dmarc_lookup(self):
        try:
            return sorted(dns.resolver.resolve(f"_dmarc.{self.domain}", "TXT"))
        except (
            dns.resolver.LifetimeTimeout,
            dns.resolver.NXDOMAIN,
            dns.resolver.YXDOMAIN,
            dns.resolver.NoAnswer,
            dns.resolver.NoNameservers,
        ):
            return []

    @property
    def __dkim_lookup(self):
        dkims = []
        try:
            selector1 = dns.resolver.resolve(
                f"selector1._domainkey.{self.domain}", "CNAME"
            )
            for dkim_entry in selector1:
                dkims.append(dkim_entry)
        except (
            dns.resolver.LifetimeTimeout,
            dns.resolver.NXDOMAIN,
            dns.resolver.YXDOMAIN,
            dns.resolver.NoAnswer,
            dns.resolver.NoNameservers,
        ):
            pass

        try:
            selector2 = dns.resolver.resolve(
                f"selector2._domainkey.{self.domain}", "CNAME"
            )
            for dkim_entry in selector2:
                dkims.append(dkim_entry)
        except (
            dns.resolver.LifetimeTimeout,
            dns.resolver.NXDOMAIN,
            dns.resolver.YXDOMAIN,
            dns.resolver.NoAnswer,
            dns.resolver.NoNameservers,
        ):
            pass

        return dkims

    @property
    def __txt_lookup(self):
        if not self.txt:
            try:
                self.txt = sorted(dns.resolver.resolve(self.domain, "TXT"))
            except (
                dns.resolver.LifetimeTimeout,
                dns.resolver.NXDOMAIN,
                dns.resolver.YXDOMAIN,
                dns.resolver.NoAnswer,
                dns.resolver.NoNameservers,
            ):
                self.txt = ""

        return self.txt

    def __str__(self):
        s = f"{colorama.Style.BRIGHT}Registrar Info\n"
        s += f"{colorama.Style.RESET_ALL}Registrar: {self.__whois.registrar}\n"
        s += f"{self.domain} expires in {self.__days_to_expiration} days on {self.__expiration_date}"
        s += "\n\n"

        s += f"{colorama.Style.RESET_ALL}{colorama.Style.BRIGHT}A Records\n"
        for a_entry in self.__a_lookup:
            s += f"{colorama.Style.RESET_ALL}{a_entry}\n"
        s += "\n"

        s += f"{colorama.Style.BRIGHT}MX Records\n"
        for mx_entry in self.__mx_lookup:
            s += f"{colorama.Style.RESET_ALL}{mx_entry.preference: <2} {mx_entry.exchange}\n"
        s += "\n"

        s += f"{colorama.Style.BRIGHT}NS Records\n"
        for ns_entry in self.__ns_lookup:
            s += f"{colorama.Style.RESET_ALL}{ns_entry}\n"
        s += "\n"

        s += f"{colorama.Style.BRIGHT}Reverse DNS\n"
        for reverse_entry in self.__reverse_lookup:
            s += f"{colorama.Style.RESET_ALL}{reverse_entry}\n"
        s += "\n"

        s += f"{colorama.Style.BRIGHT}SPF Records\n"
        for spf_entry in self.__spf_lookup:
            s += f"{colorama.Style.RESET_ALL}{spf_entry}\n"
            lookups = SpfValidator.parse(spf_entry).lookups()
            if lookups > 10:
                lookups = f"{colorama.Back.RED}{lookups}"
            else:
                lookups = f"{colorama.Fore.GREEN}{lookups}"
            s+= f"  Lookups: {lookups}\n"

        s += "\n"

        s += f"{colorama.Style.BRIGHT}DMARC Record\n"
        for dmarc_entry in self.__dmarc_lookup:
            s += f"{colorama.Style.RESET_ALL}{dmarc_entry}\n"
        s += "\n"

        s += f"{colorama.Style.BRIGHT}DKIM Records (Office 365 only)\n"
        for dkim_entry in self.__dkim_lookup:
            s += f"{colorama.Style.RESET_ALL}{dkim_entry}\n"
        s += "\n"

        s += f"{colorama.Style.BRIGHT}TXT Records\n"
        for txt_entry in self.__txt_lookup:
            s += f"{colorama.Style.RESET_ALL}{txt_entry}\n"

        return s
