from datetime import datetime
import json
from cloudbroker.actorlib.gridmanager.client import getGridClient
from gevent import Greenlet
from js9 import j

descr = """
Collects resources
"""

def get_last_hour_val(stats, key, property='avg'):
    stats_dict = get_val(stats, key)
    value = stats_dict.get('history',{}).get('3600', {})
    last_value = value[-1].get(property, 0) if value else 0
    return last_value


def get_val(stats, key):
    if stats is None:
        return {}
    now = datetime.utcnow()
    value = stats.get(key, {})
    if value:
        if value.get('last_time', 0):
            if (now - datetime.utcfromtimestamp(value.get('last_time'))).total_seconds() / (60 * 60) < 2:
                return value
    return {}

def collect_stats():
    from cloudbroker.data import Models
    from cloudbroker import data
    import os
    import capnp
    import netaddr
    redises = {}
    models = Models()

    now = datetime.utcnow()
    month = now.month
    hour = now.hour
    day = now.day
    year = now.year
    capnp.remove_import_hook()
    schemapath = os.path.join(os.path.dirname(data.__file__), 'schemas', 'resourcemonitoring.capnp')
    cloudspace_capnp = capnp.load(schemapath)
    nodes_stats = {}

    images = {str(image.id): image.name for image in models.Image.objects}
    accounts = models.Account.objects(status__nin=['DISABLED', 'DESTROYED'])
    num_disk_map = {k: 'vd%s' % chr(v) for k, v in zip(range(26), range(ord('a'), ord('z')+1))}
    for location in models.Location.objects:
        try:
            client = getGridClient(location, models).rawclient
            nodes_ids = [ node['id'] for node in client.nodes.ListNodes().json() ]
            for node_id in nodes_ids:
                nodes_stats[node_id] = client.nodes.GetStats(node_id).json()
        except:
            continue

    for account in accounts:
        folder_name = "%s/resourcetracking/active/%s/%s/%s/%s/%s" % \
                        (j.dirs.VARDIR, str(account.id), year, month, day, hour)
        j.do.createDir(folder_name)
        cloudspaces = models.Cloudspace.objects(status__nin=['DISABLED', 'DESTROYED'], account=account)
        for cloudspace in cloudspaces:
            nodeid = cloudspace.stack.referenceId
            node_stats = nodes_stats.get(nodeid)
            if not node_stats:
                continue
            cs = cloudspace_capnp.CloudSpace.new_message()
            cs.accountId = str(account.id)
            cs.cloudSpaceId = str(cloudspace.id)

            cont_id = None
            try:
                client = getGridClient(cloudspace.location, models).rawclient
                cont_name = "vfw_{space_id}".format(space_id=str(cloudspace.id))
                cont_id = client.nodes.GetContainer(cont_name, nodeid).json().get('id')
            except:
                pass

            if cont_id:
                spacerx_key = "network.packets.rx/contm{cont_id}-1".format(cont_id=cont_id)
                spaceRX = get_last_hour_val(node_stats, spacerx_key)

                spacetx_key = "network.packets.tx/contm{cont_id}-1".format(cont_id=cont_id)
                spaceTX = get_last_hour_val(node_stats, spacetx_key)
            else:
                spaceRX = spaceTX = 0

            vms = models.VMachine.objects(status__nin=['DISABLED', 'DESTROYED'], cloudspace=cloudspace)
            machines = cs.init('machines', len(vms)+1)
            m = machines[0]
            m.type = 'gw'
            nics = m.init('networks', 1)
            nic1 = nics[0]
            nic1.tx = spaceTX
            nic1.rx = spaceRX
            nic1.type = 'space'
            for idx, vm in enumerate(vms):
                m.id = str(vm.id)
                m.type = vm.type
                m.imageName = images[str(vm.image.id)]
                m.mem = vm.memory
                m.vcpus = vm.vcpus
                cpu_key = "kvm.vcpu.time/vm-{id}".format(id=str(vm.id))
                cpu_seconds = get_last_hour_val(node_stats, cpu_key)
                m.cpuMinutes = cpu_seconds / 60

                disks_capnp = m.init('disks', len(vm.disks))
                for index, disk in enumerate(vm.disks):
                    disk_capnp = disks_capnp[index]
                    disk_capnp.id = str(disk.id)
                    disk_capnp.size = disk.size
                    disk_iops_read_key = "kvm.disk.iops.read/vm-{vm_id}.{disk_name}" .format(vm_id=str(vm.id), disk_name=num_disk_map[index])
                    val = get_val(node_stats, disk_iops_read_key)
                    disk_capnp.iopsRead = val.get('avg', 0)
                    disk_capnp.iopsReadMax = val.get('max', 0)
                    disk_iops_write_key = "kvm.disk.iops.write/vm-{vm_id}.{disk_name}" .format(vm_id=str(vm.id), disk_name=num_disk_map[index])
                    val = get_val(node_stats, disk_iops_write_key)
                    disk_capnp.iopsWrite = val.get('avg', 0)
                    disk_capnp.iopsWriteMax = val.get('max', 0)

                # Calculate Network tx and rx
                nics = m.init("networks", len(vm.nics))
                for index, nic in enumerate(vm.nics):
                    mac = nic.macAddress
                    nic_capnp = nics[index]
                    nic_capnp.type = nic.type
                    tx_key = "kvm.net.txbytes/vm-{vm_id}.{mac}".format(vm_id=str(vm.id), mac=mac)
                    rx_key = "kvm.net.rxbytes/vm-{vm_id}.{mac}".format(vm_id=str(vm.id), mac=mac)
                    nic_capnp.tx = get_last_hour_val(node_stats, tx_key)
                    nic_capnp.rx = get_last_hour_val(node_stats, rx_key)
                # write files to disk
            with open("%s/%s.bin" % (folder_name, cloudspace.id), "w+b") as f:
                cs.write(f)
    g = Greenlet(collect_stats)
    g.start_later(1800)
