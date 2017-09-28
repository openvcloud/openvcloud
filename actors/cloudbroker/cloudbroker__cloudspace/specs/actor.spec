[actor] @dbtype:mem,fs
    """
    Operator actions to perform interventions on cloudspaces
    """
    method:destroy
        """
        destroy a cloudspace
        Destroys its machines, vfws and routeros
        """
        var:accountId str,,id of account
        var:cloudspaceId str,,ID of cloudspace
        var:reason str,, reason for destroying the cloudspace

    method:moveVirtualFirewallToFirewallNode
        """
        move the virtual firewall of a cloudspace to a different firewall node
        """
        var:cloudspaceId str,, id of the cloudspace
        var:targetNid int,, name of the firewallnode the virtual firewall has to be moved to

    method:resetVFW
        """
        Reset VFW
        """
        var:cloudspaceId str,, id of the cloudspace

    method:deployVFW
        """
        Deploy VFW
        """
        var:cloudspaceId str,, id of the cloudspace

    method:startVFW
        """
        Start VFW
        """
        var:cloudspaceId str,, id of the cloudspace

    method:stopVFW
        """
        Stop VFW
        """
        var:cloudspaceId str,, id of the cloudspace

    method:addExtraIP
        """
        Adds an available public IP address
        """
        var:cloudspaceId str,, id of the cloudspace
        var:ipaddress str,, only needed if a specific IP address needs to be assigned to this space @optional

    method:removeIP
        """
        Removed a public IP address from the cloudspace
        """
        var:cloudspaceId str,, id of the cloudspace
        var:ipaddress str,, public IP address to remove from this cloudspace

    method:create
        """
        Create a cloudspace for given account
        Setting a cloud unit maximum to -1 or empty will not put any restrictions on the resource
        """
        var:accountId str,, name of account to create space for
        var:locationId str,, location key where the space should be created
        var:name str,, name of space to create @tags validator:name
        var:access str,, username which have full access to this space
        var:stackId str,, Id of the stack to deploy the cloudspace on @optional
        var:maxMemoryCapacity float,-1, max size of memory in GB @optional
        var:maxVDiskCapacity int,-1, max size of aggregated vdisks in GB @optional
        var:maxCPUCapacity int,-1, max number of cpu cores @optional
        var:maxNetworkPeerTransfer int,-1, max sent/received network transfer peering @optional
        var:maxNumPublicIP int,-1, max number of assigned public IPs @optional
        var:externalnetworkId str,, Id of external network to connect to @optional
        var:allowedVMSizes list(int),, allowed sizes per cloudspace @optional

    method:update
        """
        Update cloudspace.
        Setting a cloud unit maximum to -1 or empty will not put any restrictions on the resource
        """"
        var:cloudspaceId str,,ID of cloudspace
        var:name str,, Display name
        var:maxMemoryCapacity float,, max size of memory in GB @optional
        var:maxVDiskCapacity int,, max size of aggregated vdisks in GB @optional
        var:maxCPUCapacity int,, max number of cpu cores @optional
        var:maxNetworkPeerTransfer int,, max sent/received network transfer peering @optional
        var:maxNumPublicIP int,, max number of assigned public IPs @optional
        var:allowedVMSizes list(int),, allowed sizes per cloudspace @optional

    method:destroyVFW
        """
        Destroy VFW of this cloudspace
        """
        var:cloudspaceId str,,Id of the cloudspace

    method:addUser
        """
        Give a user access rights.
        """"
        var:cloudspaceId str,,Id of the cloudspace
        var:username str,,name of the user to be given rights
        var:accesstype str,, 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin

    method:deleteUser
        """
        Delete user from account.
        """"
        var:cloudspaceId str,,Id of the cloudspace
        var:username str,,name of the user to be removed
        var:recursivedelete bool,, recursively delete access rights from owned cloudspaces and vmachines

    method:deletePortForward
        """
        Deletes a port forwarding rule for a machine
        """
        var:cloudspaceId str,, ID of cloudspace
        var:publicIp str,,Portforwarding public ip
        var:publicPort int,,Portforwarding public port
        var:proto str,,Portforwarding protocol

    method:destroyCloudSpaces
        """
        Destroy a group of cloud spaces
        """
        var:cloudspaceIds list(str),, IDs of cloudspaces
        var:reason str,, ID of account
