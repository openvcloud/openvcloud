from js9 import j

class cloudapi_portforwarding(j.code.classGetBase()):
    """
    Portforwarding api
    uses actor /opt/code/jumpscale/unstable__jumpscale_grid/apps/vfw/actor/jumpscale__netmgr/
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="portforwarding"
        self.appname="cloudapi"
        #cloudapi_portforwarding_osis.__init__(self)


    def create(self, cloudspaceId, publicIp, publicPort, machineId, localPort, protocol, **kwargs):
        """
        Create a port forwarding rule
        param:cloudspaceId id of the cloudspace
        param:publicIp public ipaddress
        param:publicPort public port
        param:machineId id of the virtual machine
        param:localPort local port
        param:protocol protocol udp or tcp
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method create")

    def delete(self, cloudspaceId, id, **kwargs):
        """
        Delete a specific port forwarding rule
        param:cloudspaceId id of the cloudspace
        param:id id of the port forward rule
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method delete")

    def deleteByPort(self, cloudspaceId, publicIp, publicPort, proto, **kwargs):
        """
        Delete a specific port forwarding rule by public port details
        param:cloudspaceId id of the cloudspace
        param:publicIp port forwarding public ip
        param:publicPort port forwarding public port
        param:proto port forwarding protocol
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method deleteByPort")

    def list(self, cloudspaceId, machineId, **kwargs):
        """
        List all port forwarding rules in a cloudspace or machine
        param:cloudspaceId id of the cloudspace
        param:machineId id of the machine, all rules of cloudspace will be listed if set to None
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method list")

    def update(self, cloudspaceId, id, publicIp, publicPort, machineId, localPort, protocol, **kwargs):
        """
        Update a port forwarding rule
        param:cloudspaceId id of the cloudspace
        param:id id of the portforward to edit
        param:publicIp public ipaddress
        param:publicPort public port
        param:machineId id of the virtual machine
        param:localPort local port
        param:protocol protocol udp or tcp
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method update")
