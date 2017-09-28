from JumpScale9Portal.portal.docgenerator.popup import Popup


def main(j, args, params, tags, tasklet):
    import netaddr
    import bson
    models = j.portal.tools.models.cloudbroker
    params.result = page = args.page
    accountId = args.getTag('accountId')
    locations = list()
    for location in models.Location.objects:
        locations.append((location.name, str(location.id)))
    externalnetworks = list()
    stacks = [('Auto', None)]

    for stack in models.Stack.objects(status='ENABLED'):
        stacks.append((stack['name'], stack['id']))

    def network_sort(pool):
        return '%04d_%s' % (pool.vlan, pool.name)

    poolsq = models.ExternalNetwork.objects(account__in=[bson.ObjectId(accountId), None])
    for pool in sorted(poolsq, key=network_sort):
        network = netaddr.IPNetwork('{network}/{subnetmask}'.format(**pool.to_dict()))
        externalnetworks.append(('{name} - {network}'.format(name=pool['name'], network=network), pool['id']))

    # Placeholder that -1 means no limits are set on the cloud unit
    culimitplaceholder = 'leave empty if no limits should be set'
    popup = Popup(id='create_space', header='Create Cloud Space',
                  submit_url='/restmachine/cloudbroker/cloudspace/create')
    popup.addText('Name', 'name', required=True)
    popup.addText('Username to grant access', 'access', required=True)
    popup.addDropdown('Choose Location', 'locationId', locations)
    popup.addDropdown('Choose Stack', 'stackId', stacks)
    popup.addDropdown('Choose External Network', 'externalnetworkId', externalnetworks)
    popup.addText('Max Memory Capacity (GB)', 'maxMemoryCapacity', placeholder=culimitplaceholder, type='float')
    popup.addText('Max VDisk Capacity (GB)', 'maxVDiskCapacity', placeholder=culimitplaceholder, type='number')
    popup.addText('Max Number of CPU Cores', 'maxCPUCapacity', placeholder=culimitplaceholder, type='number')
    popup.addText('Max External Network Transfer (GB)', 'maxNetworkPeerTransfer',
                  placeholder=culimitplaceholder, type='number')
    popup.addText('Max Number of Public IP Addresses', 'maxNumPublicIP', placeholder=culimitplaceholder, type='number')
    popup.addHiddenField('accountId', accountId)
    popup.write_html(page)
    return params


def match(j, args, params, tags, tasklet):
    return True
