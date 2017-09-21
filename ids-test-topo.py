#!/usr/bin/python

import os
import glob
import argparse
import sys
from itertools import combinations
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.node import RemoteController
from mininet.log import setLogLevel

#Setup arguments
parser = argparse.ArgumentParser(description='Generates n number of hosts to simulate normal and anomalous attack behaviors')
parser.add_argument('-n', '--hosts', dest='hosts', default=3, type=int, 
                    help='Generates an n number of attack hosts based on the quantity specified (default: 3 hosts')
parser.add_argument('-r', '--ratio', dest='ratio', default=0.1, type=int,
                    help='Anomalous to normal hosts ratio. Generates normal traffic hosts based on ratio specified')
parser.add_argument('-t', '--test', dest='test', default='all', type=str,
                    help='Specify tests (Defaults to all)')
args = parser.parse_args()

net = Mininet(controller=RemoteController, link=TCLink)

h = list()

#Generate hosts
def create_test_netowrk(hosts, ratio):
    total_hosts = int(hosts + (hosts * ((1 - ratio) * 10)))

    for i in range(0, total_hosts):
        h.append(net.addHost('test-h' + str(i)))

#Run specified test (Defaults to: all tests)
def exec_test_cases(test, directory='test-cases'):
    test_path = os.path.join(os.path.dirname, directory)

    test_files = [f for f in listdir(test_path) if isfile(join(mypath, f))]
    
    for test_file in test_files:
        name = os.path.splitext(os.path.basename(test_file))[0]
        module = __import__(name)
        


setLogLevel('info')
create_test_netowrk(args.hosts, args.ratio)
run_tests(args.test)

net.start()

CLI(net)
net.stop()
