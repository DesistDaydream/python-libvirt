#!/usr/bin/env python3
from ast import For
import sys
import libvirt
from xml.etree import ElementTree

domName = "Fedora22-x86_64-1"

conn = None
try:
    conn = libvirt.open("qemu:///system")
except libvirt.libvirtError as e:
    print(repr(e), file=sys.stderr)
    exit(1)

dom = conn.lookupByID(38)
if dom == None:
    print("Failed to find the domain " + domName, file=sys.stderr)
    exit(1)

blockStatsFormat = "\
状态信息: \n\
  设备名称: {}\
  读请求: {} 次\n\
  读大小: {} Bytes\n\
  写请求: {} 次\n\
  写大小: {} Bytes \
"

blockInfoFormat = "\
容量信息: \n\
  设备名称: {}\
  总容量: {} 次\n\
  分配容量: {} Bytes\n\
  物理容量: {} 次\
"

tree = ElementTree.fromstring(dom.XMLDesc())
devices = tree.findall("devices/disk/target")
for d in devices:
    device = d.get("dev")

    rd_req, rd_bytes, wr_req, wr_bytes, err = dom.blockStats(device)

    print(blockStatsFormat.format(device, rd_req, rd_bytes, wr_req, wr_bytes, err))

    try:
        capacity, allocation, physical = dom.blockInfo(device)
    except Exception:
        continue
    print(blockInfoFormat.format(device, capacity, allocation, physical))

conn.close()
exit(0)
