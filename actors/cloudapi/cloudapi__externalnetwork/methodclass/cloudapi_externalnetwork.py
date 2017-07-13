from js9 import j
from cloudbroker.actorlib.baseactor import BaseActor


class cloudapi_externalnetwork(BaseActor):

    def list(self, accountId, **kwargs):
        """
        result
        """
        query = {}
        if accountId:
            query['account__in'] = [None, accountId, 0]
        return self.models.ExternalNetwork.objects(*query).values_list('id', 'name')
