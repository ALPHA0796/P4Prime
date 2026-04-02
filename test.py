from scapy.all import sniff, get_if_list
from topo.FatTree6.tools import *
import argparse
import csv

print(get_if_list())

def get_args():
    parser = argparse.ArgumentParser(description='test parser')
    parser.add_argument('--o', help='send common packets', type=bool, action="store", required=False, default=False)   
                        
    return parser.parse_args()

# 用字典存储数据包时间戳
ingress_times = dict()
egress_times = dict()
args = get_args()

def ingress_callback(pkt):
    global args
    t_in = pkt.time
    # pkt.show()
    if not args.o:
        payload = pkt['TAG'].pkt_id
    else:
        payload = pkt['IP'].id
    ingress_times[int(payload)] = t_in
    # print(f"[Ingress] {pkt.summary()} at {t_in} ns")

def egress_callback(pkt):
    t_out = pkt.time
    # pkt.show()
    if not args.o:
        payload = pkt['TAG'].pkt_id
    else:
        payload = pkt['IP'].id
    egress_times[int(payload)] = t_out
    # print(f"[Egress] {pkt.summary()} at {t_out} ns")

def ingress_func():
    sniff(iface='s20-eth1', filter='inbound', prn=lambda x:ingress_callback(x))
def egress_func():
    sniff(iface='s20-eth4', filter='outbound', prn=lambda x:egress_callback(x))

# 开两个抓包线程
import threading

ingress_thread = threading.Thread(target=ingress_func)
egress_thread = threading.Thread(target=egress_func)

ingress_thread.start()
egress_thread.start()

def write_data():
    with open("res.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Packet ID", "Timestamp (ns)"])
        for pkt_id in sorted(set(ingress_times.keys()) & set(egress_times.keys())):
            writer.writerow([pkt_id, egress_times[pkt_id] - ingress_times[pkt_id]])


try:
    ingress_thread.join()
    egress_thread.join()
except KeyboardInterrupt:
    print("Interrupted by user. Exiting.")
    write_data()

