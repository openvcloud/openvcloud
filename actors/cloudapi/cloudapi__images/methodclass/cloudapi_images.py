from cloudbroker.actorlib import authenticator
from JumpScale9Portal.portal import exceptions
from cloudbroker.actorlib.baseactor import BaseActor


class cloudapi_images(BaseActor):
    """
    Lists all the images. A image is a template which can be used to deploy machines.

    """

    def list(self, accountId, cloudspaceId, **kwargs):
        """
        List the available images, filtering can be based on the cloudspace and the user which is doing the request
        """
        import bson
        fields = ['id', 'name', 'description', 'type', 'size', 'username', 'accountId', 'status']
        qkwargs = {
            'referenceId__ne': None,
            'status': 'CREATED'
        }
        if accountId:
            qkwargs['account__in'] = [bson.ObjectId(accountId), None]
        else:
            qkwargs['account'] = None

        if cloudspaceId:
            cloudspace = self.models.Cloudspace.get(cloudspaceId)
            stacks = self.models.Stack.objects(location=cloudspace.location).no_dereference()
            imageids = set()
            for stack in stacks:
                for image in stack.images:
                    imageids.add(image.id)
            qkwargs['id__in'] = list(imageids)

        results = self.models.Image.objects(**qkwargs)

        def getName(image):
            name = "%d %s %s" % (image['accountId'] or 0, image['type'], image['name'])
            return name

        return sorted(results, key=getName)

    def delete(self, imageId, **kwargs):
        """
        Delete an image

        :param imageId: id of the image to delete
        :return True if image was deleted successfully
        """
        ctx = kwargs['ctx']
        user = ctx.env['beaker.session']['user']
        image = self.models.image.get(imageId)
        if image.accountId <= 0:
            raise exceptions.MethodNotAllowed("Can not delete system images")
        account = self.models.account.get(image.accountId)
        auth = authenticator.auth(acl={'account': set('C')})
        auth.isAuthorized(user, account)
        references = self.models.vmachine.count({'imageId': imageId,
                                                 'status': {'$ne': 'DESTROYED'}})
        if references:
            raise exceptions.Conflict("Can not delete an image which is still used")
        if image.status != 'CREATED':
            raise exceptions.Forbidden("Can not delete an image which is not created yet.")

        stacks = self.models.stack.search({'images': imageId})[1:]
        gid = None
        provider = None
        if stacks:
            gid = stacks[0]['gid']
            provider = self.cb.getProviderByStackId(stacks[1]['id'])
        if not gid:
            raise exceptions.Error("Could not find image template")

        provider.client.ex_delete_template(image.referenceId)

        for stack in stacks:
            if imageId in stack['images']:
                stack['images'].remove(imageId)
                self.models.stack.set(stack)

        self.models.image.delete(imageId)
        return True

    def get_or_create_by_name(self, name, add_to_all_stacks=True):
        images = self.models.image.search({'name': name})
        if images[0]:
            image = self.models.image.new()
            image.load(images[1])
            return image
        else:
            image = self.models.image.new()
            image.name = name
            image.provider_name = 'libvirt'
            image.size = 0
            image.status = 'CREATED'
            image.type = 'Linux'
            imageid = self.models.image.set(image)[0]
            image.id = imageid
            if add_to_all_stacks:
                # TODO: enhance
                for stackid in self.models.stack.list():
                    stack = self.models.stack.get(stackid)
                    stack.images.append(imageid)
                    self.models.stack.set(stack)
            return image
