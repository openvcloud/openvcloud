from js9 import j
from JumpScale9Portal.portal import exceptions
from cloudbrokerlib import authenticator
from cloudbrokerlib.gridmanager.client import getGridClient
from cloudbrokerlib.baseactor import BaseActor


class cloudapi_disks(BaseActor):
    """
    API Actor api, this actor is the final api a enduser uses to manage his resources

    """

    def __init__(self):
        super(cloudapi_disks, self).__init__()
        self.osisclient = j.core.portal.active.osis
        self.osis_logs = j.clients.osis.getCategory(self.osisclient, "system", "log")
        self._minimum_days_of_credit_required = float(self.hrd.get(
            "instance.openvcloud.cloudbroker.creditcheck.daysofcreditrequired"))

    def getStorageVolume(self, disk, provider, node=None):
        if not isinstance(disk, dict):
            disk = disk.dump()
        return OpenvStorageVolume(id=disk['referenceId'], name=disk['name'], size=disk['sizeMax'], driver=provider.client, extra={'node': node}, iops=disk['iops'])

    @authenticator.auth(acl={'account': set('C')})
    def create(self, accountId, gid, name, description, size=10, type='D', ssdSize=0, iops=2000, **kwargs):
        """
        Create a disk

        :param accountId: id of account
        :param gid :id of the grid
        :param diskName: name of disk
        :param description: optional description of disk
        :param size: size in GBytes, default is 10
        :param type: (B;D;T)  B=Boot;D=Data;T=Temp, default is B
        :return the id of the created disk

        """
        # Validate that enough resources are available in the account CU limits to add the disk
        j.apps.cloudapi.accounts.checkAvailableMachineResources(accountId, vdisksize=size)
        disk = self._create(accountId, gid, name, description, size, type, iops)
        return disk.id

    def _create(self, accountId, gid, name, description, size=10, type='D', iops=2000, **kwargs):
        if size > 2000:
            raise exceptions.BadRequest("Disk size can not be bigger than 2000 GB")
        disk = self.models.disk.new()
        disk.name = name
        disk.descr = description
        disk.sizeMax = size
        disk.type = type
        disk.gid = gid
        disk.iops = iops
        disk.accountId = accountId
        diskid = self.models.disk.set(disk)[0]
        disk = self.models.disk.get(diskid)
        try:
            client = getGridClient(gid, self.models)
            client.storage.createVolume(disk)
        except:
            self.models.disk.delete(disk.id)
            raise
        self.models.disk.set(disk)
        return disk

    @authenticator.auth(acl={'account': set('C')})
    def limitIO(self, diskId, iops, **kwargs):
        disk = self.models.disk.get(diskId)
        if disk.status == 'DESTROYED':
            raise exceptions.BadRequest("Disk with id %s is not created" % diskId)

        machine = next(iter(self.models.vmachine.search({'disks': diskId})[1:]), None)
        if not machine:
            raise exceptions.NotFound("Could not find virtual machine beloning to disk")
        disk.iops = iops
        self.models.disk.set(disk)
        provider, node, machine = self.cb.getProviderAndNode(machine['id'])
        volume = self.getStorageVolume(disk, provider, node)
        return provider.client.ex_limitio(volume, iops)

    @authenticator.auth(acl={'account': set('R')})
    def get(self, diskId, **kwargs):
        """
        Get disk details

        :param diskId: id of the disk
        :return: dict with the disk details
        """
        if not self.models.disk.exists(diskId):
            raise exceptions.NotFound('Can not find disk with id %s' % diskId)
        return self.models.disk.get(diskId).dump()

    @authenticator.auth(acl={'account': set('R')})
    def list(self, accountId, type, **kwargs):
        """
        List the created disks belonging to an account

        :param accountId: id of accountId the disks belongs to
        :param type: type of type of the disks
        :return: list with every element containing details of a disk as a dict
        """
        query = {'accountId': accountId, 'status': {'$ne': 'DESTROYED'}}
        if type:
            query['type'] = type
        disks = self.models.disk.search(query)[1:]
        diskids = [disk['id'] for disk in disks]
        query = {'disks': {'$in': diskids}}
        vms = self.models.vmachine.search({'$query': query, '$fields': ['disks', 'id']})[1:]
        vmbydiskid = dict()
        for vm in vms:
            for diskid in vm['disks']:
                vmbydiskid[diskid] = vm['id']
        for disk in disks:
            disk['machineId'] = vmbydiskid.get(disk['id'])
        return disks

    @authenticator.auth(acl={'cloudspace': set('X')})
    def delete(self, diskId, detach, **kwargs):
        """
        Delete a disk

        :param diskId: id of disk to delete
        :param detach: detach disk from machine first
        :return True if disk was deleted successfully
        """
        if not self.models.disk.exists(diskId):
            return True
        disk = self.models.disk.get(diskId)
        if disk.status == 'DESTROYED':
            return True
        machines = self.models.vmachine.search({'disks': diskId, 'status': {'$ne': 'DESTROYED'}})[1:]
        if machines and not detach:
            raise exceptions.Conflict('Can not delete disk which is attached')
        elif machines:
            j.apps.cloudapi.machines.detachDisk(machineId=machines[0]['id'], diskId=diskId, **kwargs)
        client = getGridClient(disk.gid, self.models)
        client.storage.deleteVolume(disk)
        disk.status = 'DESTROYED'
        self.models.disk.set(disk)
        return True
