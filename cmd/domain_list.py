import libvirt
from prettytable import PrettyTable
import time


def bytes2symbols(bytes_value):
    """单位符号"""
    symbols = ("K", "M", "G", "T", "P", "E", "Z", "Y")

    """每个单位对应的bytes数的字典,先定义为空"""
    prefix = {}

    """要得到这样的{K:1024, M:1024*1024,G:1024**3},进行for循环"""
    for i, s in enumerate(symbols):
        # """enumerate()为列举函数"""
        # """i:代表下标"""
        # """s:代表改下标对应的值"""

        # """取到符号元组的值,作为prfix字典的key,根据key给value进行赋值"""
        prefix[s] = 1024 ** (i + 1)

    # """打印得到的对应字典"""
    # print(prefix)
    symbols_value = 0
    symbol = ""
    # """循环prefix字典,得到转换值"""
    for key, value in prefix.items():
        if bytes_value >= value:
            symbols_value = bytes_value / value
            symbol = key
        # 如果不满足最小的KB,则以B显示
        elif bytes_value < 1024:
            return "%0.2fB" % bytes_value
        # """返回转换值(str)"""
    return "%0.2f%sB" % (symbols_value, symbol)


def DomainMemUsage(domain: libvirt.virDomain):
    domain.setMemoryStatsPeriod(10)
    meminfo = domain.memoryStats()
    free_mem = float(meminfo["unused"])
    total_mem = float(meminfo["available"])
    util_mem = ((total_mem - free_mem) / total_mem) * 100
    return round(util_mem, 2)


def DomainCpuUsage(domain: libvirt.virDomain):
    # 开始计算cpu使用率
    t1 = time.time()
    c1 = int(domain.info()[4])
    time.sleep(0.05)
    t2 = time.time()
    c2 = int(domain.info()[4])
    c_nums = int(domain.info()[3])
    usage = (c2 - c1) * 100 / ((t2 - t1) * c_nums * 1e9)
    return round(usage, 2)


def listDomains(conn: libvirt.virConnect):
    table = PrettyTable(["实例", "状态", "CPU", "CPU使用率", "内存", "内存使用率"])
    table.title = conn.getHostname()

    allMem: int = 0
    allCPU: int = 0

    for id in conn.listDomainsID():
        domain = conn.lookupByID(id)

        domainName = "\033[0;37;44m{}\033[0m".format(domain.name())
        domainStat = (
            "\033[0;37;42m%s\033[0m" % "开机"
            if domain.info()[0] == 1
            else "\033[0;37;41m%s\033[0m" % "关机"
        )
        domainCPU = str(domain.info()[3])
        domainMem = str(domain.info()[2] / 1024 / 1024) + "GiB"
        domainCpuUsage = str(DomainCpuUsage(domain)) + "%"
        domainMemUsage = str(DomainMemUsage(domain)) + "%"

        # DomainDiskUsage(domain)

        table.add_row(
            [
                domainName,
                domainStat,
                domainCPU,
                domainCpuUsage,
                domainMem,
                domainMemUsage,
            ]
        )

        allMem = allMem + (domain.info()[2] / 1024 / 1024)
        allCPU = allCPU + domain.info()[3]

    print(table)
    print("当前服务器共有 {} CPU，已分配给虚拟机 {} CPU".format(conn.getInfo()[2], allCPU))
    print(
        "当前服务器共有 {:.2f} GiB 内存，已分配给虚拟机 {:.2f} GiB 内存".format(
            conn.getInfo()[1] / 1024, allMem
        )
    )


if __name__ == "__main__":
    conn = libvirt.open("qemu+tcp://172.38.180.95/system")
    listDomains(conn)
