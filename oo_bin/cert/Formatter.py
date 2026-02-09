import click
from prettytable import PrettyTable


class Formatter:
    thresholds = {}

    @staticmethod
    def altNames(names, cert, conn):
        # TODO it'd be nice to multi-line this based on the size of the console...
        if type(names) == str:
            return names

        try:
            sub = PrettyTable(header=False, border=False)
            sub.field_names = ["v1", "v2"]
            sub.align["v1"] = "l"
            sub.align["v2"] = "l"
            for idx in range(0, len(names), 2):
                row = names[idx : idx + 2]
                if len(row) != 2:
                    row.append("")
                for id, val in enumerate(row):
                    if cert.host == val:
                        row[id] = click.style(f" {val} ", bg="green", fg="black")
                sub.add_row(row)
            return sub.get_string()
        except Exception:
            pass
        return ""

    @staticmethod
    def certificateToTable(fields, certificate, connection) -> PrettyTable:
        table = PrettyTable(border=False)
        table.field_names = ["key", "value"]
        table.align["key"] = "r"
        table.align["value"] = "l"
        table.header = False
        for field in fields:
            value = getattr(certificate, field)
            if value is None or (type(value) is list and not len(value)):
                continue
            display = fields[field]
            render = Formatter.echo
            if type(display) is tuple:
                display, render = fields[field]
            table.add_row([display, render(value, certificate, connection)])

        return table

    @staticmethod
    def dnsCaa(value, cert, conn):
        if value:
            return click.style("Yes", fg="green")
        else:
            return click.style("NO", fg="yellow")

    @staticmethod
    def echo(value, cert, conn):
        return value

    @staticmethod
    def subject(cn, cert, conn):
        if cert.host in cn:
            return click.style(f" {cn} ", bg="green", fg="black")
        else:
            cn = click.style(cn, bg="yellow")
            return f"{cn} (does not match {cert.host})"

    @staticmethod
    def validUntil(value, cert, conn):
        days = f"{cert.expiresIn} days"
        status = cert.status(Formatter.thresholds)
        opts = None
        if status == "expired":
            opts = {"bg": "red"}
        elif status != "ok":
            opts = Formatter.thresholds[status]["opts"]
        if opts:
            days = click.style(days, **opts)

        return f"{value} ({days})"
