from js9 import j
from JumpScale9Portal.portal import exceptions
from JumpScale9Portal.portal.auth import auth
from cloudbroker.actorlib.baseactor import BaseActor


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
        image.status = 'ENABLED'
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

        enabledStacks = [x for x in enabledStacks]
        image = self.models.Image.get(imageId)
        if not image:
            raise exceptions.BadRequest("Image Unavailable, is it synced?")
        for stack in self.models.Stack.objects(images=image):
            if str(stack.id) not in enabledStacks:
                stack.update(pull_images=image)
            else:
                enabledStacks.remove(str(stack.id))

        for stackid in enabledStacks:
            stack = self.models.Stack.get(stackid)
            stack.update(add_to_set__images=image)
        return True
