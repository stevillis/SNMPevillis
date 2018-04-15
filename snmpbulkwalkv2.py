from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import cmdgen
from pysnmp.carrier.asyncore.dgram import udp

class SNMPBulkWalk():
    def __init__(self, community='public', agent='192.168.1.6', OID=(1, 3, 6, 1, 2, 1, 1)):

        self.community = community
        self.agent = agent
        self.OID = OID
        print(self.OID)

        self.response = ''
        
        # Create SNMP engine instance
        self.snmpEngine = engine.SnmpEngine()

        #
        # SNMPv2c setup
        #

        # SecurityName <-> CommunityName mapping
        config.addV1System(self.snmpEngine, 'my-area', self.community)

        # Specify security settings per SecurityName (SNMPv1 - 0, SNMPv2c - 1)
        config.addTargetParams(self.snmpEngine, 'my-creds', 'my-area', 'noAuthNoPriv', 1)

        #
        # Setup transport endpoint and bind it with security settings yielding
        # a target name
        #

        # UDP/IPv4
        config.addTransport(
            self.snmpEngine,
            udp.domainName,
            udp.UdpSocketTransport().openClientMode()
        )
        config.addTargetAddr(
            self.snmpEngine, 'my-router',
            udp.domainName, (self.agent, 161),
            'my-creds'
        )
        


    def start(self):
        # Prepare initial request to be sent
        cmdgen.BulkCommandGenerator().sendVarBinds(
            self.snmpEngine,
            'my-router',
            None, '',  # contextEngineId, contextName
            0, 25,  # non-repeaters, max-repetitions
            [(self.OID, None)], self.cbFun)

        # Run I/O dispatcher which would send pending queries and process responses
        self.snmpEngine.transportDispatcher.runDispatcher()
    
    def get_response(self):
        return self.response
    
    # Error/response receiver
    # noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
    def cbFun(self, snmpEngine, sendRequesthandle, errorIndication,
              errorStatus, errorIndex, varBindTable, cbCtx):
        if errorIndication:
            print(errorIndication)
            return  # stop on error
        if errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBindTable[-1][int(errorIndex) - 1][0] or '?'))
            return  # stop on error
        for varBindRow in varBindTable:            
            for oid, val in varBindRow:
                #print('%s = %s' % (oid.prettyPrint(), val.prettyPrint()))
                #print('%s = %s' % (oid, val))
                self.response += '{} = {}\n'.format(oid, val)
                
        # return True  # signal dispatcher to continue walking
        return False  # signal dispatcher to continue walking        

#obj = SNMPBulkWalk()
#obj.start()
#print(obj.get_response())
