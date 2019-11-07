##########################################
# Note: This script should be run as root
##########################################

import os
import subprocess
import argparse
import threading
import time


def exec_subprocess(cmd, block=True):
    temp = subprocess.Popen(cmd.split())
    if block:
        temp.communicate()
    else:
        pass

# ns: namespace


def server(ns):
    # run netserver
    exec_subprocess('ip netns exec ' + ns + ' netserver')


def client(ns):
    # TODO: Remove server IP dependency
    # run flent
    exec_subprocess('ip netns exec ' + ns +
                    ' flent tcp_download -H 10.1.2.2 -p tcp_cwnd --socket-stats -o cwnd.png')


# Default Network Namespaces
n1 = 'n1'
n2 = 'n2'
router = 'router'

# Parse Arguements
cmdParser = argparse.ArgumentParser()
cmdParser.add_argument('names', type=str, nargs=2)
args = cmdParser.parse_args()
n1 = args.names[0]
n2 = args.names[1]

# Add Network Namespace
# TODO: Check if the namespace already exists
exec_subprocess('ip netns add ' + n1)
exec_subprocess('ip netns add ' + n2)
exec_subprocess('ip netns add ' + router)

# Setup virtual ethernet devices (veth)
exec_subprocess('ip link add eth-n1 type veth peer name eth-r1')
exec_subprocess('ip link add eth-r2 type veth peer name eth-n2')
exec_subprocess('ip link set eth-n1 netns ' + n1)
exec_subprocess('ip link set eth-r1 netns ' + router)
exec_subprocess('ip link set eth-r2 netns ' + router)
exec_subprocess('ip link set eth-n2 netns ' + n2)

# Configure the ethernet devices
exec_subprocess('ip netns exec ' + n1 + ' ip link set dev lo up')
exec_subprocess('ip netns exec ' + n1 + ' ip link set dev eth-n1 up')
exec_subprocess('ip netns exec ' + n1 +
                ' ip address add 10.1.1.1/24 dev eth-n1')

exec_subprocess('ip netns exec ' + router + ' ip link set dev eth-r1 up')
exec_subprocess('ip netns exec ' + router + ' ip link set dev eth-r2 up')
exec_subprocess('ip netns exec ' + router +
                ' ip address add 10.1.1.2/24 dev eth-r1')
exec_subprocess('ip netns exec ' + router +
                ' ip address add 10.1.2.1/24 dev eth-r2')

exec_subprocess('ip netns exec ' + n2 + ' ip link set dev lo up')
exec_subprocess('ip netns exec ' + n2 + ' ip link set dev eth-n2 up')
exec_subprocess('ip netns exec ' + n2 +
                ' ip address add 10.1.2.2/24 dev eth-n2')

# Configure routing
exec_subprocess('ip netns exec ' + n1 +
                ' ip route add 10.1.2.0/24 dev eth-n1 via 10.1.1.2')
exec_subprocess('ip netns exec ' + router +
                ' ip route add 10.1.1.0/24 dev eth-r1 via 10.1.1.1')
exec_subprocess('ip netns exec ' + router +
                ' ip route add 10.1.2.0/24 dev eth-r2 via 10.1.2.2')
exec_subprocess('ip netns exec ' + n2 +
                ' ip route add 10.1.1.0/24 dev eth-n2 via 10.1.2.1')

# Run server and client application
t1 = threading.Thread(target=server, args=(n2, ))
t2 = threading.Thread(target=client, args=(n1, ))

t1.start()
time.sleep(2.0)  # to ensure that flent runs after server is established
t2.start()

t1.join()
t2.join()

# Delete created Network Namespaces and veth pairs
exec_subprocess('ip netns exec ' + n1 + ' ip link del eth-n1')
exec_subprocess('ip netns exec ' + router + ' ip link del eth-r1')
exec_subprocess('ip netns exec ' + router + ' ip link del eth-r2')
exec_subprocess('ip netns exec ' + n2 + ' ip link del eth-n2')
exec_subprocess('ip netns del ' + n1)
exec_subprocess('ip netns del ' + n2)
exec_subprocess('ip netns del ' + router)
