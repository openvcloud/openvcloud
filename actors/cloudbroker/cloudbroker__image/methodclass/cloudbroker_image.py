from JumpScale9Portal.portal import exceptions
from JumpScale9Portal.portal.auth import auth
from cloudbroker.actorlib.baseactor import BaseActor


class cloudbroker_image(BaseActor):
    def __init__(self):
        super(cloudbroker_image, self).__init__()

    def _checkimage(self, imageId):
        cbimage = self.models.Image.get(imageId)
        if not cbimage:
            raise exceptions.BadRequest('Image with id "%s" not found' % imageId)
        return cbimage

    @auth(['level1', 'level2', 'level3'])
    def create(self, name, description, size, accountId, username, password, type, referenceId, **kwargs):
        """
        create an image
        param:name ,,  Image Name
        param:description ,, description of image
        param:size ,, minimal disk size in Gigabyte
        param:username default username for image image
        param:password default password for image
        param:accountId ,, Id of account to which this image belongs
        param:referenceId ,, Path of the image on the storage server
        result int
        """
        image = self.models.Image(
            name=name,
            size=size,
            description=description,
            account=accountId or None,
            status='ENABLED',
            type=type,
            username=username or '',
            password=password or '',
            referenceId=referenceId
        )
        image.save()
        return str(image.id)

    @auth(['level1', 'level2', 'level3'])
    def delete(self, imageId, **kwargs):
        """
        Delete an image
        param:imageId id of image
        result bool
        """
        cbimage = self._checkimage(imageId)
        cbimage.update(status='DESTROYED')
        return True

    @auth(['level1', 'level2', 'level3'])
    def edit(self, imageId, name, description, type, username, password, **kwargs):
        image = self._checkimage(imageId)
        update = {}
        if name:
            image.name = name
        if description:
            image.description = description
        if type:
            image.type = type
        if username:
            image.username = username
        if password:
            image.password = password
        image.save()
    

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
