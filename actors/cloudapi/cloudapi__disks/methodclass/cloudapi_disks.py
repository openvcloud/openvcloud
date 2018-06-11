from js9 import j
from JumpScale9Portal.portal import exceptions
from cloudbroker.actorlib import authenticator
from cloudbroker.actorlib.baseactor import BaseActor


class cloudapi_disks(BaseActor):
    """
    API Actor api, this actor is the final api a enduser uses to manage his resources

    """
    @authenticator.auth(acl={'account': set('C')})
    def create(self, accountId, locationId, name, description, size=10, type='DB', ssdSize=0, iops=2000, **kwargs):
        """
        Create a disk

        :param accountId: id of account
        :param locationId :id of the location
        :param diskName: name of disk
        :param description: optional description of disk
        :param size: size in GBytes, default is 10
        :param type: (BOOT;DB;CACHE;TMP)
        :return the id of the created disk

        """
        # Validate that enough resources are available in the account CU limits to add the disk
        location = self.models.Location.get(locationId)
        if not location:
            raise exceptions.BadRequest("Invalid locationId passed")
        j.apps.cloudapi.accounts.checkAvailableMachineResources(accountId, vdisksize=size)
        disk = self._create(accountId, location, name, description, size, type, iops)
        return disk.id

    def _create(self, accountId, location, name, description, size=10, type='D', iops=2000, **kwargs):
        if size > 2000:
            raise exceptions.BadRequest("Disk size can not be bigger than 2000 GB")
        disk = self.models.Disk(
            name=name,
            description=description,
            location=location,
            size=size,
            type=type,
            iops=iops,
            account=accountId
        )
        disk.save()
        try:
            client = getGridClient(location, self.models)
            client.storage.createVolume(disk)
        except:
            disk.delete()
            raise
        return disk

    @authenticator.auth(acl={'account': set('C')})
    def limitIO(self, diskId, iops, **kwargs):
        disk = self.models.Disk.get(diskId)
        if not disk or disk.status == 'DESTROYED':
            raise exceptions.NotFound("Disk with id %s is not created" % diskId)

        machine = self.models.VMachine.objects(disks=disk).first()
        if not machine:
            raise exceptions.BadRequest("Could not find virtual machine beloning to disk")
        disk.modify(iops=iops)
        self.cb.machine.update(machine)
        return True

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
        disk = self.models.Disk.get(diskId)
        if not disk:
            return True
        if disk.status == 'DESTROYED':
            return True
        machine = self.models.VMachine.objects(disks=disk).first()
        if machine and not detach:
            raise exceptions.Conflict('Can not delete disk which is attached')
        elif machine:
            j.apps.cloudapi.machines.detachDisk(machineId=machine.id, diskId=diskId, **kwargs)
        client = getGridClient(disk.location, self.models)
        client.storage.deleteVolume(disk)
        disk.update(status='DESTROYED')
        return True
