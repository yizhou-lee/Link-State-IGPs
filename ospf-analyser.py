#! /usr/bin/python3

import sys
from scapy.all import *
from scapy.contrib.ospf import *

########
# Main #
########

if len(sys.argv) > 1:
    infile = sys.argv[1]
print("\nreading file " + infile)

all_packets = rdpcap(infile)

router_lsa = dict()
network_lsa = dict()
output_link = []
output_stub = []

for p in all_packets:
    # get LSA from LSUpd
    if p.haslayer(OSPF_LSUpd):
        for lsa in p[OSPF_LSUpd].lsalist:
            # check if lsa is a router lsa
            if lsa.type == 1:
                new_router_lsa = {
                    "seq": lsa.seq, "ad_router": lsa.adrouter, "links": lsa.linklist}
                if lsa.id not in router_lsa:
                    router_lsa[lsa.id] = new_router_lsa
                if lsa.id in router_lsa and lsa.seq > router_lsa[lsa.id].get("seq"):
                    router_lsa[lsa.id] = new_router_lsa
            # check if lsa is a network lsa
            if lsa.type == 2:
                new_network_lsa = {"seq": lsa.seq,
                                   "router_list": lsa.routerlist}
                if lsa.id not in network_lsa:
                    network_lsa[lsa.id] = new_network_lsa
                if lsa.id in network_lsa and lsa.seq > network_lsa[lsa.id].get("seq"):
                    network_lsa[lsa.id] = new_network_lsa

# integrate link outputs
for lsa, lsa_info in network_lsa.items():
    link_metric = 0
    for link in router_lsa[lsa_info["router_list"][0]]["links"]:
        if link.id == lsa:
            link_metric = link.metric
    new_link = {"link_id": lsa, "link_metric": link_metric,
                "routers": lsa_info["router_list"][0] + "-" + lsa_info["router_list"][1]}
    output_link.append(new_link)

# integrate stub outputs
for lsa, lsa_info in router_lsa.items():
    for link in lsa_info["links"]:
        # check if the link is a stub link
        if link.type == 3:
            new_stub = {"stub_id": link.id, "netmask": link.data,
                        "metric": link.metric, "ad_router": lsa_info["ad_router"]}
            output_stub.append(new_stub)

# standard output
print("{:<16} {:<11} {:<16}".format("Link ID", "Metric", "Routers"))
for data in output_link:
    print("{:<16} {:<11} {:<16}".format(
        data["link_id"], data["link_metric"], data["routers"]))
print()
print("{:<16} {:<21} {:<11} {:<16}".format(
    "Stub ID", "Netmask", "Metric", "Advertising router"))
for data in output_stub:
    print("{:<16} {:<21} {:<11} {:<16}".format(
        data["stub_id"], data["netmask"], data["metric"], data["ad_router"]))
