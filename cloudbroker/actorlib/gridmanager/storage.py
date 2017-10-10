from .base import BaseManager
from JumpScale9Portal.portal import exceptions
import random
from time import time

VDISKTYPEMAP = {'BOOT': 'boot',
                'DB': 'db',
                'CACHE': 'cache',
                'TMP': 'tmp'}


class StorageManager(BaseManager):
    def createVolume(self, disk, image=None):
        volume = {}
        if image:
            volume['imageId'] = image.referenceId
            volume['vdiskstorage'] = image.vdiskstorage
        else:
            vdiskstors = self.listVdiskStorages()
            if not vdiskstors:
                raise exceptions.PreconditionFailed('no vdiskstorages available')
            vdiskstor = random.choice(vdiskstors)
            volume['vdiskstorage'] = vdiskstor['id']
        diskid = hex(int(time()*10000000))
        volume.update({'size': disk.size,
                       'blocksize': 4096,
                       'id': diskid,
                       'type': VDISKTYPEMAP.get(disk.type, 'boot'),
                       })
        self.client.vdiskstorage.CreateNewVdisk(volume,  volume['vdiskstorage'])
        disk.referenceId = '{}:{}'.format(volume['vdiskstorage'], diskid)
        disk.modify(referenceId=disk.referenceId)

    def deleteVolume(self, disk):
        if disk.referenceId:
            vdiskstore, diskId = disk.referenceId.split(':')
            self.client.vdiskstorage.DeleteVdisk(diskId, vdiskstore)

    def rollbackVolume(self, disk, epoch):
        data = {'epoch': epoch}
        vdiskstore, diskId = disk.referenceId.split(':')
        self.client.vdiskstorage.RollbackVdisk(data, diskId, vdiskstore)

    def listVdiskStorages(self):
        return self.client.vdiskstorage.ListVdiskStorages().json()

    def listImages(self, vdiskstorage):
        return self.client.vdiskstorage.ListImages(vdiskstorageid=vdiskstorage).json()
