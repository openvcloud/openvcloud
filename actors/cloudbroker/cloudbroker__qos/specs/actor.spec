
[actor]
    """
    Provide Quality of service feature for network disk and cpu
    """

    method:limitInternalBandwith
        """
        This will put a limit on the VIF of all VMs within the cloudspace or machine
        Pass either cloudspaceId or machineId depending what you want to filter down.
        """
        var:cloudspaceId str,0, Id of the cloudspace to limit @optional
        var:machineId str,0, Id of the machineId to limit @optional
        var:machineMAC string,, MAC of the machine to limit @optional
        var:rate int,, maximum speeds in kilobytes per second, 0 means unlimited
        var:burst int,, maximum burst speed in kilobytes per second, 0 means unlimited
        result:bool

    method:limitInternetBandwith
        """
        This will put a limit on the outgoing traffic on the public VIF of the VFW on the physical machine
        """
        var:cloudspaceId str,, Id of the cloudspace to limit
        var:rate int,, maximum speeds in kilobytes per second, 0 means unlimited
        var:burst int,, maximum burst speed in kilobytes per second, 0 means unlimited
        result:bool

    method:limitIO
        """
        Limit IO done on a certain disk
        """
        var:diskId str,, Id of the disk to limit
        var:iops int,, Max IO per second, 0 means unlimited
        result:bool


    method:limitCPU
        """
        Limit CPU quota
        """
        var:machineId str,, Id of the machine to limit
        result:bool

    method:events
        """
        Handle qos events
        """
        var:event str,, Name of the event
        var:state str,, State of the event
        var:name str,, Name of the affected resource