from JumpScale9Portal.portal import exceptions
from .gridmanager.client import getGridClient
import requests.exceptions
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
        nodeid, corexid = self.get_container(cloudspace)
        client = getGridClient(cloudspace.location, self.models)
        name = 'vfw_{}'.format(cloudspace.id)
        data = self.get_config(cloudspace, name)
        client.rawclient.nodes.CreateGW(data, nodeid)

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
                'srcip': portforward.fromAddr,
                'dstport': portforward.toPort,
                'dstip': portforward.toAddr
            }
            portforwards.append(rule)

        data = {
            'name': name,
            'domain': 'lan',
            'hostname': name,
            'portforwards': portforwards,
            'nics': [privatenic, publicnic]
        }
        return data

    def get_machines(self, cloudspaceId):
        return self.models.VMachine.objects(cloudspace=cloudspaceId, status__in=['RUNNING', 'PAUSED', 'HALTED'])

    def update(self, cloudspace, nodeid=None, corexid=None):
        if not nodeid or not corexid:
            nodeid, name = self.get_container(cloudspace)
        client = getGridClient(cloudspace.location, self.models)
        data = self.get_config(cloudspace, name)
        client.rawclient.nodes.UpdateGateway(data, name, nodeid)

    def get_container(self, cloudspace):
        name = 'vfw_{}'.format(cloudspace.id)
        if cloudspace.stack:
            nodeid = cloudspace.stack.referenceId
        else:
            stack = self.cb.getBestStack(cloudspace.location)
            if stack == -1:
                raise exceptions.ServiceUnavailable("Could not finder provider to deploy virtual router")
            cloudspace.modify(stack=stack)
            nodeid = stack.referenceId
        return nodeid, name

    def destroy(self, cloudspace):
        """
        """
        nodeid, corexid = self.get_container(cloudspace)
        if corexid:
            client = getGridClient(cloudspace.location, self.models)
            try:
                client.rawclient.nodes.DeleteGateway(corexid, nodeid)
            except requests.exceptions.HTTPError as e:
                # allow 404 this means the container does not exists
                if e.response.status_code != 404:
                    raise
            cloudspace.modify(status='VIRTUAL', stack=None)

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
