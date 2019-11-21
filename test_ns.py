import ns_helper as ns

#######################
# Topology
#
# n1 ----- n2 ----- n3  
#######################


def run():

    # Cleanup previously created namespaces
    ns.delete_ns("n1")
    ns.delete_ns("n2")
    ns.delete_ns("n3")

    # Create peer and routers
    ns.create_peer("n1")
    ns.create_router("n2")
    ns.create_peer("n3")

    # Connect n1 and n2; assign IPs to interfaces in same subnet
    (eth_n1_n2, eth_n2_n1) = ns.connect("n1","n2")
    ns.assign_ip("n1", eth_n1_n2, '10.1.1.1/24')
    ns.assign_ip("n2", eth_n2_n1, '10.1.1.2/24')
                                
    # Connect n2 and n3; assign IPs to interfaces in the same subnet
    (eth_n2_n3, eth_n3_n2) = ns.connect("n2","n3")
    ns.assign_ip("n2", eth_n2_n3, '10.2.2.1/24')
    ns.assign_ip("n3", eth_n3_n2, '10.2.2.2/24')

    # Add route from n1 to n3, n3 to n1
    ns.add_route("n1", "10.2.2.2", "10.1.1.2", eth_n1_n2)
    ns.add_route("n3", "10.1.1.1", "10.2.2.1", eth_n3_n2)


if __name__ == "__main__":
    run()