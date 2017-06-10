
def main(j, args, params, tags, tasklet):
    models = j.portal.tools.models.cloudbroker
    page = args.page
    modifier = j.portal.tools.html.htmlfactory.getPageModifierGridDataTables(page)

    stackid = args.getTag('stackid')
    filters = dict()
    if stackid:
        stack = models.Stack.get(stackid)
        filters['id'] = {'$in': stack.images}

    def getLocation(field, row):
        gid = field[row]
        if not gid:
            return ''
        return "[{name} ({gid})|/cbgrid/location?id={id}]".format(id=row.location.id, name=row.location.name)

    fields = [
        {'name': 'Name',
         'id': 'name',
         'value': "<a href='/cbgrid/image?id=%(id)s'>%(name)s</a>"
         },
        {'name': 'Location',
         'id': 'gid',
         'filterable': False,
         'value': getLocation
         },
        {'name': 'Type',
         'id': 'type',
         'value': 'type'
         },
        {'name': 'Status',
         'id': 'status',
         'value': 'status'
         },
        {'name': 'Size',
         'id': 'size',
         'type': 'int',
         'value': '%(size)s GiB'
         },
    ]
    tableid = modifier.addTableFromModel('cloudbroker', 'image', fields, filters)
    modifier.addSearchOptions('#%s' % tableid)

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
