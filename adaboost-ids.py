from pox.core import core
import pickle

CLASSIFIER_FILE = 'adaboost-ids.pkl'

class PacketChecker(object):

    def __init__(self, connection):
        self.connection = connection
        connection.addListeners(self)

        self.number = switch_number

        clf = joblib.load(CLASSIFIER_FILE)
        log.info('Classifier loaded')

        log.info('Switch active')
        log.info('Switch number:' +  str(self.number))

    def _handle_PacketIn(self, event):
        info.log('Packet In')

    #Start Component
    def launch():
        
        def start_switch (event):
            global switch_number
            switch_number += 1
            log.debug("Controlling %s" % (event.connection,))
            checker.append(PacketChecker(event.connection))
            core.Interactive.variables['checker'] = checker

        core.openflow.addListenerByName("Connection Up", start_switch)
