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
        cluster = random.choice(self.client.storageclusters.ListAllClusters().json())
        diskid = 'vdisk-{}'.format(disk.id)
        volume.update({'size': disk.size,
                       'blocksize': 4096,
                       'id': diskid,
                       'storagecluster': cluster,
                       'type': VDISKTYPEMAP.get(disk.type, 'boot'),
                       })
        self.client.vdisks.CreateNewVdisk(volume)
        disk.referenceId = '{}:{}'.format(cluster, diskid)
        disk.modify(referenceId=disk.referenceId)

    def deleteVolume(self, disk):
        if disk.referenceId:
            cluster, volumeId = disk.referenceId.split(':')
            self.client.vdisks.DeleteVdisk(volumeId)

    def rollbackVolume(self, disk, epoch):
        data = {'epoch': epoch}
        cluster, volumeId = disk.referenceId.split(':')
        self.client.vdisks.RollbackVdisk(data, volumeId)
