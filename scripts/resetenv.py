from cloudbroker.data import Models
import netaddr


def cleanup():
    models = Models()
    models.VMachine.objects.delete()
    models.Disk.objects.delete()
    for cloudspace in models.Cloudspace.objects:
        if cloudspace.networkId:
            network = models.NetworkIds.objects(location=cloudspace.location).first()
            if cloudspace.networkId in network.usedNetworkIds:
                network.usedNetworkIds.remove(cloudspace.networkId)
            if cloudspace.networkId not in network.freeNetworkIds:
                network.freeNetworkIds.append(cloudspace.networkId)
            network.save()
        if cloudspace.externalnetworkip and cloudspace.externalnetwork:
            ip = str(netaddr.IPNetwork(cloudspace.externalnetworkip).ip)
            cloudspace.externalnetwork.ips.append(ip)
            cloudspace.externalnetwork.save()
        cloudspace.delete()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    cleanup()
