#!/usr/bin/python

import argparse
import sys
from mininet.net import Mininet
from mininet.link import Link
from mininet.cli import CLI
from mininet.node import RemoteController

parser = argparse.ArgumentParser(description='Creates a hybrid star topology of switches depending on number specified')
parser.add_argument('-s', '--switches', dest='n', default=3, type=int,
	help='creates the topology based on the number specified (default: 3 switches connected to central switch)')
parser.add_argument('-l' '--looptest', dest='lt', action="store_true", help='creates ping looptest on all hosts')
args = parser.parse_args()

def linkIntfs( node1, node2 ):
    "Create link from node1 to node2 and return intfs"
    link = Link( node1, node2 )
    return link.intf1, link.intf2

net = Mininet(controller=RemoteController)
s = list()
h = list()
sInt = list()
hInt = list()

def createTopo(nSwitch):
	#create nodes
	c0 = net.addController()
	s.append(net.addSwitch('s0'))

	for i in range(0, nSwitch):
		s.append(net.addSwitch('s'+str(i+1)))
		h.append(net.addHost('h'+str(i)))
		sInt.append(linkIntfs(s[0], s[i+1]))
		hInt.append(linkIntfs(h[i],s[i+1]))

createTopo(args.n)

net.start()

if(args.lt == True):
    for j in range(0, len(h)):
        for k in range(0, len(h)):
        	if(h[j] != h[k] ):
        		for l in range(0, 4):
	        		hostPair = [h[j], h[k]]
	        		net.pingFull(hostPair)
CLI(net)
net.stop()
