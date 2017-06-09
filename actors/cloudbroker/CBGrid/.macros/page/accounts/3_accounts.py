
def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.portal.tools.html.htmlfactory.getPageModifierGridDataTables(page)

    filters = dict()

    userGroupId = args.getTag('acl.userGroupId')
    if userGroupId:
        filters['acl.userGroupId'] = userGroupId

    def makeACL(row, field):
        return str('<br>'.join(['%s:%s' % (acl['userGroupId'], acl['right']) for acl in row[field]]))

    fields = [
        {
            'name': 'ID',
            'value': '[%(id)s|/CBGrid/account?id=%(id)s]',
            'id': 'id'
        },
        {
            'name': 'Name',
            'value': 'name',
            'id': 'name'
        },
        {
            'name': 'Status',
            'value': 'status',
            'id': 'status'
        },
        {
            'name': 'Access Controler List',
            'value': makeACL,
            'sortable': False,
            'filterable': False,
            'id': 'acl'
        },
        {
            'name': 'Creation Time',
            'value': modifier.makeTime,
            'id': 'creationTime',
            'type': 'date'
        },
    ]

    tableid = modifier.addTableFromModel('cloudbroker', 'account', fields, filters, selectable='rows')
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 1, 'desc')

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
