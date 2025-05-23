#! /usr/bin/python3
import time
import random
import argparse

from scapy.layers.inet import IP, UDP
from scapy.layers.http import HTTPRequest, HTTP
from scapy.layers.l2 import Ether
from scapy.utils import wrpcap

SRC_MAC = "6C:B3:11:50:D3:DA"
DST_MAC = "3C:FD:FE:EC:48:11"

"""
This script generate both the ACL file and synthetic flow stored in *.pcap
./firewall -h
"""

"""
firewall rules(ACL rules) similar to POM paper
"""


def generate_random_str(randomlength=16):
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length = len(base_str) - 1
    for i in range(randomlength):
        random_str += base_str[random.randint(0, length)]
    return random_str


def generate_fw_rules(filename, src_ips, dst_ips):
    random.shuffle(dst_ips)
    with open(filename, "w") as f:
        for ip in dst_ips:
            f.write(ip+"/32\n")


def get_ip_list(flow_size):
    if flow_size > 40000:
        raise Exception("Too many flow")
    src_ip_prefix = "10.1."
    dst_ip_prefix = "10.2."
    cnt = 0
    src_ips = []
    dst_ips = []
    while cnt < flow_size:
        for i in range(2, 202):
            for j in range(3, 203):
                src = src_ip_prefix+str(i)+"."+str(j)
                dst = dst_ip_prefix+str(i)+"."+str(j)
                src_ips.append(src)
                dst_ips.append(dst)
                cnt += 1
                if cnt == flow_size:
                    break
            if cnt == flow_size:
                break

    return (src_ips, dst_ips)


def get_random_ip_list(flow_size):
    src_ip_list = []
    dst_ip_list = []
    for i in range(flow_size):
        done = False
        while not done:
            a = random.randrange(1, 255)
            b = random.randrange(1, 255)
            c = random.randrange(1, 255)
            d = random.randrange(1, 255)
            ip = str(a)+"."+str(b)+"."+str(c)+"."+str(d)
            if not dst_ip_list.__contains__(ip):
                dst_ip_list.append(ip)
                done = True
        done = False
        while not done:
            a = random.randrange(1, 255)
            b = random.randrange(1, 255)
            c = random.randrange(1, 255)
            d = random.randrange(1, 255)
            ip = str(a)+"."+str(b)+"."+str(c)+"."+str(d)
            if not dst_ip_list.__contains__(ip) and not src_ip_list.__contains__(ip):
                src_ip_list.append(ip)
                done = True
    assert (len(src_ip_list) == len(dst_ip_list))
    return (src_ip_list, dst_ip_list)


def generate_packets(args):
    cnt = 0
    total_size = args.flow_num * args.slf
    pkt_list = [None] * total_size
    flows_list = [None] * args.flow_num
    src_ips, dst_ips = get_random_ip_list(args.flow_num)
    generate_fw_rules("fw"+str(args.flow_num)+".rules", src_ips, dst_ips)

    for flow_idx in range(args.flow_num):
        src_ip = src_ips[flow_idx]
        dst_ip = dst_ips[flow_idx]
        src_port = random.randint(1024, 65535)
        dst_port = random.randint(1024, 65535)
        eth = Ether(src=SRC_MAC, dst=DST_MAC)
        ip = IP(src=src_ip, dst=dst_ip)
        udp = UDP(sport=src_port, dport=dst_port)
        http = HTTP()
        httpreq = HTTPRequest()
        # It may not be realistic for HTTP over UDP, but it's a synthetic test and
        # we use it anyway.
        pkt = eth / ip / udp / http / httpreq
        flows_list[flow_idx] = pkt
    print("Setup all the flows")
    for flow_idx in range(args.flow_num):
        # src_ip, dst_ip, src_port, dst_port = flows_list[flow_idx]
        for i in range(args.slf):
            # pkt_size = random.randint(200, 300)
            pkt_list[cnt] = flows_list[flow_idx]
            cnt += 1
    return pkt_list


def store_packets_to_pcap_file(args, packets_list):
    print("Store the generated packets to synthetic_packets.pcap")
    print(f"Total packets: {len(packets_list)}")
    filename = f"synthetic_slf{args.slf}_flow_num{args.flow_num}_seed{args.seed}.pcap"
    wrpcap(filename, packets_list)
    print("Done!")


"""
Make sure you have installed scapy: pip install scapy
To view the parameter, please run the following command:
./generate_synthetic_flow.py -h 
"""
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--slf", help="spacial locality factor(SLF)", type=int, default=1)
    parser.add_argument(
        "--flow-num", help="total number of flow", type=int, default=100000)
    parser.add_argument(
        "--seed", help="seed for generating random number", type=int, default=42)
    args = parser.parse_args()
    # For reproducible experiments
    random.seed(args.seed)
    start_time = time.time_ns()
    packets = generate_packets(args=args)
    store_packets_to_pcap_file(args, packets)
    end_time = time.time_ns()
    print(f"Total time: {(end_time - start_time) / 1000 / 1000} ms")
