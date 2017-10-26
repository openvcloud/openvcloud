from js9 import j
from JumpScale9Portal.portal import exceptions
import netaddr
from JumpScale9Portal.portal.auth import auth
from cloudbroker.actorlib.baseactor import BaseActor
from cloudbroker.actorlib.gridmanager.client import getGridClient


def checkIPS(network, ips):
    for ip in ips:
        if netaddr.IPAddress(ip) not in network:
            return False
    return True


class cloudbroker_iaas(BaseActor):
    """
    gateway to grid
    """
    def addExternalNetwork(self, name, subnet, gateway, startip, endip, locationId, vlan, accountId, **kwargs):
        """
        Adds a public network range to be used for cloudspaces
        param:subnet the subnet to add in CIDR notation (x.x.x.x/y)
        """
        try:
            net = netaddr.IPNetwork(subnet)
            if netaddr.IPAddress(startip) not in net:
                raise exceptions.BadRequest("Start IP Addresses %s is not in subnet %s" % (startip, subnet))
            if netaddr.IPAddress(endip) not in net:
                raise exceptions.BadRequest("End IP Addresses %s is not in subnet %s" % (endip, subnet))
            if not checkIPS(net, [gateway]):
                raise exceptions.BadRequest("Gateway Address %s is not in subnet %s" % (gateway, subnet))
            if self.models.ExternalNetwork.objects(vlan=vlan).count() > 0:
                raise exceptions.Conflict("VLAN {} is already in use by another external network")
        except netaddr.AddrFormatError as e:
            raise exceptions.BadRequest(e.args[0])

        if accountId and self.models.Account.objects(id=accountId, status__ne='DESTROYED').count() == 0:
            raise exceptions.BadRequest("AccountId {} is not valid".format(accountId))
        pool = self.models.ExternalNetwork(
            location=locationId,
            gateway=gateway,
            name=name,
            vlan=vlan,
            subnetmask=str(net.netmask),
            network=str(net.network),
            account=accountId,
            ips=[str(ip) for ip in netaddr.IPRange(startip, endip)],
        )
        pool.save()
        return str(pool.id)

    def getUsedIPInfo(self, pool):
        network = {'spaces': [], 'vms': []}
        for space in self.models.Cloudspace.objects(location=pool.location, externalnetwork=pool, status='DEPLOYED'):
            network['spaces'].append(space)
        for vm in self.models.VMachine.find({'nics.type': 'PUBLIC', 'status': {'$nin': ['ERROR', 'DESTROYED']}}):
            for nic in vm.nics:
                if nic.type == 'PUBLIC':
                    tagObject = j.core.tags.getObject(nic.params)
                    if int(tagObject.tags.get('externalnetworkId', 0)) == pool.id:
                        vm.externalnetworkip = nic.ipAddress
                        network['vms'].append(vm)
        return network

    def _getUsedIPS(self, pool):
        networkinfo = self.getUsedIPInfo(pool)
        usedips = set()
        for obj in networkinfo['vms'] + networkinfo['spaces']:
            ip = str(netaddr.IPNetwork(obj['externalnetworkip']).ip)
            usedips.add(ip)
        return usedips

    def deleteExternalNetwork(self, externalnetworkId, **kwargs):
        if not self.models.ExternalNetwork.exists(externalnetworkId):
            raise exceptions.NotFound("Could not find external network with id %s" % externalnetworkId)
        cloudCount = self.models.Cloudspace.objects(externalnetwork=externalnetworkId, status__ne='DESTROYED').count()
        if cloudCount == 0:
            self.models.ExternalNetwork.objects(id=externalnetworkId).delete()
        else:
            raise exceptions.Conflict("Cannot delete, external network in use")
        return True

    def addExternalIPS(self, externalnetworkId, startip, endip, **kwargs):
        """
        Add public ips to an existing range
        """
        pool = self.models.ExternalNetwork.get(externalnetworkId)
        if not pool:
            raise exceptions.NotFound("Could not find external network with id %s" % externalnetworkId)
        try:
            net = netaddr.IPNetwork("{}/{}".format(pool.network, pool.subnetmask))
            if netaddr.IPAddress(startip) not in net:
                raise exceptions.BadRequest("Start IP Addresses %s is not in subnet %s" % (startip, net))
            if netaddr.IPAddress(endip) not in net:
                raise exceptions.BadRequest("End IP Addresses %s is not in subnet %s" % (endip, net))
        except netaddr.AddrFormatError as e:
            raise exceptions.BadRequest(e.message)
        ips = set(pool.ips)
        newset = {str(ip) for ip in netaddr.IPRange(startip, endip)}
        usedips = self._getUsedIPS(pool)
        duplicateips = usedips.intersection(newset)
        if duplicateips:
            raise exceptions.Conflict("New range overlaps with existing deployed IP Addresses")

        ips.update(newset)
        pool.modify(ips=ips)
        return True

    def changeIPv4Gateway(self, externalnetworkId, gateway, **kwargs):
        if not self.models.ExternalNetwork.exists(externalnetworkId):
            raise exceptions.NotFound("Could not find externalnetwork with id %s" % externalnetworkId)

        pool = self.models.ExternalNetwork.get(externalnetworkId)
        try:
            net = netaddr.IPNetwork("{}/{}".format(pool.network, pool.subnetmask))
            if not checkIPS(net, [gateway]):
                raise exceptions.BadRequest("Gateway Address %s is not in subnet %s" % (gateway, net))
        except netaddr.AddrFormatError as e:
            raise exceptions.BadRequest(e.message)

        pool.gateway = gateway
        pool.save()

    def removeExternalIPs(self, externalnetworkId, freeips, **kwargs):
        """
        Remove public ips from an existing range
        """
        ctx = kwargs["ctx"]
        if not self.models.ExternalNetwork.exists(externalnetworkId):
            ctx.start_response("404 Not Found")
            return "Could not find externalnetwork with subnet %s" % externalnetworkId
        pool = self.models.ExternalNetwork.get(externalnetworkId)
        net = netaddr.IPNetwork("{}/{}".format(pool.network, pool.subnetmask))
        if not checkIPS(net, freeips):
            ctx.start_response("400 Bad Request")
            return "One or more IP Addresses %s is not in subnet %s" % (net)
        pool.pubips = list(set(pool.pubips) - set(freeips))
        pool.save()
        return True

    def removeExternalIP(self, externalnetworkId, ip, **kwargs):
        """
        Remove External IP Addresses
        """
        if not self.models.ExternalNetwork.exists(externalnetworkId):
            raise exceptions.NotFound("Could not find externalnetwork with id %s" % externalnetworkId)
        self.models.ExternalNetwork.objects(id=externalnetworkId).update_one(pull__ips=ip)
        return True

    @auth(['level1', 'level2', 'level3'])
    def addSize(self, name, vcpus, memory, disksize, **kwargs):
        """
        Add a new size to grid location.

        @param name: str name of new size.
        @param vcpus: int  number of vcpus to be used.
        @param memory: int  amount of memory for this size.
        @param disksize: [int] list of disk sizes available.
        """
        cloudbroker_size = next(iter(self.models.size.search({"vcpus": vcpus, "memory": memory})[1:]), None)
        disks = map(int, disksize.split(","))
        if not cloudbroker_size:
            cloudbroker_size = dict()
            cloudbroker_size['name'] = name
            cloudbroker_size['memory'] = memory
            cloudbroker_size['vcpus'] = vcpus
            locations = self.models.location.search({"$query": {}, "$fields": ['gid']})
            cloudbroker_size['gids'] = [location['gid'] for location in locations[1:]]
            cloudbroker_size['disks'] = disks
        else:
            new_disks = set(cloudbroker_size['disks'])
            new_disks.update(disks)
            cloudbroker_size['disks'] = list(new_disks)
        self.models.size.set(cloudbroker_size)

        return True

    @auth(['level1', 'level2', 'level3'])
    def deleteSize(self, size_id, **kwargs):
        """
        Delete unused size in location.

        @param size_id: int id if size to be deleted.
        """
        if self.models.vmachine.count({"sizeId": size_id}) == 0:
            self.models.size.delete(size_id)
        return True

    @auth(['level1', 'level2', 'level3'])
    def syncImages(self, locationId, **kwargs):
        """
        synchronize IaaS Images from 0-orchestrator to cloudbroker
        result boolean
        """
        location = self.models.Location.get(locationId)
        if not location:
            raise exceptions.BadRequest("Invalid location passed")
        gc = getGridClient(location, self.models)
        for storage in gc.storage.listVdiskStorages():
            for image in gc.storage.listImages(storage['id']):
                localimage = self.models.Image.objects(referenceId=image['name'], status__ne='DESTROYED').first()
                if not localimage:
                    localimage = self.models.Image(
                        name=image['name'],
                        referenceId=image['name'],
                        vdiskstorage=storage['id'],
                        size=image['size'],
                        blocksize=image['diskBlockSize'],
                        status='ENABLED',
                        type='Imported Image'
                    )
                    localimage.save()
                    self.models.Stack.objects(location=location).update(add_to_set__images=localimage)
        return True
