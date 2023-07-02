import click
import libvirt
from snapshot_list import listSnapshots
from domain_list import listDomains


@click.group()
def cli():
    pass


@cli.group()
def domain():
    pass


@domain.command()
def create():  # type: ignore
    click.echo("Creating a domain")


@domain.command()
def list():  # type: ignore
    ips = ["172.38.180.95", "172.38.180.96", "172.38.180.97"]
    for ip in ips:
        conn = libvirt.open("qemu+tcp://{}/system".format(ip))
        listDomains(conn)
        conn.close()


@cli.group()
def snapshot():
    pass


@snapshot.command()
def create():
    click.echo("This is the snapshot create command")


@snapshot.command()
def list():
    ips = ["172.38.180.95", "172.38.180.96", "172.38.180.97"]
    for ip in ips:
        conn = libvirt.open("qemu+tcp://{}/system".format(ip))
        listSnapshots(conn)
        conn.close()


if __name__ == "__main__":
    cli()
