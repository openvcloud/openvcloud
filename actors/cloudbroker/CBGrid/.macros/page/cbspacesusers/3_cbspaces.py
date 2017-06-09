
def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.portal.tools.html.htmlfactory.getPageModifierGridDataTables(page)

    filters = dict()
    userId = args.getTag('userId')
    userId = userId.split('_', 1)[-1]
    if not userId:
        pass

    fieldnames = ['ID', 'Name', 'ACL', 'Status', ]
    filters['acl.userGroupId'] = userId

    def makeACL(row, field):
        for acl in row['acl']:
            if acl['userGroupId'] == userId:
                return acl['right']
        return ''

    fieldids = ['id', 'name', 'acl', 'status']
    fieldvalues = ['[%(id)s|/CBGrid/cloud space?id=%(id)s]', 'name',
                   makeACL, 'status' ]
    tableid = modifier.addTableForModel('cloudbroker', 'cloudspace', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 1, 'desc')

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
