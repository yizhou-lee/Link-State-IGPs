# Link-State-IGPs
a simple analyser of IGP messages, focusing on a specific link-state IGP called OSPF.
## ospf-analyser.py
parses the content of cw2-stage1-trace.pcap, and reconstructs the OSPF network graph from it.
## path-analyser.py
checks the consistency of input paths and traceroute logs with an OSPF network graph
## convergence-analyser.py
checks whether an input failure can trigger forwarding loops during OSPF convergence.
