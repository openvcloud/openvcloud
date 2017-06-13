from cloudbroker.actorlib.baseactor import BaseActor


class cloudapi_sizes(BaseActor):
    """
    Lists all the configured flavors available.
    A flavor is a combination of amount of compute capacity(CU) and disk capacity(GB).
    """

    def list(self, cloudspaceId, **kwargs):
        """
        List the available flavors, filtering based on the cloudspace

        :param cloudspaceId: id of the cloudspace
        :return list of flavors contains id CU and disksize for every flavor on the cloudspace
        """
        cloudspace = self.models.Cloudspace.get(cloudspaceId)
        fields = ['id', 'name', 'vcpus', 'memory', 'description', 'disks']
        qkwargs = {
            'locations': cloudspace.location
        }
        if cloudspace.allowedVMSizes:
            qkwargs['id__in'] = cloudspace.allowedVMSizes
        sizes = []
        for size in self.models.Size.objects(**qkwargs).only(*fields):
            sizes.append(size.to_dict())
        return sizes
