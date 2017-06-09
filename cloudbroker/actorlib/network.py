import netaddr


class Network(object):
    def __init__(self, models):
        self.models = models

    def getExternalIpAddress(self, gid, externalnetworkId=None):
        query = {'gid': gid}
        if externalnetworkId is not None:
            query['id'] = externalnetworkId
        for pool in self.models.externalnetwork.search(query)[1:]:
            for ip in pool['ips']:
                res = self.models.externalnetwork.updateSearch({'id': pool['id']},
                                                               {'$pull': {'ips': ip}})
                if res['nModified'] == 1:
                    pool = self.models.externalnetwork.get(pool['id'])
                    return pool, netaddr.IPNetwork("%s/%s" % (ip, pool.subnetmask))

    def releaseExternalIpAddress(self, externalnetworkId, ip):
        net = netaddr.IPNetwork(ip)
        self.models.externalnetwork.updateSearch({'id': externalnetworkId},
                                                 {'$addToSet': {'ips': str(net.ip)}})
