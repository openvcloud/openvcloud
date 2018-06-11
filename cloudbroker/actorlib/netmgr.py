import netaddr

DEFAULTCIDR = '192.168.112.254/24'
DOMAIN = 'lan'


class NetManager(object):
    """
    net manager

    """
    def __init__(self, cb, models):
        self.models = models
        self.cb = cb

    def create(self, cloudspace):
        """
        param:cloudspace
        """
        name = 'vfw_{}'.format(cloudspace.id)
        data = self.get_config(cloudspace, name)
        client = cloudspace.stack.get_sal()
        gw = client.gateways.get(name)
        gw.from_dict(data)
        gw.deploy()

    def get_config(self, cloudspace, name):
        externalnetwork = cloudspace.externalnetwork

        privatenic = {
            'type': 'vxlan',
            'name': 'private',
            'id': str(cloudspace.networkId),
            'config': {
                'cidr': cloudspace.networkcidr,
                'dns': []},
            'dhcpserver': {
                'nameservers': ['8.8.8.8'],
                'hosts': [],
                'domain': 'lan'
            }
        }
        publicnic = {
            'type': 'vlan',
            'id': str(externalnetwork.vlan),
            'name': 'external',
            'config': {
                'cidr': cloudspace.externalnetworkip,
                'gateway': externalnetwork.gateway,
                'dns': ['8.8.8.8']},
        }
        for machine in self.get_machines(cloudspace.id):
            cloudinit = self.cb.machine.get_cloudinit_data(machine)
            for nic in machine['nics']:
                if nic['type'] != 'vxlan':
                    continue
                hostrecord = {
                    'hostname': 'vm-{}'.format(machine['id']),
                    'macaddress': nic['macAddress'],
                    'ipaddress': nic['ipAddress'],
                    'cloudinit': cloudinit,
                }
                privatenic['dhcpserver']['hosts'].append(hostrecord)

        # if there are not dhcp server hosts drop the section
        if not privatenic['dhcpserver']['hosts']:
            privatenic.pop('dhcpserver')

        portforwards = []
        for portforward in cloudspace.forwardRules:
            rule = {
                'protocols': [portforward.protocol],
                'srcport': portforward.fromPort,
                'srcnetwork': 'external',
                'name': '{}:{}'.format(portforward.fromAddr, portforward.fromPort),
                'dstport': portforward.toPort,
                'dstip': portforward.toAddr
            }
            portforwards.append(rule)

        data = {
            'name': name,
            'domain': 'lan',
            'hostname': name,
            'portforwards': portforwards,
            'networks': [privatenic, publicnic]
        }
        return data

    def get_machines(self, cloudspaceId):
        return self.models.VMachine.objects(cloudspace=cloudspaceId, status__in=['RUNNING', 'PAUSED', 'HALTED'])

    def update(self, cloudspace):
        # currently update and create do the same thing (through sal magic)
        return self.create(cloudspace)

    def destroy(self, cloudspace):
        """
        """
        if cloudspace.stack:
            client = cloudspace.stack.get_sal()
            name = 'vfw_{}'.format(cloudspace.id)
            gw = client.gateways.get(name)
            gw.stop()
            cloudspace.stack = None
        cloudspace.status = 'VIRTUAL'
        cloudspace.save()

    def getFreeIPAddress(self, cloudspace):
        machines = self.get_machines(cloudspace.id)
        network = netaddr.IPNetwork(cloudspace.networkcidr)
        usedips = [netaddr.IPAddress(nic['ipAddress']) for vm in machines for nic in vm.nics if nic.type == 'vxlan' and nic.networkId == cloudspace.networkId]
        usedips.append(network.ip)
        ip = network.broadcast - 1
        while ip in network:
            if ip not in usedips:
                return str(ip)
            else:
                ip -= 1
        else:
            raise RuntimeError("No more free IP addresses for space")
