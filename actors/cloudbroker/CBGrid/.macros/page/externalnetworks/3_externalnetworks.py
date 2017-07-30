def main(j, args, params, tags, tasklet):
    import bson
    page = args.page
    modifier = j.portal.tools.html.htmlfactory.getPageModifierGridDataTables(page)

    filters = dict()
    locationId = args.getTag('locationId')
    if locationId:
        filters['location'] = bson.ObjectId(locationId)

    def getFreeIPS(row, id):
        return str(len(row[id]))

    def makeLocationLink(row, field):
        return '[%(name)s|/CBGrid/location?id=%(id)s]' % row.location

    fields = [
        {
            'name': 'Name',
            'value': '[%(name)s|External Network?networkid=%(id)s]',
            'id': 'name'
        }, {
            'name': 'Network',
            'value': 'network',
            'id': 'network'
        }, {
            'name': 'Subnetmask',
            'value': 'subnetmask',
            'id': 'subnetmask'
        }, {
            'name': 'Location',
            'value': makeLocationLink,
            'id': 'location'
        }, {
            'name': 'Vlan',
            'value': 'vlan',
            'id': 'vlan'
        }, {
            'name': 'Free IPs',
            'value': getFreeIPS,
            'id': 'ips'
        }
    ]
    tableid = modifier.addTableFromModel('cloudbroker', 'ExternalNetwork', fields, filters)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 1, 'desc')

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
