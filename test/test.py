#!/usr/bin/python3
import signal
import libvirt
import time
import os
import sys
from prettytable import PrettyTable
from xml.etree import ElementTree

"""将bytes数转换成更加直观的符号显示"""


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


# TODO: 怎么能判断出所有虚拟机所拥有的磁盘，每个磁盘添加一列呢？
def DomainDiskUsage(domain: libvirt.virDomain):
    # 开始计算磁盘I/O
    tree = ElementTree.fromstring(domain.XMLDesc())
    devices = tree.findall("devices/disk/target")

    for d in devices:
        domainBlockDevice = d.get("dev")
        # domainBlockDevice = "vda"
        try:
            # 这个逻辑可能会获取到错误信息，并由 libvirt 库直接写到 shell 中，通过 `python3 kvm.py 2> /dev/null` 即可忽略错误信息
            capacity, allocation, _ = domain.blockInfo(domainBlockDevice)
            print(
                "虚拟机 {} 的磁盘设备 {} 总容量 {},分配了 {}".format(
                    "\033[0;37;44m{}\033[0m".format(domain.name()),
                    domainBlockDevice,
                    bytes2symbols(capacity),
                    bytes2symbols(allocation),
                )
            )
        except Exception as err:
            continue


def get():
    # conn = libvirt.open("test:///default")
    # conn = libvirt.open("qemu:///system")
    # conn = libvirt.open("qemu+ssh://root@172.38.180.96/system")
    conn = libvirt.open("qemu+tcp://172.38.180.95/system")

    domain = conn.lookupByName("tj-test-spst-k3s-node-1")
    print(domain.info()[2])

    # virsh desc DOMAIN 获取虚拟机描述
    desc = domain.metadata(libvirt.VIR_DOMAIN_METADATA_DESCRIPTION, None)
    print(desc)

    # 获取节点上的硬件信息。CPU架构、内存大小、CPU数量、CPU 频率、NUMA 节点数量、每个节点的 CPU 数量、每个插槽的核心数、每个核心的线程数
    mem = conn.getInfo()[1]
    cpu = conn.getInfo()[2]
    print(mem, cpu)

    # for id in conn.listDomainsID():
    #     domain = conn.lookupByID(id)

    #     domainName = "\033[0;37;44m{}\033[0m".format(domain.name())
    #     domainStat = (
    #         "\033[0;37;42m%s\033[0m" % "开机"
    #         if domain.info()[0] == 1
    #         else "\033[0;37;41m%s\033[0m" % "关机"
    #     )
    #     domainMem = str(domain.info()[1] / 1024 / 1024) + "GiB"
    #     domainCPU = str(domain.info()[3])
    #     domainMemUsage = str(DomainMemUsage(domain)) + "%"
    #     domainCpuUsage = str(DomainCpuUsage(domain)) + "%"

    #     print(
    #         domainName,
    #         domainStat,
    #         domainCPU,
    #         domainCpuUsage,
    #         domainMem,
    #         domainMemUsage,
    #     )

    conn.close()


if __name__ == "__main__":
    get()
