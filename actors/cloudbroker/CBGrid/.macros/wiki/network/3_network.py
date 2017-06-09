def main(j, args, params, tags, tasklet):
    params.result = (args.doc, args.doc)
    id = args.requestContext.params.get('id')
    gid = args.requestContext.params.get('gid')
    try:
        id = int(id)
        gid = int(gid)
    except:
        pass
    if not isinstance(gid, int) or not isinstance(id, int):
        args.doc.applyTemplate({})
        return params

    id = int(id)
    vcl = j.clients.osis.getNamespace('vfw')
    scl = j.clients.osis.getNamespace('system')
    ccl = j.clients.osis.getNamespace('cloudbroker')
    key = "%s_%s" % (gid, id)

    if not vcl.virtualfirewall.exists(key):
        # check if cloudspace with id exists
        cloudspaces = ccl.cloudspace.search({'gid': int(gid), 'networkId': int(id), 'status': 'VIRTUAL'})[1:]
        data = {}
        if cloudspaces:
            data['cloudspaceId'] = cloudspaces[0]['id']
            data['cloudspaceName'] = cloudspaces[0]['name']

        args.doc.applyTemplate(data)
        return params

    network = vcl.virtualfirewall.get(key)
    obj = network.dump()
    if scl.node.exists(obj['nid']):
        obj['nodename'] = scl.node.get(obj['nid']).name
    else:
        obj['nodename'] = str(obj['nid'])
    obj['pubips'] = ', '.join(obj['pubips'])
    obj['running'] = j.apps.cloudbroker.iaas.cb.netmgr.fw_check(network.guid)

    args.doc.applyTemplate(obj, True)
    return params


def match(j, args, params, tags, tasklet):
    return True
