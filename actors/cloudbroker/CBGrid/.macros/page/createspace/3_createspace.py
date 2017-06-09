from JumpScale9Portal.portal.docgenerator.popup import Popup


def main(j, args, params, tags, tasklet):
    import netaddr
    params.result = page = args.page
    accountId = args.getTag('accountId')
    ccl = j.clients.osis.getNamespace('cloudbroker')
    locations = list()
    for location in ccl.location.search({})[1:]:
        locations.append((location['name'], location['locationCode']))
    externalnetworks = list()

    def network_sort(pool):
        return '%04d_%s' % (pool['vlan'], pool['name'])

    for pool in sorted(ccl.externalnetwork.search({'accountId': {'$in': [int(accountId), 0]}})[1:], key=network_sort):
        network = netaddr.IPNetwork('{network}/{subnetmask}'.format(**pool))
        externalnetworks.append(('{name} - {network}'.format(name=pool['name'], network=network), pool['id']))

    # Placeholder that -1 means no limits are set on the cloud unit
    culimitplaceholder = 'leave empty if no limits should be set'
    popup = Popup(id='create_space', header='Create Cloud Space',
                  submit_url='/restmachine/cloudbroker/cloudspace/create')
    popup.addText('Name', 'name', required=True)
    popup.addText('Username to grant access', 'access', required=True)
    popup.addDropdown('Choose Location', 'location', locations)
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
