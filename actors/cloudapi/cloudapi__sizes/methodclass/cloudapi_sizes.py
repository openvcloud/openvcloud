from js9 import j
from cloudbrokerlib.baseactor import BaseActor

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
        cloudspaceId = int(cloudspaceId)
        cloudspace = self.models.cloudspace.get(cloudspaceId)
        fields = ['id', 'name', 'vcpus', 'memory', 'description', 'CU', 'disks']
        if cloudspace.allowedVMSizes:
            results = self.models.size.search({'$fields': fields, 'gids': cloudspace.gid, 'id': {'$in': cloudspace.allowedVMSizes}})[1:]
        else:
            results = self.models.size.search({'$fields': fields, 'gids': cloudspace.gid})[1:]
        return results
