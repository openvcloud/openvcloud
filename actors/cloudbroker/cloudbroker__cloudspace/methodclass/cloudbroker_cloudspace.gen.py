from js9 import j

class cloudbroker_cloudspace(j.code.classGetBase()):
    """
    Operator actions to perform interventions on cloudspaces
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="cloudspace"
        self.appname="cloudbroker"
        #cloudbroker_cloudspace_osis.__init__(self)


    def addExtraIP(self, cloudspaceId, ipaddress, **kwargs):
        """
        Adds an available public IP address
        param:cloudspaceId id of the cloudspace
        param:ipaddress only needed if a specific IP address needs to be assigned to this space
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method addExtraIP")

    def addUser(self, cloudspaceId, username, accesstype, **kwargs):
        """
        Give a user access rights.
        param:cloudspaceId Id of the cloudspace
        param:username name of the user to be given rights
        param:accesstype 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method addUser")

    def create(self, accountId, location, name, access, externalnetworkId, allowedVMSizes, maxMemoryCapacity=-1.0, maxVDiskCapacity=-1, maxCPUCapacity=-1, maxNetworkPeerTransfer=-1, maxNumPublicIP=-1, **kwargs):
        """
        Create a cloudspace for given account
        Setting a cloud unit maximum to -1 or empty will not put any restrictions on the resource
        param:accountId name of account to create space for
        param:location location key where the space should be created
        param:name name of space to create
        param:access username which have full access to this space
        param:maxMemoryCapacity max size of memory in GB default=-1.0
        param:maxVDiskCapacity max size of aggregated vdisks in GB default=-1
        param:maxCPUCapacity max number of cpu cores default=-1
        param:maxNetworkPeerTransfer max sent/received network transfer peering default=-1
        param:maxNumPublicIP max number of assigned public IPs default=-1
        param:externalnetworkId Id of external network to connect to
        param:allowedVMSizes allowed sizes per cloudspace
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method create")

    def deletePortForward(self, cloudspaceId, publicIp, publicPort, proto, **kwargs):
        """
        Deletes a port forwarding rule for a machine
        param:cloudspaceId ID of cloudspace
        param:publicIp Portforwarding public ip
        param:publicPort Portforwarding public port
        param:proto Portforwarding protocol
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method deletePortForward")

    def deleteUser(self, cloudspaceId, username, recursivedelete, **kwargs):
        """
        Delete user from account.
        param:cloudspaceId Id of the cloudspace
        param:username name of the user to be removed
        param:recursivedelete recursively delete access rights from owned cloudspaces and vmachines
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method deleteUser")

    def deployVFW(self, cloudspaceId, **kwargs):
        """
        Deploy VFW
        param:cloudspaceId id of the cloudspace
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method deployVFW")

    def destroy(self, accountId, cloudspaceId, reason, **kwargs):
        """
        destroy a cloudspace
        Destroys its machines, vfws and routeros
        param:accountId id of account
        param:cloudspaceId ID of cloudspace
        param:reason reason for destroying the cloudspace
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method destroy")

    def destroyCloudSpaces(self, cloudspaceIds, reason, **kwargs):
        """
        Destroy a group of cloud spaces
        param:cloudspaceIds IDs of cloudspaces
        param:reason ID of account
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method destroyCloudSpaces")

    def destroyVFW(self, cloudspaceId, **kwargs):
        """
        Destroy VFW of this cloudspace
        param:cloudspaceId Id of the cloudspace
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method destroyVFW")

    def moveVirtualFirewallToFirewallNode(self, cloudspaceId, targetNid, **kwargs):
        """
        move the virtual firewall of a cloudspace to a different firewall node
        param:cloudspaceId id of the cloudspace
        param:targetNid name of the firewallnode the virtual firewall has to be moved to
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method moveVirtualFirewallToFirewallNode")

    def removeIP(self, cloudspaceId, ipaddress, **kwargs):
        """
        Removed a public IP address from the cloudspace
        param:cloudspaceId id of the cloudspace
        param:ipaddress public IP address to remove from this cloudspace
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method removeIP")

    def resetVFW(self, cloudspaceId, **kwargs):
        """
        Reset VFW
        param:cloudspaceId id of the cloudspace
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method resetVFW")

    def startVFW(self, cloudspaceId, **kwargs):
        """
        Start VFW
        param:cloudspaceId id of the cloudspace
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method startVFW")

    def stopVFW(self, cloudspaceId, **kwargs):
        """
        Stop VFW
        param:cloudspaceId id of the cloudspace
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method stopVFW")

    def update(self, cloudspaceId, name, maxMemoryCapacity, maxVDiskCapacity, maxCPUCapacity, maxNetworkPeerTransfer, maxNumPublicIP, allowedVMSizes, **kwargs):
        """
        Update cloudspace.
        Setting a cloud unit maximum to -1 or empty will not put any restrictions on the resource
        param:cloudspaceId ID of cloudspace
        param:name Display name
        param:maxMemoryCapacity max size of memory in GB
        param:maxVDiskCapacity max size of aggregated vdisks in GB
        param:maxCPUCapacity max number of cpu cores
        param:maxNetworkPeerTransfer max sent/received network transfer peering
        param:maxNumPublicIP max number of assigned public IPs
        param:allowedVMSizes allowed sizes per cloudspace
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method update")
