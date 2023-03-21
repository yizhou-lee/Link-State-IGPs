#! /usr/bin/python3

import sys
import networkx as nx

if len(sys.argv) > 1:
    lsdb_file = sys.argv[1]
    paths_file = sys.argv[2]
    traceroutes_file = sys.argv[3]

G = nx.MultiDiGraph()
routing_table = dict()
stub_table = dict()

# read data from lsdb file
with open(lsdb_file) as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 3:
            link_id, metric, routers = parts
            router1, router2 = routers.split('-')
            G.add_weighted_edges_from(
                [(router1, router2, int(metric)), (router2, router1, int(metric))])
            routing_table[link_id] = {router1, router2}
        if len(parts) == 4 and parts[0] != "Link":
            stub_id, netmask, metric, ad_router = parts
            stub_table[stub_id] = ad_router

# check the paths
with open(paths_file) as f:
    for line in f:
        path_correct = "false"
        parts = line.strip().split(":")
        if len(parts) == 2:
            path_id = parts[0]
            path_routers = parts[1].strip().split()
            source_router = path_routers[0]
            target_router = path_routers[-1]
            # calculate the shortest path from source to target
            shortest_paths = list(nx.all_shortest_paths(
                G, source_router, target_router, weight='weight'))
            if path_routers in shortest_paths:
                path_correct = "true"

            print("%s: %s" % (path_id, path_correct))

# check the traceroutes
with open(traceroutes_file) as f:
    traceroutes = f.read().split('\n\n')
    for traceroute in traceroutes:
        lines = traceroute.strip().split('\n')
        # get traceroute and source
        traceroute_id = lines[0].split(": ")[1].strip()
        source = lines[1].split(": ")[1].strip()

        # get all possible router-paths
        last_routers = [source]
        generated_paths = [[source]]

        output_flag = True

        for line in lines[4:]:
            parts = line.strip().split()
            possible_ips = [
                elem for elem in parts if '.' in elem and not elem.endswith('ms')]
            temp_routers = []
            new_routers = []
            updated_routers = []
            for ip in possible_ips:
                ip_prefix = ip[:ip.rfind('.')]
                for key in routing_table:
                    if ip_prefix in key:
                        temp_routers.extend(routing_table[key])
                for key in stub_table:
                    if ip_prefix in key:
                        temp_routers.append(stub_table[key])

            temp_routers = list(set(temp_routers))

            # generate the router path
            for router1 in last_routers:
                for router2 in temp_routers:
                    if {router1, router2} in list(routing_table.values()):
                        new_routers.append(router2)
                        for path in generated_paths:
                            if path[-1] == router1:
                                front_routers = path.copy()
                                front_routers.append(router2)
                                updated_routers.append(front_routers)

            # if there is no matched router in previous routing table
            if len(new_routers) == 0:
                print("%s: false" % traceroute_id)
                output_flag = False
                break

            # update the router path info
            last_routers = new_routers
            generated_paths = updated_routers

        # check the router paths in traceroute
        path_consistence = "true"
        for path in generated_paths:
            # calculate the shortest path from source to target
            shortest_paths = list(nx.all_shortest_paths(
                G, path[0], path[-1], weight='weight'))
            if path not in shortest_paths:
                path_consistence = "false"
                break
        if output_flag:
            print("%s: %s" % (traceroute_id, path_consistence))
