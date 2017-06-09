
def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.portal.tools.html.htmlfactory.getPageModifierGridDataTables(page)

    filters = dict()

    for tag, val in args.tags.tags.items():
        val = args.getTag(tag)
        filters[tag] = val

    fieldnames = ['ID', 'Name', 'IP Addresses']

    def makeIPs(row, field):
        return str(', '.join(row[field]))

    fieldids = ['id', 'name', 'ipaddr']
    fieldvalues = ['[%(id)s|/Grid/grid node?id=%(id)s&gid=%(gid)s]', 'name', makeIPs]
    tableid = modifier.addTableForModel('system', 'node', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 1, 'desc')

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
