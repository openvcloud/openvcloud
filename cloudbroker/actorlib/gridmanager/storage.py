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
            volume['templatevdisk'] = image.referenceId

        vdiskstors = self.client.vdiskstorage.ListVdiskStorages().json()
        if not vdiskstors:
            raise exceptions.PreconditionFailed('no vdiskstorages available')
        vdiskstor = random.choice(vdiskstors)
        diskid = 'vdisk-{}'.format(disk.id)
        volume.update({'size': disk.size,
                       'blocksize': 4096,
                       'id': diskid,
                       'blockStoragecluster': cluster,
                       'type': VDISKTYPEMAP.get(disk.type, 'boot'),
                       })
        self.client.vdisks.CreateNewVdisk(volume)
        disk.referenceId = '{}:{}'.format(vdiskstor['id'], diskid)
        disk.modify(referenceId=disk.referenceId)

    def deleteVolume(self, disk):
        if disk.referenceId:
            cluster, volumeId = disk.referenceId.split(':')
            self.client.vdisks.DeleteVdisk(volumeId)

    def rollbackVolume(self, disk, epoch):
        data = {'epoch': epoch}
        cluster, volumeId = disk.referenceId.split(':')
        self.client.vdisks.RollbackVdisk(data, volumeId)
