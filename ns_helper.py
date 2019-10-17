##########################################
# Note: This script should be run as root
##########################################

import os
import subprocess

# TODO: This module needs to be tested; each function should be seperately tested

def exec_subprocess(cmd, block = True):
	temp = subprocess.Popen(cmd.split())
	if block:
		temp.communicate()
	else:
		pass

############################################
# CONVENTION: In parameter list, namespace 
# names come before interface names.
############################################

def create_ns(ns_name):
    """
    Create namespace with name `ns_name`
    if it doesn't already exist
    """
    # TODO: Check if the ns_name already exists
    exec_subprocess('ip netns add ' + ns_name)

def delete_ns(ns_name):
    """
    Drops the namespace with name `ns_name`
    if it already exists.
    """
    exec_subprocess('ip nets drop ' + ns_name)

def en_ip_forwarding(ns_name):
    """
    Enables ip forwarding in the namespace 
    `ns_name`. Used for routers
    """
    exec_subprocess('ip netns exec ' + ns_name + ' sysctl -w net.ipv4.ip_forward=1 > /dev/null')

def create_veth(int_name1, int_name2):
    """
    Create a veth interfaces with endpoints
    `int_name1` and `int_name2`
    """
    exec_subprocess('ip link add ' + int_name1 +' type veth peer name ' + int_name2)

def add_int2ns(ns_name, int_name):
    """
    Add interface `int_name` to namespace `ns_name`
    """
    exec_subprocess('ip link set ' + int_name + ' netns ' + ns_name)

def set_int_up(ns_name, int_name):
    """
    Set interface `int_name` in namespace `ns_name` to up
    """
    exec_subprocess('ip netns exec ' + ns_name + ' ip link set dev ' + int_name + ' up')

# Use this function for `high level convinience`
def setup_veth(ns_name1, ns_name2, int_name1, int_name2):
    """
    Sets up veth connection with interafaces `int_name1` and
    `int_name2` associated with namespaces `ns_name1` and 
    `ns_name2` respectively. The interfaces are set up as well.
    """
    create_veth(int_name1, int_name2)
    add_int2ns(ns_name1, int_name1)
    add_int2ns(ns_name2, int_name2)
    set_int_up(ns_name1, int_name1)
    set_int_up(ns_name2, int_name2)

def create_peer(peer_name):
    """
    Creates a peer with the name `peer_name` and adds it to 
    the existing topology.
    """
    create_ns(peer_name)

def create_router(peer_name):
    """
    Creates a peer with the name `peer_name` and adds it to 
    the existing topology.
    """
    create_ns(peer_name)
    en_ip_forwarding(peer_name)

def connect(peer_name=None, router_name1=None, router_name2=None):
    """
    Connects two namespaces(a peer with a router or two routers) and
    returns the created interface names
    """
    if(peer_name):
        peer_int = peer_name + '-' + router_name1
        router_int = router_name1 + '-' + peer_name
        setup_veth(peer_name, router_name1, peer_int, router_int)
        return (peer_int, router_int)
    else:
        router1_int = router_name1 + '-' + router_name2
        router2_int = router_name2 + '-' + router_name1
        setup_veth(router_name1, router_name2, router1_int, router2_int)
        return (router1_int, router2_int)

def assign_ip(host_name, int_name, ip_address):
    """
    Assigns ip address `ip_address` to interface
    `int_name` in host `host_name`.
    """
    #TODO: Support for ipv6
    exec_subprocess('ip netns exec ' + host_name + ' ip address add ' + ip_address + ' dev ' + int_name)
    

#TODO: Assigning ip addresses to interfaces and routing

if __name__ == '__main__':
    n1 = 'red'
    n2 = 'blue'
    n3 = 'green'
    n4 = 'pink'
    # create_ns(n1)
    # create_ns(n2)
    # setup_veth(n1, n2, i1, i2)
    create_peer(n3)
    create_router(n4)
    (int1, int2) = connect(peer_name=n3, router_name1=n4)
    assign_ip(n3, int1, '10.0.1.1/24')
