

def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.portal.tools.html.htmlfactory.getPageModifierGridDataTables(page)

    filters = dict()
    for tag, val in args.tags.tags.items():
        val = args.getTag(tag)
        if isinstance(val, list):
            val = ', '.join(val)
        filters[tag] = val

    fieldnames = ['GID', 'Name', 'API URL']
    fieldids = ['gid', 'name', 'apiUrl']
    fieldvalues = ['[%(gid)s|/CBGrid/grid?gid=%(gid)s]', 'name', 'apiUrl']
    tableid = modifier.addTableForModel('cloudbroker', 'location', fieldids, fieldnames,
                                        fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
