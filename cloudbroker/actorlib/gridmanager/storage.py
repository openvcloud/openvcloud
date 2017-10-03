from .base import BaseManager
from JumpScale9Portal.portal import exceptions
import random

VDISKTYPEMAP = {'BOOT': 'boot',
                'DB': 'db',
                'CACHE': 'cache',
                'TMP': 'tmp'}


class StorageManager(BaseManager):
    def createVolume(self, disk, image=None):
        volume = {}
        if image:
            volume['imageId'] = image.referenceId

        vdiskstors = self.client.vdiskstorage.ListVdiskStorages().json()
        if not vdiskstors:
            raise exceptions.PreconditionFailed('no vdiskstorages available')
        vdiskstor = random.choice(vdiskstors)
        diskid = 'vdisk-{}'.format(disk.id)
        volume.update({'size': disk.size,
                       'blocksize': 4096,
                       'id': diskid,
                       'vdiskstorage': vdiskstor['id'],
                       'type': VDISKTYPEMAP.get(disk.type, 'boot'),
                       })
        self.client.vdiskstorage.CreateNewVdisk(volume)
        disk.referenceId = '{}:{}'.format(vdiskstor['id'], diskid)
        disk.modify(referenceId=disk.referenceId)

    def deleteVolume(self, disk):
        if disk.referenceId:
            vdiskstore, diskId = disk.referenceId.split(':')
            self.client.vdiskstorage.DeleteVdisk(diskId, vdiskstore)

    def rollbackVolume(self, disk, epoch):
        data = {'epoch': epoch}
        vdiskstore, diskId = disk.referenceId.split(':')
        self.client.vdiskstorage.RollbackVdisk(data, diskId, vdiskstore)
