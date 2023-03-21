#! /usr/bin/python3

import sys
import networkx as nx

if len(sys.argv) > 1:
    lsdb_file = sys.argv[1]
    test_link_id = sys.argv[2]
    des_ip = sys.argv[3]

G_old = nx.MultiDiGraph()
G_new = nx.MultiDiGraph()
routing_table = dict()
stub_table = dict()
loop_routers = []

# read data from lsdb file
with open(lsdb_file) as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 3:
            link_id, metric, routers = parts
            router1, router2 = routers.split('-')
            G_old.add_weighted_edges_from(
                [(router1, router2, int(metric)), (router2, router1, int(metric))])
            routing_table[link_id] = {router1, router2}
            if link_id != test_link_id:
                G_new.add_weighted_edges_from(
                    [(router1, router2, int(metric)), (router2, router1, int(metric))])
        if len(parts) == 4 and parts[0] != "Link":
            stub_id, netmask, metric, ad_router = parts
            stub_table[stub_id] = ad_router

# check the path difference
target_router = stub_table.get(des_ip)
all_routers = list(set(list(stub_table.values())))
if target_router is None:
    print("OSPF convergence loop: no loop")
else:
    for source_router in all_routers:
        if source_router != target_router:
            shortest_paths_old = list(nx.all_shortest_paths(
                G_old, source_router, target_router, weight='weight'))
            shortest_paths_new = list(nx.all_shortest_paths(
                G_new, source_router, target_router, weight='weight'))

            """ 
            Find the longest common elements in these two lists
            """

    if len(loop_routers) == 0:
        print("OSPF convergence loop: no loop")
    else:
        print("OSPF convergence loop: ", loop_routers)
