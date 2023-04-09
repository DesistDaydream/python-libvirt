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


def DomainMonitoring(conn: libvirt.virConnect, table: PrettyTable):
    try:
        for id in conn.listDomainsID():
            domain = conn.lookupByID(id)

            domainName = "\033[0;37;44m{}\033[0m".format(domain.name())
            domainStat = (
                "\033[0;37;42m%s\033[0m" % "开机"
                if domain.info()[0] == 1
                else "\033[0;37;41m%s\033[0m" % "关机"
            )
            domainMem = str(domain.info()[1] / 1024 / 1024) + "GiB"
            domainCPU = str(domain.info()[3])
            domainMemUsage = str(DomainMemUsage(domain)) + "%"
            domainCpuUsage = str(DomainCpuUsage(domain)) + "%"

            DomainDiskUsage(domain)

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
    except:
        pass


def my_handler(signum, frame):
    global stop
    stop = True
    print("进程被终止")


# 设置相应信号处理的handler
signal.signal(signal.SIGINT, my_handler)
signal.signal(signal.SIGHUP, my_handler)
signal.signal(signal.SIGTERM, my_handler)

stop = False


def main():
    os.system("clear")
    print(
        '''
    *********************************************
                    _ooOoo_
                    o8888888o
                    88" . "88
                    (| -_- |)
                    O\  =  /O
                ____/`---"\____
                ."  \\|     |//  `.
                /  \\|||  :  |||//  \\
            /  _||||| -:- |||||-  \\
            |   | \\\  -  /// |   |
            | \_|  ""\---/""  |   |
            \  .-\__  `-`  ___/-. /
            ___`. ."  /--.--\  `. . __
        ."" "<  `.___\_<|>_/___."  >""".
        | |:  `- \`.; `\ _ /`; .`/ - `: | |
        \  \ `-.   \_ __\ / __ _ / .-` / /
    == == ==`-.____`- .___\_____/___.-`____.-"== == ==                    `=-- -="
    ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^
            佛祖保佑       永不宕机'''
    )
    print(
        "\033[0;37;41m{}\033[0m".format(
            "######################     实时监控kvm虚拟机信息--CPU,内存,磁盘I/O    ##################"
        )
    )
    print("Ctrl+C 可退出程序,脚本每6秒执行一次")

    conn = libvirt.open("qemu:///system")

    if len(conn.listDomainsID()) <= 0:
        print("\033[0;37;41m{}\033[0m".format("没有正在运行的虚拟机，程序退出."))
        os.system("command")
        time.sleep(1)
        sys.exit()

    table = PrettyTable(["实例名", "状态", "CPU", "CPU使用率", "内存", "内存使用率"])

    DomainMonitoring(conn, table)

    print(table)

    conn.close()

    time.sleep(6)


while True:
    try:
        if stop:
            break
    except:
        pass

    main()
