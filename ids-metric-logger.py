#Import pox libraries
from pox.core import core

log = core.getLogger()

class IDSTest(object):

    def __init__(self):
        self.connection = connection
        connection.addListeners(self)

    def log_blocked_host(msg):
        print(msg)

    #Register component to POX core object
    def launch():
        core.registerNew(IDSTest)
        