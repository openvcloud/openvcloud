from JumpScale9 import j
from cloudbroker.data import Models
import netaddr


def setup(locationname, publiccidr, gateway, startrange, endrange, vlan):
    # ensure groups
    sysmodels = j.portal.tools.models.system
    groupnames = ['level1', 'level2', 'level3']
    for groupname in groupnames:
        if sysmodels.Group.objects(name=groupname).count() == 0:
            sysmodels.Group(name=groupname).save()
    # add groups to admin user
    adminuser = sysmodels.User.objects(name='admin').first()
    if adminuser:
        for groupname in groupnames:
            if groupname not in adminuser.groups:
                adminuser.groups.append(groupname)
        adminuser.save()

    models = Models()
    location = models.Location.objects(name=locationname).first()
    if not location:
        location = models.Location(
            name=locationname,
        )
        location.save()

    networkids = models.NetworkIds.objects(location=location).first()
    if not networkids:
        networkids = models.NetworkIds(
            location=location,
            freeNetworkIds=list(range(1, 1000))
        )
        networkids.save()

    cidr = netaddr.IPNetwork(publiccidr)
    network = str(cidr.network)
    netmask = str(cidr.netmask)
    externalnetwork = models.ExternalNetwork.objects(network=network, subnetmask=netmask, location=location).first()
    if not externalnetwork:
        externalnetwork = models.ExternalNetwork(
            name=str(cidr),
            network=network,
            subnetmask=netmask,
            gateway=gateway,
            vlan=vlan,
            location=location,
            ips=[str(ip) for ip in netaddr.IPRange(startrange, endrange)]
        )
        externalnetwork.save()

    # add default images
    # images = [
    #     ('Ubuntu 1604', 'ardb:///template:ubuntu-1604', 10, 'Linux', None, None),
    #     ('Ubuntu 1604 GIG', 'ardb:///template:ovc:ubuntu-1604', 10, 'Linux', 'gig', 'rooter'),
    #     ('Lede 17.01', 'ardb:///template:lede-1701', 1, 'Linux', None, None)
    # ]
    # disksizes = [10, 20, 50, 100, 250, 500, 1000, 2000]

    # for name, url, size, type, login, password in images:
    #     image = models.Image.objects(name=name, referenceId=url).first()
    #     if not image:
    #         image = models.Image(
    #             name=name,
    #             size=size,
    #             type=type,
    #             status='ENABLED',
    #             username=login,
    #             password=password,
    #             disks=disksizes,
    #             referenceId=url
    #         )
    #         image.save()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', help='Location Name')
    parser.add_argument('-p', '--publiccidr', help='CIDR of external network ex. 175.12.12.0/24')
    parser.add_argument('-g', '--gateway', help='Gateway of external network ex. 175.12.12.1')
    parser.add_argument('-s', '--start', help='Start IP of external network ex. 175.12.12.10')
    parser.add_argument('-e', '--end', help='End IP of external network ex. 175.12.12.20')
    parser.add_argument('-v', '--vlan', help='VLAN for external network', type=int)
    options = parser.parse_args()
    setup(options.name, options.publiccidr, options.gateway, options.start, options.end, options.vlan)
