def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.portal.tools.html.htmlfactory.getPageModifierGridDataTables(page)

    filters = dict()
    gid = args.getTag('gid')
    if gid:
        filters['gid'] = int(gid)

    fieldnames = ['Name', 'Network', 'Netmask', 'GID', 'VLAN', 'Free']

    def getFreeIPS(row, id):
        return str(len(row[id]))

    fieldids = ['name', 'network', 'netmask', 'gid', 'vlan', 'ips']
    fieldvalues = ['[%(name)s|External Network?networkid=%(id)s]', 'network', 'subnetmask', '[%(gid)s|grid?gid=%(gid)s]', 'vlan', getFreeIPS]
    tableid = modifier.addTableForModel('cloudbroker', 'externalnetwork', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 1, 'desc')

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
