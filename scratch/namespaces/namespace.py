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
	
n1 = "n1"
n2 = "n2"
cmdParser = argparse.ArgumentParser()
cmdParser.add_argument('names', type=str, nargs=2)
args = cmdParser.parse_args()
n1 = args.names[0]
n2 = args.names[1]
exec_subprocess("ip netns add " + n1)
exec_subprocess("ip netns add " + n2)

exec_subprocess("ip link add eth-n1 type veth peer name eth-n2")

print('j')

exec_subprocess("ip link set eth-n1 netns " + n1)
exec_subprocess("ip link set eth-n2 netns " + n2)

print('i')

exec_subprocess("ip netns exec " + n1 + " ip link set dev lo up")
exec_subprocess("ip netns exec " + n1 + " ip link set dev eth-n1 up")
exec_subprocess("ip netns exec " + n1 + " ip address add 10.0.0.1/24 dev eth-n1")

exec_subprocess("ip netns exec " + n2 + " ip link set dev lo up")
exec_subprocess("ip netns exec " + n2 + " ip link set dev eth-n2 up")
exec_subprocess("ip netns exec " + n2 + " ip address add 10.0.0.2/24 dev eth-n2")

t1 = threading.Thread(target=exec_subprocess, args=("ip netns exec " + n2 + " python3 server.py", )) 
t2 = threading.Thread(target=exec_subprocess, args=("ip netns exec " + n1 + " telnet 10.0.0.2 1025", ))

t1.start()
time.sleep(2.0)
t2.start()

t1.join()
t2.join()

# exec_subprocess("ip netns exec " + n2 + " python3 server.py")
# exec_subprocess("ip netns exec " + n1 + " telnet 10.0.0.2 1025")
# exec_subprocess("ip netns exec " + n1 + " python3 client.py", block=False)

exec_subprocess("ip netns del " + n1)
exec_subprocess("ip netns del " + n2)


