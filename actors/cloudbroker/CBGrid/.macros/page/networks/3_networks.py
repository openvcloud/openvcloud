def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.portal.tools.html.htmlfactory.getPageModifierGridDataTables(page)

    filters = dict()
    for tag, val in args.tags.tags.items():
        val = args.getTag(tag)
        if val and val.isdigit():
            val = int(val)
        filters[tag] = val


    fieldnames = ['GID', 'ID', 'Cloud Space ID', 'Public IPs', 'Management IP' ]

    def makeNS(row, field):
        return str(', '.join(row[field]))

    fieldids = ['gid', 'id', 'domain', 'pubips', 'host']
    fieldvalues = ['gid',
                   '[%(id)s|/CBGrid/private network?id=%(id)s&gid=%(gid)s] (%(id)04x)',
                   '[%(domain)s|/CBGrid/cloud space?id=%(domain)s]',
                   makeNS,
                   'host'
                   ]
    tableid = modifier.addTableForModel('vfw', 'virtualfirewall', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 1, 'desc')

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True