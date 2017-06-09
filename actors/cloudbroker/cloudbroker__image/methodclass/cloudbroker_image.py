from js9 import j
from JumpScale9Portal.portal import exceptions
from JumpScale.portal.portal.auth import auth
from cloudbrokerlib.baseactor import BaseActor


class cloudbroker_image(BaseActor):
    def __init__(self):
        super(cloudbroker_image, self).__init__()

    def _checkimage(self, imageId):
        cbimage = self.models.image.search({'id': imageId})[1:]
        if not cbimage:
            raise exceptions.BadRequest('Image with id "%s" not found' % imageId)
        cbimage = cbimage[0]
        return cbimage

    @auth(['level1', 'level2', 'level3'])
    def create(self, name, gid, description, size, accountId, type, referenceId, **kwargs):
        """
        create an image
        param:name ,,  Image Name
        param:gid ,,grid id
        param:description ,, description of image
        param:size ,, minimal disk size in Gigabyte
        param:accountId ,, Id of account to which this image belongs
        param:referenceId ,, Path of the image on the storage server
        result int
        """
        if self.models.location.count({'gid': gid}) == 0:
            raise exceptions.BadRequest("Location with gid {} does not exists".format(gid))
        image = self.models.image.new()
        image.name = name
        image.gid = gid
        image.size = size
        image.description = description
        image.accountId = accountId or 0
        image.status = 'CREATED'
        image.type = type
        image.referenceId = referenceId
        return self.models.image.set(image)[0]

    @auth(['level1', 'level2', 'level3'])
    def delete(self, imageId, **kwargs):
        """
        Delete an image
        param:imageId id of image
        result bool
        """
        cbimage = self._checkimage(imageId)
        cbimage['status'] = 'DESTROYED'
        self.models.image.set(cbimage)
        images = self.models.image.search({'referenceId': imageId})[1:]
        for image in images:
            self.models.stack.updateSearch({'images': image['id']}, {'$pull': {'images': image['id']}})
        return True

    @auth(['level1', 'level2', 'level3'])
    def rename(self, imageId, name, **kwargs):
        self._checkimage(imageId)
        self.models.image.updateSearch({'id': imageId}, {'$set': {'name': name}})

    @auth(['level1', 'level2', 'level3'])
    def enable(self, imageId, **kwargs):
        """
        Enable an image
        param:imageId id of image
        result bool
        """
        self._checkimage(imageId)
        self.models.image.updateSearch({'id': imageId}, {'$set': {'status': 'CREATED'}})

    @auth(['level1', 'level2', 'level3'])
    def disable(self, imageId, **kwargs):
        """
        Disable an image
        param:imageId id of image
        result bool
        """
        self._checkimage(imageId)
        self.models.image.updateSearch({'id': imageId}, {'$set': {'status': 'DISABLED'}})

    @auth(['level1', 'level2', 'level3'])
    def updateNodes(self, imageId, enabledStacks, **kwargs):
        enabledStacks = enabledStacks or list()

        enabledStacks = [int(x) for x in enabledStacks]
        images = self.models.image.search({'id': imageId})[1:]
        if not images:
            raise exceptions.BadRequest("Image Unavailable, is it synced?")
        image = images[0]
        for stack in self.models.stack.search({'images': image['id']})[1:]:
            if stack['id'] not in enabledStacks:
                if image['id'] in stack['images']:
                    stack['images'].remove(image['id'])
                    self.models.stack.set(stack)
            else:
                enabledStacks.remove(stack['id'])

        for stackid in enabledStacks:
            stack = self.models.stack.get(stackid)
            if image['id'] not in stack.images:
                stack.images.append(image['id'])
                self.models.stack.set(stack)

        return True
