import libvirt
from prettytable import PrettyTable


def listSnapshots(conn: libvirt.virConnect):
    table = PrettyTable(["实例", "快照"])

    for id in conn.listDomainsID():
        domain = conn.lookupByID(id)
        for snapshot in domain.listAllSnapshots():
            table.add_row([domain.name(), snapshot.getName()])

    print(table)


if __name__ == "__main__":
    conn = libvirt.open("qemu+tcp://172.38.180.95/system")
    listSnapshots(conn)
