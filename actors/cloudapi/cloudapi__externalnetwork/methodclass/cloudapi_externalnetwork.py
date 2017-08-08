from js9 import j
from cloudbroker.actorlib.baseactor import BaseActor
from cloudbroker.data.models import to_python


class cloudapi_externalnetwork(BaseActor):

    def list(self, accountId, **kwargs):
        """
        result
        """
        query = {}
        ext_networks = []
        if accountId:
            query['account__in'] = [None, accountId, 0]
        result = self.models.ExternalNetwork.objects(*query).only('id', 'name')
        ext_networks = to_python((list(result)))
        for ext_net in ext_networks:
            ext_net.pop('ips')
        return ext_networks
