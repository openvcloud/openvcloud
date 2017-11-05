from js9 import j

class cloudbroker_qos(j.tools.code.classGetBase()):
    """
    Provide Quality of service feature for network disk and cpu
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="qos"
        self.appname="cloudbroker"
        #cloudbroker_qos_osis.__init__(self)


    def events(self, event, state, name, **kwargs):
        """
        Handle qos events
        param:event Name of the event
        param:state State of the event
        param:name Name of the affected resource
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method events")

    def limitCPU(self, machineId, **kwargs):
        """
        Limit CPU quota
        param:machineId Id of the machine to limit
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method limitCPU")

    def limitIO(self, diskId, iops, **kwargs):
        """
        Limit IO done on a certain disk
        param:diskId Id of the disk to limit
        param:iops Max IO per second, 0 means unlimited
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method limitIO")

    def limitInternalBandwith(self, machineMAC, rate, burst, cloudspaceId='0', machineId='0', **kwargs):
        """
        This will put a limit on the VIF of all VMs within the cloudspace or machine
        Pass either cloudspaceId or machineId depending what you want to filter down.
        param:cloudspaceId Id of the cloudspace to limit default=0
        param:machineId Id of the machineId to limit default=0
        param:machineMAC MAC of the machine to limit
        param:rate maximum speeds in kilobytes per second, 0 means unlimited
        param:burst maximum burst speed in kilobytes per second, 0 means unlimited
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method limitInternalBandwith")

    def limitInternetBandwith(self, cloudspaceId, rate, burst, **kwargs):
        """
        This will put a limit on the outgoing traffic on the public VIF of the VFW on the physical machine
        param:cloudspaceId Id of the cloudspace to limit
        param:rate maximum speeds in kilobytes per second, 0 means unlimited
        param:burst maximum burst speed in kilobytes per second, 0 means unlimited
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method limitInternetBandwith")
