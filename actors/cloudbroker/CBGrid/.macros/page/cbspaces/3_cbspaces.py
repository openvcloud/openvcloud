def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.portal.tools.html.htmlfactory.getPageModifierGridDataTables(page)

    filters = dict()
    accountId = args.getTag('accountId')
    if accountId:
        filters['accountId'] = int(accountId)

    def makeNetworkLink(row, field):
        if row[field]:
            return '[%(networkId)s|/CBGrid/private network?id=%(networkId)s&gid=%(gid)s]' % row
        else:
            return ''

    def makeExternalNetworkLink(row, field):
        if row[field]:
            return '[%(externalnetworkip)s|/CBGrid/External Network?networkid=%(externalnetworkId)s]' % row
        else:
            return ''
    fields = [
        {
            'name': 'ID',
            'value': '[%(id)s|/CBGrid/Cloud Space?id=%(id)s]',
            'id': 'id'
        }, {
            'name': 'Name',
            'value': 'name',
            'id': 'name'
        }, {
            'name': 'Account ID',
            'value': '[%(accountId)s|/CBGrid/account?id=%(accountId)s]',
            'id': 'accountId'
        }, {
            'name': 'Network ID',
            'value': makeNetworkLink,
            'id': 'networkId'
        }, {
            'name': 'Location Code',
            'value': 'location',
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
