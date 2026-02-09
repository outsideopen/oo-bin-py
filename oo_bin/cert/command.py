import traceback
from functools import reduce

import click

from oo_bin.cert.Client import Client
from oo_bin.cert.Formatter import Formatter
from oo_bin.utils import SkipArg

# TODO make these thresholds configurable
thresholds = {
    "error": {"days": 2, "opts": {"bg": "red"}},
    "warning": {"days": 7, "opts": {"bg": "yellow"}},
    "info": {"days": 14, "opts": {"fg": "yellow"}},
}


def alertOnHostMismatch(cert, conn) -> bool:
    if cert.host not in cert.subject and cert.host not in cert.altNames:
        # TODO process wildcard domains better...
        click.secho("########## PROBLEM ##########", fg="red")
        click.secho(
            " Host did not match CN nor was it in the subject alternative names",
            fg="red",
        )
        click.echo(
            Formatter.certificateToTable(
                {
                    "subject": "Subject",
                    "altNames": ("Alternative Names", Formatter.altNames),
                },
                cert,
                conn,
            )
        )
        click.secho("########## PROBLEM ##########", fg="red")
        return True
    return False


@click.group(
    cls=SkipArg, invoke_without_command=True, help="SSL Certificate Information"
)
@click.pass_context
@click.argument("host", required=False)
@click.argument("port", required=False, default=443)
@click.option("--starttls", default="auto")
def cert(ctx, host, port, starttls):
    if not host and not ctx.invoked_subcommand:
        click.echo(click.get_current_context().get_help())
        return

    if ctx.invoked_subcommand is None:
        ctx.forward(check)


@cert.command("check", help="Check certificate validity")
@click.argument("host")
@click.argument("port", required=False, default=443)
@click.option("--starttls", default="auto")
def check(host: str, port: int | None, starttls: str = "auto") -> None:
    cert, conn = Client.make(host, port, starttls).scan()

    def warning(**kwargs) -> str:
        click.secho("########## WARNING ##########", **kwargs)
        click.echo(f" Expires on {cert.validUntil} ({cert.expiresIn} days)")
        click.secho("########## WARNING ##########", **kwargs)

    expiresOn = f" Expires on {cert.validUntil} ({cert.expiresIn} days)"
    status = cert.status(thresholds)

    if status == "expired":
        click.secho("########## EXPIRED ##########", bg="red")
        click.secho(expiresOn, fg="red")
        click.secho("########## EXPIRED ##########", bg="red")
    elif status == "ok":
        click.echo(click.style("OK", fg="green") + f"{expiresOn}")
    else:
        warning(**thresholds[status]["opts"])


@cert.command("details")
@click.argument("host")
@click.argument("port", required=False, default=443)
@click.option("--starttls", default="auto")
def details(host: str, port: int | None, starttls: str = "auto") -> None:
    """Display the details for the certificate"""
    fields = {
        "subject": ("Subject", Formatter.subject),
        "commonNames": "Common Names",
        "altNames": ("Alternative Names", Formatter.altNames),
        "serialNumber": "Serial Number",
        "validFrom": "Valid From",
        "validUntil": ("Valid Until", Formatter.validUntil),
        # key
        # weak key (Debian)
        "issuer": "Issuer",
        "sigAlg": "Signature Algorithm",
        "sha256Hash": "Fingerprint SHA256",
        "pinSha256": "Pin SHA256",
        # 'extendedValidation': 'Extended Validation',
        # 'transparency': 'Certificate Transparency',
        # 'ocspStaple': 'OCSP Must Staple',
        # 'revokeInfo': 'Revocation Information',
        # 'revokeStatus': 'Revocation Status',
        "dnsCaa": ("DNS CAA", Formatter.dnsCaa),
    }

    cert, conn = Client.make(host, port, starttls).scan()
    if alertOnHostMismatch(cert, conn):
        return
    msg = None
    style = {}
    status = cert.status(thresholds)

    if status == "expired":
        msg = "EXPIRED"
        style["bg"] = "red"
    elif status == "ok":
        pass
    else:
        style = thresholds[status]["opts"]
        msg = "WARNING"
    Formatter.thresholds = thresholds

    info = Formatter.certificateToTable(fields, cert, conn)
    output = str(info)

    if msg:
        msg = "{0:#^{1}}".format(
            f"{msg:^{len(msg) + 2}}", reduce(lambda a, b: a + b, info._widths) + 4
        )
    msg and click.secho(msg, **style)
    click.echo(output)
    msg and click.secho(msg, **style)
