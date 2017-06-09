
def main(j, args, params, tags, tasklet):
    doc = args.doc
    id = args.getTag('id')
    gid = int(args.getTag('gid'))
    width = args.getTag('width')
    height = args.getTag('height')
    result = "{{jgauge width:%(width)s id:%(id)s height:%(height)s val:%(running)s start:0 end:%(total)s}}"
    ac = j.clients.osis.getCategory(j.core.portal.active.osis, 'cloudbroker', 'networkids')
    if ac.exists(gid):
        networkids = ac.get(gid)
        usedNetworkIds = networkids.usedNetworkIds
        freeNetworkIds = networkids.freeNetworkIds
    else:
        usedNetworkIds = []
        freeNetworkIds = []
    allnetworkids = usedNetworkIds + freeNetworkIds
    total = len(allnetworkids)
    running = len(usedNetworkIds)
    if freeNetworkIds < 10:
        result += '\n{color:red}** *LESS THAN 10 FREE NETWORK IDs*{color}'
    result = result % {'height': height,
                       'width': width,
                       'running': running,
                       'id': id,
                       'total': total}
    params.result = (result, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True
