##########################################
# Note: This script should be run as root
##########################################

import os
import subprocess
import argparse
import threading
import time

def exec_subprocess(cmd, block = True):
	temp = subprocess.Popen(cmd.split())
	if block:
		temp.communicate()
	else:
		pass

# ns: namespace
def server(ns):
    #run a iperf server for 10s
    exec_subprocess("ip netns exec " + ns + " iperf -s -t 10")

def client(ns):
    # TODO: Remove server IP dependency
    #run a iperf client for 10s running 4 processes in parallel
    exec_subprocess("ip netns exec " + ns + " iperf -c 10.0.0.2 -t 10 -P 4")

def get_param(ns):
    exec_subprocess("ip netns exec " + ns + " ./ss.py 10.0.0.2")

# Default Network Namespaces
n1 = "n1"
n2 = "n2"

# Parse Arguements
cmdParser = argparse.ArgumentParser()
cmdParser.add_argument('names', type=str, nargs=2)
args = cmdParser.parse_args()
n1 = args.names[0]
n2 = args.names[1]

# Add Network Namespace
# TODO: Check if the namespace already exists
exec_subprocess("ip netns add " + n1)
exec_subprocess("ip netns add " + n2)

# Setup virtual ethernet devices (veth)
exec_subprocess("ip link add eth-n1 type veth peer name eth-n2")
exec_subprocess("ip link set eth-n1 netns " + n1)
exec_subprocess("ip link set eth-n2 netns " + n2)

# Configure the ethernet devices
exec_subprocess("ip netns exec " + n1 + " ip link set dev lo up")
exec_subprocess("ip netns exec " + n1 + " ip link set dev eth-n1 up")
exec_subprocess("ip netns exec " + n1 + " ip address add 10.0.0.1/24 dev eth-n1")

exec_subprocess("ip netns exec " + n2 + " ip link set dev lo up")
exec_subprocess("ip netns exec " + n2 + " ip link set dev eth-n2 up")
exec_subprocess("ip netns exec " + n2 + " ip address add 10.0.0.2/24 dev eth-n2")

# Run server and client application
t1 = threading.Thread(target=server, args=(n2, ))
t2 = threading.Thread(target=client, args=(n1, ))
t3 = threading.Thread(target=get_param, args=(n1, ))

t1.start()
time.sleep(2.0) # to ensure that telnet runs after server is established
t2.start()
t3.start()

t1.join()
t2.join()
t3.join()

# exec_subprocess("ip netns exec " + n2 + " python3 server.py")
# exec_subprocess("ip netns exec " + n1 + " telnet 10.0.0.2 1025")
# exec_subprocess("ip netns exec " + n1 + " python3 client.py", block=False)

# Delete created Network Namespaces
exec_subprocess("ip netns del " + n1)
exec_subprocess("ip netns del " + n2)
