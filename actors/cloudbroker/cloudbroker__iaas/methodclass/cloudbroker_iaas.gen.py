from js9 import j

class cloudbroker_iaas(j.tools.code.classGetBase()):
    """
    iaas manager
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="iaas"
        self.appname="cloudbroker"
        #cloudbroker_iaas_osis.__init__(self)


    def addExternalIPS(self, externalnetworkId, startip, endip, **kwargs):
        """
        Adds a public network range to be used for cloudspaces
        param:externalnetworkId the id of the external network
        param:startip First IP Address from the range to add
        param:endip Last IP Address from the range to add
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method addExternalIPS")

    def addExternalNetwork(self, name, subnet, gateway, startip, endip, locationId, vlan, accountId, **kwargs):
        """
        Adds a external network range to be used for cloudspaces
        param:name the subnet to add in CIDR notation (x.x.x.x/y)
        param:subnet the subnet to add in CIDR notation (x.x.x.x/y)
        param:gateway gateway of the subnet
        param:startip First IP Address from the range to add
        param:endip Last IP Address from the range to add
        param:locationId id of the location
        param:vlan VLAN Tag
        param:accountId accountId that has exclusive access to this network Tag
        result int
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method addExternalNetwork")

    def addSize(self, name, vcpus, memory, disksize, **kwargs):
        """
        Add size to location
        param:name Name of the size
        param:vcpus Number of vcpus
        param:memory Memory in MB
        param:disksize Size of bootdisk in GB comma seperated digits
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method addSize")

    def changeIPv4Gateway(self, externalnetworkId, gateway, **kwargs):
        """
        Updates the gateway of the pool
        param:externalnetworkId the id of the external network
        param:gateway Gateway of the pool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method changeIPv4Gateway")

    def deleteExternalNetwork(self, externalnetworkId, **kwargs):
        """
        Deletes external network
        param:externalnetworkId the id of the external network
        result boolean
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method deleteExternalNetwork")

    def deleteSize(self, size_id, **kwargs):
        """
        Deletes unused size from location
        param:size_id Id of size to be deleted
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method deleteSize")

    def removeExternalIP(self, externalnetworkId, ip, **kwargs):
        """
        Removes External IP address
        param:externalnetworkId 
        param:ip 
        result boolean
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method removeExternalIP")

    def removeExternalIPs(self, externalnetworkId, freeips, **kwargs):
        """
        Adds a public network range to be used for cloudspaces
        param:externalnetworkId the id of the external network
        param:freeips list of ips to mark as free in the subnet
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method removeExternalIPs")

    def syncAvailableImagesToCloudbroker(self, **kwargs):
        """
        synchronize IaaS Images from the libcloud model and cpunodes to the cloudbroker model
        result boolean
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method syncAvailableImagesToCloudbroker")

    def syncAvailableSizesToCloudbroker(self, **kwargs):
        """
        synchronize IaaS Sizes/flavors from the libcloud model to the cloudbroker model
        result boolean
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method syncAvailableSizesToCloudbroker")
