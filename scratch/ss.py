#!/usr/bin/python3

import subprocess
import os
import sys
import time
import matplotlib.pyplot as plt

#PERIOD  = 0.1 # in seconds
#COUNT   = 100

def get_param(host):
    """
    returns rtt and cwnd
    ip:   host ip (I think)
    port: host port
    """

    # ss -i dst 172.217.26.238:https

    cmd = "ss"
    args = "-i"
    host = "dst "+host

    temp = subprocess.Popen([cmd, args, host], stdout = subprocess.PIPE)
    output = str(temp.communicate())
    
    output = output.split("\n")
    # print(output[0])
    output = output[0].split("\\")

    if(len(output) < 3):
        return ["null", "null"]

    parameters = {}

    for p in output[3].split():
        parameters[p.split(":")[0]] = p

    # parameters = output[3].split(" ")

    return [parameters["rtt"], parameters["cwnd"]]

def plot_param(host, PERIOD = 0.1, COUNT = 100, OUTPUT = "output.png"):
    """
    plots cwnd and rtt into OUTPUT file
    host  : host ip
    PERIOD: Time between each measurement in seconds
    COUNT : Number of measurements
    OUTPUT: Output file for the plot
    """
    TIME = 0
    RTTs = []
    CWNDs = []
    TIMEs = []

    # host = sys.argv[1]

    for i in range(COUNT):
        # if(i/COUNT > 0.1):
        #     host = '172.217.167.142'
        # else:
        #     continue
        param = get_param(host)
        # print(i)
        # for p in param:
        #     print(p)
        # print()

        try:
            rtt = float(param[0][4:].split("/")[0])
            cwnd = float(param[1][5:])
            RTTs.append(rtt)
            CWNDs.append(cwnd)

        except:
            RTTs.append(0)
            CWNDs.append(0)

        TIMEs.append(TIME)
        TIME += PERIOD
        time.sleep(PERIOD)


    # TODO: Nicer plot output
    plt.subplot(211)
    plt.plot(TIMEs, RTTs)
    # plt.show()

    plt.subplot(212)
    plt.plot(TIMEs, CWNDs)
    #plt.show()
    plt.savefig(OUTPUT)


