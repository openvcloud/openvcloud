[actor] @dbtype:mem,fs
    """
    iaas manager
    """
    method:syncAvailableImagesToCloudbroker
        """
        synchronize IaaS Images from the libcloud model and cpunodes to the cloudbroker model
        """
        result:boolean

    method:addExternalNetwork
        """
        Adds a external network range to be used for cloudspaces
        """
        var:name str,, the subnet to add in CIDR notation (x.x.x.x/y)
        var:subnet str,, the subnet to add in CIDR notation (x.x.x.x/y)
        var:gateway str,, gateway of the subnet
        var:startip str,, First IP Address from the range to add
        var:endip str,, Last IP Address from the range to add
        var:locationId str,, id of the location
        var:vlan int,,VLAN Tag
        var:accountId str,,accountId that has exclusive access to this network Tag @optional
        result:int

    method:deleteExternalNetwork
        """
        Deletes external network
        """
        var:externalnetworkId str,, the id of the external network
        result:boolean

    method:addExternalIPS
        """
        Adds a public network range to be used for cloudspaces
        """
        var:externalnetworkId str,, the id of the external network
        var:startip str,, First IP Address from the range to add
        var:endip str,, Last IP Address from the range to add

    method:changeIPv4Gateway
        """
        Updates the gateway of the pool
        """
        var:externalnetworkId str,, the id of the external network
        var:gateway str,, Gateway of the pool

    method:removeExternalIP
        """
        Removes External IP address
        """
        var:externalnetworkId str,,
        var:ip str,,
        result:boolean

    method:addSize
        """
        Add size to location
        """
        var:name str,, Name of the size
        var:vcpus int,,Number of vcpus
        var:memory int,,Memory in MB
        var:disksize str,,Size of bootdisk in GB comma seperated digits

    method:deleteSize
        """
        Deletes unused size from location
        """
        var:size_id int,, Id of size to be deleted

    method:removeExternalIPs
        """
        Adds a public network range to be used for cloudspaces
        """
        var:externalnetworkId str,, the id of the external network
        var:freeips list,, list of ips to mark as free in the subnet

    method:syncAvailableSizesToCloudbroker
        """
        synchronize IaaS Sizes/flavors from the libcloud model to the cloudbroker model
        """
        result:boolean
