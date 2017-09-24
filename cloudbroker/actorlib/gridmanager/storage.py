from .base import BaseManager
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
        vdiskstor = random.choice(self.client.vdiskstorage.ListVdiskStorages().json())
        diskid = 'vdisk-{}'.format(disk.id)
        volume.update({'size': disk.size,
                       'blocksize': 4096,
                       'id': diskid,
                       'backupStoragecluster': vdiskstor['slaveCluster'],
                       'objectStoragecluster': vdiskstor['objectCluster'],
                       'blockStoragecluster': vdiskstor['blockCluster'],
                       'type': VDISKTYPEMAP.get(disk.type, 'boot'),
                       })
        self.client.vdisks.CreateNewVdisk(volume)
        disk.referenceId = '{}:{}'.format(vdiskstor, diskid)
        disk.modify(referenceId=disk.referenceId)

    def deleteVolume(self, disk):
        if disk.referenceId:
            cluster, volumeId = disk.referenceId.split(':')
            self.client.vdisks.DeleteVdisk(volumeId)

    def rollbackVolume(self, disk, epoch):
        data = {'epoch': epoch}
        cluster, volumeId = disk.referenceId.split(':')
        self.client.vdisks.RollbackVdisk(data, volumeId)
