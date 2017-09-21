from pox.core import core
from pox.lib.addresses import IPAddr, EthAddr
from pox.lib.util import dpidToStr
from pox.lib.revent import EventHalt
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt
import datetime
import threading
log = core.getLogger()
opcode_map = {1:'REQUEST', 2:'REPLY', 3: 'REV_REQUEST', 4: 'REV_REPLY'}
ipv4_protocols = {4: 'IPv4', 1: 'ICMP_PROTOCOL', 6:'TCP_PROTOCOL', 17:'UDP_PROTOCOL', 2:'IGMP_PROTOCOL'}

checker = list()
switch_number = -1
threshold = 15
interval = 1

class PacketChecker (object):
  """
  A Tutorial object is created for each switch that connects.
  A Connection object for that switch is passed to the __init__ function.
  """
  def __init__ (self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection

    # This binds our PacketIn event listener
    connection.addListeners(self)


    #number is number of switch (determined during initialization)
    self.number = switch_number
    self.attached_host = "10.0.0." + str(self.number)
    self.mac_to_port = {}
    self.enable_checker = False
    self.srcip_list = {}
    self.black_list = list()
    self.timestamp_log = list()
    self.count = 0
    log.info("Switch active")
    log.info("Switch number: " + str(self.number))
    

  def show_blacklist(self):
	print ("BLACKLIST: " + str(self.black_list))
  def set_checker(self, enable):
    if (enable == False):
	  self.enable_checker = False 
	  print ("This checker has been set to: " + str(enable))
    else: 
	  # Default value is True to avoid flows from installing on start-up
	  self.enable_checker = True 
	  print ("This checker has been set to: " + str(enable))


  def get_checkers(self):
    for switch in checker:
		print( "Switch#" + str(switch.number) + " " + str(switch.enable_checker))


def _handle_PacketIn (self, event):
   
    """
    	Description of if statements:
	1) If or if not the algorithm would be implemented in the switch
	2) If or if not the packet is IP type 
        3) If or if not the packet came from the host
        4) If or if not the incoming packet's source IP address is new
        5) If or if not the source is blacklisted 
        6) If or if not the number of packets per source exceeded limit
    """
    # 1)  
    if self.enable_checker == True:
        packet = event.parsed

        self.count += 1 
        print("Switch#" + str(self.number) + " packet# " + str(self.count))
        #Determine if packet is IP type to be able to get IP address of source/destination
        ip = packet.find('ipv4')
        # 2) 
        if ip is None:
           print("Switch# " + str(self.number) + " This isn't IP!")
        else:
           
            #Determine if incoming packet came from host 
            # 3) 
            if (self.attached_host == ip.srcip):
                nothing = 0  
		#log.debug("I am from my host. Ignored")
            else:         
                print("Switch# " + str(self.number) + " Source IP: " +  str(ip.srcip))
                #log.debug("Switch# " + str(self.number) + " Destination IP:" + str(ip.dstip))

                #If source IP is new, record it. 
                #Then, create new thread that eventually remove logs
                # 4) 
	        if ip.srcip not in self.srcip_list:
	      	    self.srcip_list[ip.srcip] = list()
                    print("Create new record of IP: " + str(ip.srcip))
                    time_check = datetime.datetime.now()
                    self.srcip_list[ip.srcip].append(time_check)
                    t = threading.Thread(target=log_remover, args=(self, ip.srcip))
                    t.start()
	        else:
                    #If blacklisted, block. Else, log the packets
		    # 5) 
                    if str(ip.srcip) in self.black_list:
                        print(str(ip.srcip) + "BLOCKED!")
						
						#Create openflow message to set block rule 
                        msg = of.ofp_flow_mod()
                        msg.priority = 30000
                        msg.match.dl_type = pkt.ethernet.IP_TYPE
                        msg.match.nw_dst = IPAddr(self.attached_host)
                        msg.match.nw_src = ip.srcip 
                        msg.match.nw_proto = pkt.ipv4.ICMP_PROTOCOL
                        self.connection.send(msg)
                        return EventHalt
        
                    else:
                        # 6) Log the packet if threshold is not exceeded

                        if len(self.srcip_list[ip.srcip]) < threshold:
                            time_check = datetime.datetime.now()
                            self.srcip_list[ip.srcip].append(time_check)
                        else:
                            print("Added to blacklist: " + str(ip.srcip) + "Reason: " + str(len(self.srcip_list[ip.srcip])))
                            self.black_list.append(str(ip.srcip))

                            #Create openflow message to set block rule
                            msg = of.ofp_flow_mod()
                            msg.priority = 30000
                            msg.match.dl_type = pkt.ethernet.IP_TYPE
                            msg.match.nw_dst = IPAddr(self.attached_host)
                            msg.match.nw_src = ip.srcip
                            msg.match.nw_proto = pkt.ipv4.ICMP_PROTOCOL 
                            self.connection.send(msg)

def log_remover(self,ip_key):
    log.debug("THREAD STARTED")
    while True:
        time_check = datetime.datetime.now()
        for timestamp in self.srcip_list[ip_key]:

            #All logged packets longer than 1 seconds are removed
        
            if (time_check - timestamp) > datetime.timedelta(seconds=1):
	        self.srcip_list[ip_key].remove(timestamp)
	        log.debug("removed a log")
                    
def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    global switch_number
    switch_number += 1
    log.debug("Controlling %s" % (event.connection,))
    checker.append(PacketChecker(event.connection))
    core.Interactive.variables['checker'] = checker
  core.openflow.addListenerByName("ConnectionUp", start_switch)
