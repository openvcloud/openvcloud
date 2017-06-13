from JumpScale9Portal.portal import exceptions
import netaddr


class Network(object):
    def __init__(self, models):
        self.models = models

    def get_ip_from_pool(self, pool):
        for ip in pool.ips:
            res = pool.update(full_result=True, pull__ips=ip)
            if res['nModified'] == 1:
                pool.reload()
                return pool, netaddr.IPNetwork("%s/%s" % (ip, pool.subnetmask))

    def getExternalIpAddress(self, location, externalnetwork=None):
        if externalnetwork is not None:
            pool = externalnetwork
            if pool.location.id != location.id:
                raise exceptions.BadRequest("ExternalNetwork does not belong to location")
            return self.get_ip_from_pool(pool)

        for pool in self.models.ExternalNetwork.objects(location=location):
            netinfo = self.get_ip_from_pool(pool)
            if netinfo:
                return netinfo

    def releaseExternalIpAddress(self, externalnetwork, ip):
        net = netaddr.IPNetwork(ip)
        externalnetwork.update(push__ips=str(net.ip))
