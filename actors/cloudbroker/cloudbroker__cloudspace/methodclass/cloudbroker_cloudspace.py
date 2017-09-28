from js9 import j
from cloudbroker.actorlib import authenticator
from JumpScale9Portal.portal.auth import auth
from JumpScale9Portal.portal.async import async
from cloudbroker.actorlib.baseactor import BaseActor
from cloudbroker.actorlib import network
from JumpScale9Portal.portal import exceptions


class cloudbroker_cloudspace(BaseActor):

    def __init__(self):
        super(cloudbroker_cloudspace, self).__init__()
        self.network = network.Network(self.models)

    @auth(['level1', 'level2', 'level3'])
    def destroy(self, accountId, cloudspaceId, reason, **kwargs):
        """
        Destroys a cloudspacec and its machines, vfws and routeros
        """
        cloudspace = self.cb.cloudspace.get(cloudspaceId)

        ctx = kwargs['ctx']
        ctx.events.runAsync(self._destroy,
                            args=(cloudspace, reason, ctx),
                            kwargs={},
                            title='Deleting Cloud Space',
                            success='Finished deleting Cloud Space',
                            error='Failed to delete Cloud Space')

    def _destroy(self, cloudspace, reason, ctx):
        if cloudspace.status == 'DEPLOYING':
            raise exceptions.BadRequest('Can not delete a CloudSpace that is being deployed.')
        status = cloudspace.status
        cloudspace.modify(status='DESTROYING')
        title = 'Deleting Cloud Space %(name)s' % cloudspace
        try:
            # delete machines
            machines = self.models.VMachine.objects(cloudspace=cloudspace, status__ne='DESTROYED')
            for idx, machine in enumerate(machines):  # enumerate(sorted(machines, key=lambda m: m['cloneReference'], reverse=True)):
                if machine.status != 'DESTROYED':
                    ctx.events.sendMessage(title, 'Deleting Virtual Machine %s/%s' % (idx + 1, len(machines)))
                    j.apps.cloudbroker.machine.destroy(machine.id, reason)
        except:
            cloudspace.modify(status=status)
            raise

        # delete vfw
        ctx.events.sendMessage(title, 'Deleting Virtual Firewall')
        self.cb.actors.cloudapi.cloudspaces.delete(cloudspaceId=cloudspace.id)
        return True

    @auth(['level1', 'level2', 'level3'])
    def destroyCloudSpaces(self, cloudspaceIds, reason, **kwargs):
        """
        Destroys a cloudspacec and its machines, vfws and routeros
        """
        ctx = kwargs['ctx']
        ctx.events.runAsync(self._destroyCloudSpaces,
                            args=(cloudspaceIds, reason, ctx),
                            kwargs={},
                            title='Destroying Cloud Spaces',
                            success='Finished destroying Cloud Spaces',
                            error='Failed to destroy Cloud Space')

    def _destroyCloudSpaces(self, cloudspaceIds, reason, ctx):
        for idx, cloudspaceId in enumerate(cloudspaceIds):
            cloudspace = self.cb.cloudspace.get(cloudspaceId)
            self._destroy(cloudspace, reason, ctx)

    @auth(['level1', 'level2', 'level3'])
    @async('Moving Virtual Firewall', 'Finished moving VFW', 'Failed to move VFW')
    def moveVirtualFirewallToFirewallNode(self, cloudspaceId, targetNid, **kwargs):
        """
        move the virtual firewall of a cloudspace to a different firewall node
        param:cloudspaceId id of the cloudspace
        param:targetNode name of the firewallnode the virtual firewall has to be moved to
        """
        cloudspace = self.cb.cloudspace.get(cloudspaceId)
        if cloudspace.status != 'DEPLOYED':
            raise exceptions.BadRequest('Could not move fw for cloudspace which is not deployed')

        fwid = "%s_%s" % (cloudspace.gid, cloudspace.networkId)
        self.cb.netmgr.fw_move(fwid=fwid, targetNid=int(targetNid))
        return True

    @auth(['level1', 'level2', 'level3'])
    def addExtraIP(self, cloudspaceId, ipaddress, **kwargs):
        """
        Adds an available public IP address
        param:cloudspaceId id of the cloudspace
        param:ipaddress only needed if a specific IP address needs to be assigned to this space
        """
        return True

    @auth(['level1', 'level2', 'level3'])
    def removeIP(self, cloudspaceId, ipaddress, **kwargs):
        """
        Removed a public IP address from the cloudspace
        param:cloudspaceId id of the cloudspace
        param:ipaddress public IP address to remove from this cloudspace
        """
        return True

    @auth(['level1', 'level2', 'level3'])
    @async('Deploying Cloud Space', 'Finished deploying Cloud Space', 'Failed to deploy Cloud Space')
    def deployVFW(self, cloudspaceId, **kwargs):
        """
        Deploy VFW
        param:cloudspaceId id of the cloudspace
        """
        return self.cb.actors.cloudapi.cloudspaces.deploy(cloudspaceId=cloudspaceId)

    @auth(['level1', 'level2', 'level3'])
    @async('Redeploying Cloud Space', 'Finished redeploying Cloud Space', 'Failed to redeploy Cloud Space')
    def resetVFW(self, cloudspaceId, **kwargs):
        """
        Restore the virtual firewall of a cloudspace on an available firewall node
        param:cloudspaceId id of the cloudspace
        """
        self.destroyVFW(cloudspaceId, **kwargs)
        self.cb.actors.cloudapi.cloudspaces.deploy(cloudspaceId=cloudspaceId)

    @auth(['level1', 'level2', 'level3'])
    def startVFW(self, cloudspaceId, **kwargs):
        """
        Start VFW
        param:cloudspaceId id of the cloudspace
        """
        if not self.models.cloudspace.exists(cloudspaceId):
            raise exceptions.NotFound('Cloudspace with id %s not found' % (cloudspaceId))

        cloudspace = self.models.cloudspace.get(cloudspaceId)
        fwid = '%s_%s' % (cloudspace.gid, cloudspace.networkId)
        return self.cb.netmgr.fw_start(fwid=fwid)

    @auth(['level1', 'level2', 'level3'])
    def stopVFW(self, cloudspaceId, **kwargs):
        """
        Stop VFW
        param:cloudspaceId id of the cloudspace
        """
        if not self.models.cloudspace.exists(cloudspaceId):
            raise exceptions.NotFound('Cloudspace with id %s not found' % (cloudspaceId))

        cloudspace = self.models.cloudspace.get(cloudspaceId)
        fwid = '%s_%s' % (cloudspace.gid, cloudspace.networkId)
        return self.cb.netmgr.fw_stop(fwid=fwid)

    @auth(['level1', 'level2', 'level3'])
    def destroyVFW(self, cloudspaceId, **kwargs):
        cloudspace = self.cb.cloudspace.get(cloudspaceId)
        self.cb.cloudspace.release_resources(cloudspace, False)
        cloudspace.update(status='VIRTUAL')
        return True

    @auth(['level1', 'level2', 'level3'])
    def update(self, cloudspaceId, name, maxMemoryCapacity, maxVDiskCapacity, maxCPUCapacity,
               maxNetworkPeerTransfer, maxNumPublicIP, allowedVMSizes, **kwargs):
        """
        Update a cloudspace name or the maximum cloud units set on it
        Setting a cloud unit maximum to -1 will not put any restrictions on the resource

        :param cloudspaceId: id of the cloudspace to change
        :param name: name of the cloudspace
        :param maxMemoryCapacity: max size of memory in GB
        :param maxVDiskCapacity: max size of aggregated vdisks in GB
        :param maxCPUCapacity: max number of cpu cores
        :param maxNetworkPeerTransfer: max sent/received network transfer peering
        :param maxNumPublicIP: max number of assigned public IPs
        :return: True if update was successful
        """

        resourcelimits = {'CU_M': maxMemoryCapacity,
                          'CU_D': maxVDiskCapacity,
                          'CU_C': maxCPUCapacity,
                          'CU_NP': maxNetworkPeerTransfer,
                          'CU_I': maxNumPublicIP}
        self.cb.fillResourceLimits(resourcelimits, preserve_none=True)
        maxMemoryCapacity = resourcelimits['CU_M']
        maxVDiskCapacity = resourcelimits['CU_D']
        maxCPUCapacity = resourcelimits['CU_C']
        maxNetworkPeerTransfer = resourcelimits['CU_NP']
        maxNumPublicIP = resourcelimits['CU_I']
        return self.cb.actors.cloudapi.cloudspaces.update(cloudspaceId=cloudspaceId, name=name, maxMemoryCapacity=maxMemoryCapacity,
                                             maxVDiskCapacity=maxVDiskCapacity, maxCPUCapacity=maxCPUCapacity,
                                             maxNetworkPeerTransfer=maxNetworkPeerTransfer, maxNumPublicIP=maxNumPublicIP, allowedVMSizes=allowedVMSizes)

    @auth(['level1', 'level2', 'level3'])
    def create(self, accountId, locationId, name, access, stackId=None, maxMemoryCapacity=-1, maxVDiskCapacity=-1,
               maxCPUCapacity=-1, maxNetworkPeerTransfer=-1, maxNumPublicIP=-1, externalnetworkId=None, allowedVMSizes=[], **kwargs):
        """
        Create a cloudspace

        :param accountId: id of account to create space for
        :param name: name of space to create
        :param maxMemoryCapacity: max size of memory in GB
        :param maxVDiskCapacity: max size of aggregated vdisks in GB
        :param maxCPUCapacity: max number of cpu cores
        :param maxNetworkPeerTransfer: max sent/received network transfer peering
        :param maxNumPublicIP: max number of assigned public IPs
        :param allowedVMSizes: alowed sizes for a cloudspace
        :return: True if update was successful
        """
        if self.systemodel.User.objects(name=access).count() == 0:
            raise exceptions.NotFound('Username "%s" not found' % access)

        resourcelimits = {'CU_M': maxMemoryCapacity,
                          'CU_D': maxVDiskCapacity,
                          'CU_C': maxCPUCapacity,
                          'CU_NP': maxNetworkPeerTransfer,
                          'CU_I': maxNumPublicIP}
        self.cb.fillResourceLimits(resourcelimits)
        maxMemoryCapacity = resourcelimits['CU_M']
        maxVDiskCapacity = resourcelimits['CU_D']
        maxCPUCapacity = resourcelimits['CU_C']
        maxNetworkPeerTransfer = resourcelimits['CU_NP']
        maxNumPublicIP = resourcelimits['CU_I']

        return self.cb.cloudspace.create(accountId=accountId, locationId=locationId, name=name,
                                         access=access, stackId=None, maxMemoryCapacity=maxMemoryCapacity,
                                         maxVDiskCapacity=maxVDiskCapacity, maxCPUCapacity=maxCPUCapacity,
                                         maxNetworkPeerTransfer=maxNetworkPeerTransfer,
                                         maxNumPublicIP=maxNumPublicIP, externalnetworkId=externalnetworkId,
                                         allowedVMSizes=allowedVMSizes, **kwargs)

    @auth(['level1', 'level2', 'level3'])
    def addUser(self, cloudspaceId, username, accesstype, **kwargs):
        """
        Give a user access rights.
        Access rights can be 'R' or 'W'
        param:accountname id of the account
        param:username id of the user to give access or emailaddress to invite an external user
        param:accesstype 'R' for read only access, 'W' for Write access
        result bool
        """
        return self.cb.actors.cloudapi.cloudspaces.addUser(cloudspaceId=cloudspaceId, userId=username, accesstype=accesstype)

    @auth(['level1', 'level2', 'level3'])
    def deleteUser(self, cloudspaceId, username, recursivedelete, **kwargs):
        """
        Delete a user from the account
        """
        return self.cb.actors.cloudapi.cloudspaces.deleteUser(cloudspaceId=cloudspaceId, userId=username, recursivedelete=recursivedelete)

    @auth(['level1', 'level2', 'level3'])
    def deletePortForward(self, cloudspaceId, publicIp, publicPort, proto, **kwargs):
        return self.cb.actors.cloudapi.portforwarding.deleteByPort(cloudspaceId=cloudspaceId, publicIp=publicIp, publicPort=publicPort, proto=proto)
