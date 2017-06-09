
def main(j, args, params, tags, tasklet):
    page = args.page
    machineId = args.getTag('machineid')
    modifier = j.portal.tools.html.htmlfactory.getPageModifierGridDataTables(page)

    if machineId:
        filters = {'machineId': int(machineId)}

    fieldnames = ['ID', 'Name', 'Bucket', 'Status', 'Storage Type']

    fieldids = ['id', 'name', 'bucket', 'status', 'storagetype']
    fieldvalues = ['[%(id)s|/CBGrid/vmexport?id=%(id)s]', 'name', 'bucket', 'status', 'storagetype']
    tableid = modifier.addTableForModel('cloudbroker', 'vmexport', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
