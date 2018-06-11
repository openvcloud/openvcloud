

def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.portal.tools.html.htmlfactory.getPageModifierGridDataTables(page)

    filters = dict()
    for tag, val in args.tags.tags.items():
        val = args.getTag(tag)
        if isinstance(val, list):
            val = ', '.join(val)
        filters[tag] = val

    fields = [
        {
            'name': 'Name',
            'value': '[%(name)s|/CBGrid/location?id=%(id)s]',
            'id': 'name'
        }
    ]
    tableid = modifier.addTableFromModel('cloudbroker', 'location', fields, filters)
    modifier.addSearchOptions('#%s' % tableid)

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
