from js9 import j

class cloudapi_cloudspaces(j.tools.code.classGetBase()):
    """
    API Actor api for managing cloudspaces, this actor is the final api a enduser uses to manage cloudspaces
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="cloudspaces"
        self.appname="cloudapi"
        #cloudapi_cloudspaces_osis.__init__(self)


    def addAllowedSize(self, cloudspaceId, sizeId, **kwargs):
        """
        Add allowed size for a cloudspace
        param:cloudspaceId id of the cloudspace
        param:sizeId id of the required size to be added
        result bool,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method addAllowedSize")

    def addUser(self, cloudspaceId, userId, accesstype, **kwargs):
        """
        Give a registered user access rights
        param:cloudspaceId id of the cloudspace
        param:userId username or emailaddress of the user to grant access
        param:accesstype 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        result bool,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method addUser")

    def create(self, accountId, location, name, access, externalnetworkId, allowedVMSizes, maxMemoryCapacity='-1', maxVDiskCapacity=-1, maxCPUCapacity=-1, maxNetworkPeerTransfer=-1, maxNumPublicIP=-1, **kwargs):
        """
        Create an extra cloudspace
        Setting a cloud unit maximum to -1 or empty will not put any restrictions on the resource
        param:accountId id of acount this cloudspace belongs to
        param:location location code for the cloudspace
        param:name name of space to create
        param:access username of a user which has full access to this space
        param:maxMemoryCapacity max size of memory in GB default=-1
        param:maxVDiskCapacity max size of aggregated vdisks in GB default=-1
        param:maxCPUCapacity max number of cpu cores default=-1
        param:maxNetworkPeerTransfer max sent/received network transfer peering default=-1
        param:maxNumPublicIP max number of assigned public IPs default=-1
        param:externalnetworkId id of externalnetwork to connect to
        param:allowedVMSizes allowed sizes per cloudspace
        result int,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method create")

    def delete(self, cloudspaceId, **kwargs):
        """
        Delete the cloudspace
        param:cloudspaceId id of the cloudspace
        result bool,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method delete")

    def deleteUser(self, cloudspaceId, userId, recursivedelete=False, **kwargs):
        """
        Revoke user access from the cloudspace
        param:cloudspaceId id of the cloudspace
        param:userId id or emailaddress of the user to remove
        param:recursivedelete recursively revoke access rights from related vmachines default=False
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method deleteUser")

    def deploy(self, cloudspaceId, **kwargs):
        """
        Create VFW for cloudspace
        param:cloudspaceId id of the cloudspace
        result str,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method deploy")

    def disable(self, cloudspaceId, reason, **kwargs):
        """
        Disable the cloudspace
        param:cloudspaceId id of the cloudspace
        param:reason reason for disabling
        result bool,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method disable")

    def enable(self, cloudspaceId, reason, **kwargs):
        """
        Enable the cloudspace
        param:cloudspaceId id of the cloudspace
        param:reason reason for enabling
        result bool,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method enable")

    def get(self, cloudspaceId, **kwargs):
        """
        Get cloudspace details
        param:cloudspaceId id of the cloudspace
        result dict,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method get")

    def getDefenseShield(self, cloudspaceId, **kwargs):
        """
        Get information about the defense shield
        param:cloudspaceId id of the cloudspace
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getDefenseShield")

    def getOpenvpnConfig(self, cloudspaceId, **kwargs):
        """
        Get OpenVPN config file (in zip format) for specified cloudspace
        param:cloudspaceId id of the cloudspace
        result str,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getOpenvpnConfig")

    def list(self, **kwargs):
        """
        List all cloudspaces the user has access to
        result [],
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method list")

    def removeAllowedSize(self, cloudspaceId, sizeId, **kwargs):
        """
        Remove allowed size for a cloudspace
        param:cloudspaceId id of the cloudspace
        param:sizeId id of the required size to be removed
        result bool,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method removeAllowedSize")

    def update(self, cloudspaceId, name, maxMemoryCapacity, maxVDiskCapacity, maxCPUCapacity, maxNetworkPeerTransfer, maxNumPublicIP, allowedVMSizes, **kwargs):
        """
        Update the cloudspace name and capacity parameters
        Setting a cloud unit maximum to -1 or empty will not put any restrictions on the resource
        param:cloudspaceId id of the cloudspace
        param:name name of the cloudspace
        param:maxMemoryCapacity max size of memory in GB
        param:maxVDiskCapacity max size of aggregated vdisks in GB
        param:maxCPUCapacity max number of cpu cores
        param:maxNetworkPeerTransfer max sent/received network transfer peering
        param:maxNumPublicIP max number of assigned public IPs
        param:allowedVMSizes allowed sizes per cloudspace
        result bool,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method update")

    def updateUser(self, cloudspaceId, userId, accesstype, **kwargs):
        """
        Update user access rights. Returns True only if an actual update has happened.
        param:cloudspaceId id of the cloudspace
        param:userId userid/email for registered users or emailaddress for unregistered users
        param:accesstype 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        result bool,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method updateUser")
