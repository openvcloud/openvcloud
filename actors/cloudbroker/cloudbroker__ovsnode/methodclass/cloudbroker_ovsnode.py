#!/usr/bin/env jspython
from js9 import j
import netaddr
import itertools
from JumpScale9Portal.portal import exceptions
from cloudbrokerlib.baseactor import BaseActor


class cloudbroker_ovsnode(BaseActor):
    def __init__(self):
        super(cloudbroker_ovsnode, self).__init__()
        self.scl = j.clients.osis.getNamespace('system')
        self.ccl = j.clients.osis.getNamespace('cloudbroker')
        self.lcl = j.clients.osis.getNamespace('libcloud')

    def decommissionNode(self, nid, **kwargs):
        ctx = kwargs['ctx']
        node = self.scl.node.get(nid)
        node.active = False
        self.scl.node.set(node)
        ipaddress = None
        for nic in node.netaddr:
            if nic["name"] == "backplane1":
                ipaddress = nic["ip"][0]
                break

        if ipaddress is None:
            raise exceptions.Error("Could not find IP for nic backplane1 on node %s" % nid)
        if 'storagedriver' not in node.roles:
            raise exceptions.BadRequest('Node with nid %s is not a storagedriver' % nid)
        query = {'$query': {'referenceId': {'$regex': ipaddress.replace('.', '\.')},
                            'status': {'$ne': 'DESTROYED'}
                            },
                 }
        disks = self.ccl.disk.search(query)[1:]
        diskids = [disk['id'] for disk in disks]
        print(diskids)
        query = {'$query': {'disks': {'$in': diskids},
                            'status': {'$ne': 'DESTROYED'}
                            },
                 }
        vms = self.ccl.vmachine.search(query)[1:]
        runningvms = []
        for idx, vm in enumerate(vms):
            vmdata = self.cb.actors.cloudapi.machines.get(machineId=vm['id'])
            if vmdata['status'] == 'RUNNING':
                ctx.events.sendMessage("Decomission OVS Node", 'Stopping Virtual Machine %s/%s' % (idx + 1, len(vms)))
                self.cb.actors.cloudapi.machines.stop(machineId=vm['id'])
                runningvms.append(vm['id'])

        storagedrivers = self.scl.node.search({'roles': 'storagedriver',
                                               'active': True})[1:]
        storagedriverips = []
        for storagedriver in storagedrivers:
            for netaddress in storagedriver['netaddr']:
                for ip, cidr in zip(netaddress['ip'], netaddress['cidr']):
                    network = netaddr.IPNetwork('%s/%s' % (ip, cidr))
                    if netaddr.IPNetwork(ipaddress).ip in network:
                        storagedriverips.append(ip)

        storagedriverips = itertools.cycle(storagedriverips)
        for vm in vms:
            storagedriverip = next(storagedriverips)
            for diskid in vm['disks']:
                disk = self.ccl.disk.get(diskid)
                disk.referenceId = disk.referenceId.replace(ipaddress, storagedriverip)
                self.ccl.disk.set(disk)
            domainkey = 'domain_%s' % (vm['referenceId'])
            xml = self.lcl.libvirtdomain.get(domainkey)
            xml = xml.replace(ipaddress, storagedriverip)
            self.lcl.libvirtdomain.set(xml, domainkey)

        vmcount = len(runningvms)
        for idx, vmid in enumerate(runningvms):
            print("Starting vm %s/%s" % (idx + 1, vmcount))
            self.cb.actors.cloudapi.machines.start(machineId=vmid)
