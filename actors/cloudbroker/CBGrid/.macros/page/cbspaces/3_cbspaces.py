def main(j, args, params, tags, tasklet):
    import bson
    page = args.page
    modifier = j.portal.tools.html.htmlfactory.getPageModifierGridDataTables(page)

    filters = dict()
    accountId = args.getTag('accountId')
    if accountId:
        filters['account'] = bson.ObjectId(accountId)

    def makeExternalNetworkLink(row, field):
        if row[field]:
            return '[{externalnetworkip}|/CBGrid/External Network?networkid={externalnetworkId}]'.format(externalnetworkip=row.externalnetworkip, externalnetworkId=row.externalnetwork.id)
        else:
            return ''

    def makeAccountLink(row, field):
        return '[%(name)s|/CBGrid/account?id=%(id)s]' % row.account

    def makeLocationLink(row, field):
        return '[%(name)s|/CBGrid/location?id=%(id)s]' % row.location

    fields = [
        {
            'name': 'Name',
            'value': '[%(name)s|/CBGrid/Cloud Space?id=%(id)s]',
            'id': 'name'
        }, {
            'name': 'Account',
            'value': makeAccountLink,
            'filterable': False,
            'sortable': False,
            'id': 'account'
        }, {
            'name': 'Network ID',
            'value': '%(networkId)s (%(networkId)04x)',
            'id': 'networkId'
        }, {
            'name': 'Location',
            'value': makeLocationLink,
            'filterable': False,
            'sortable': False,
            'id': 'location'
        }, {
            'name': 'Status',
            'value': 'status',
            'id': 'status'
        }, {
            'name': 'External IP Address',
            'value': makeExternalNetworkLink,
            'id': 'externalnetworkip'
        }
    ]
    tableid = modifier.addTableFromModel('cloudbroker', 'cloudspace', fields, filters, selectable='rows')
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 1, 'desc')

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
