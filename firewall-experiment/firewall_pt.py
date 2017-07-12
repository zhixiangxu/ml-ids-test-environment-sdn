"""
About this firewall prototype:

This firewall program was based on 
-> of_firewall.py by William Emmanuel Yu 
-> mac_blocker.py (already a POX component) by James McCauley
with some ideas from of_sw_tutorial_oo.py for interactivity.

This program was designed to be used with my own 
l2_switch implementation based on the openflow tutorial.
However, it can work with the l2_switch that comes with POX

To make it work please place this file along with
switch_pt.py in the ext folder and type the following:

On the mininet console:
sudo mn --topo single,3 --mac --switch ovsk --controller remote

On Command Line:
./pox.py py log.level --DEBUG firewall_pt switch_pt

Commands Available:

firewall.addFirewallRule(address, dl_type, nw_proto)
>Add a firewall rule that blocks packets with matching properties

firewall.addFirewallRule(address, dl_type, nw_proto)
>Removes a firewall rule with the same property

firewall.showFirewallRules()
>Displays all firewall Rules
"""
#Import pox libraries
from pox.core import core
from pox.lib.revent import EventHalt
from pox.lib.addresses import EthAddr, IPAddr
from pox.lib.util import dpidToStr
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt

#Apply basic logging
log = core.getLogger()

#Storage for all active firewalls
fw = list();

#Firewall allows all connection by default
#Rules define packets to be blocked
class Firewall(object):

	def __init__(self, connection):
		log.info("Firewall activated")		
		self.connection = connection
		connection.addListeners(self)

		#this if for the actual firewall
		self.firewall = set()

################# THE FOLLOWING BLOCK IS FOR FIREWALL ####################

	#Block a packet based on type, protocol and IP addresses
	#It can also block arp packets based on MAC addresses
	#Connections to and from specified IP is blocked
	def addFirewallRule(self, address, toAll=False, dl_type=0x800, nw_proto=1):
		firewallAddRule = of.ofp_flow_mod()
		if dl_type == 0x800:
			ip_addr = IPAddr(address)
			rule_group = (ip_addr, dl_type, nw_proto)

			firewallAddRule.match.dl_type = dl_type
			firewallAddRule.match.nw_dst = ip_addr
			firewallAddRule.match.nw_proto = nw_proto
			firewallAddRule.priority = 65535

			if toAll == False:
				self.connection.send(firewallAddRule)
			else:
				for i in range(0, len(fw)):
					fw[i].connection.send(firewallAddRule)

			if rule_group in self.firewall:
				log.debug("Duplicate Rule Detected")
				return
			self.firewall.add(rule_group)
			log.debug("Adding the following rule: %s -> %s, %s" % (ip_addr, dl_type, nw_proto))

		elif dl_type == 0x806:
			mac_addr = EthAddr(address)
			rule_group = (mac_addr, dl_type, nw_proto)

			firewallAddRule.match.dl_type = dl_type
			firewallAddRule.match.dl_dst = mac_addr
			firewallAddRule.match.nw_proto = nw_proto
			firewallAddRule.priority = 65535

			if toAll == False:
				self.connection.send(firewallAddRule)
			else:
				for i in range(0, len(fw)):
					fw[i].connection.send(firewallAddRule)
			
			if rule_group in self.firewall:
				log.debug("Duplicate Rule Detected")
				return
			self.firewall.add(rule_group)
			log.debug("Adding the following rule: %s -> %s, %s" % (mac_addr, dl_type, nw_proto))

	def delFirewallRule(self, address, toAll=False, dl_type=0x800, nw_proto=1):
		firewallDelRule = of.ofp_flow_mod()
		if dl_type == 0x800:
			ip_addr = IPAddr(address)
			rule_group = (ip_addr, dl_type, nw_proto)
			try:
				self.firewall.remove(rule_group)
				firewallDelRule.match.dl_type = dl_type
				firewallDelRule.match.nw_dst = ip_addr
				firewallDelRule.match.nw_proto = nw_proto
				firewallDelRule.priority = 65535
				firewallDelRule.command = of.OFPFC_DELETE

				if toAll == False:
					self.connection.send(firewallDelRule)
				else:
					for i in range(0, len(fw)):
						fw[i].connection.send(firewallDelRule)

			except KeyError:
				log.debug("Rule %s -> %s, %s not found" % (ip_addr, dl_type, nw_proto))
			log.debug("Removed Rule %s -> %s, %s from block list" % (ip_addr, dl_type, nw_proto))

		elif dl_type == 0x806:
			mac_addr = EthAddr(address)
			rule_group = (mac_addr, dl_type, nw_proto)
			try:
				self.firewall.remove(rule_group)
				firewallDelRule.match.dl_type = dl_type
				firewallDelRule.match.nw_dst = mac_addr
				firewallDelRule.match.nw_proto = nw_proto
				firewallDelRule.priority = 65535
				firewallDelRule.command = of.OFPFC_DELETE
				
				if toAll == False:
					self.connection.send(firewallDelRule)
				else:
					for i in range(0, len(fw)):
						fw[i].connection.send(firewallDelRule)				
			
			except KeyError:
				log.debug("Rule %s -> %s, %s not found" % (mac_addr, dl_type, nw_proto))
			log.debug("Removed Rule %s -> %s, %s from block list" % (mac_addr, dl_type, nw_proto))			

	#THIS IS A SPECIAL TEST FUNCTION FOR THE CENTRAL SWITCH WITH N SWITCHES DYNAMIC TOPO 
	def sendToAllExcept(firewall, address, dl_type=0x800, nw_proto=1):
		firewallAddRule = of.ofp_flow_mod()
		if dl_type == 0x800:
			ip_addr = IPAddr(address)
			rule_group = (ip_addr, dl_type, nw_proto)

			firewallAddRule.match.dl_type = dl_type
			firewallAddRule.match.nw_dst = ip_addr
			firewallAddRule.match.nw_proto = nw_proto
			firewallAddRule.priority = 65535

			for i in range(0, len(fw)):
				if(fw[i] != firewall):
					fw[i].connection.send(firewallAddRule)

	def showFirewallRules(self):
		print "Active Blocking Rules:" 
		for item in self.firewall:
			print "Rule:" + str(item)

	def returnDPID(self):
		dpid = dpidToStr(self.connection.dpid)
		log.debug("DPID: %s" % (dpid))

def launch():
	def start_firewall (event):
		log.debug("Controlling %s" % (event.connection,))
		fw.append(Firewall(event.connection))
		core.Interactive.variables['fw'] = fw
	core.openflow.addListenerByName("ConnectionUp", start_firewall)