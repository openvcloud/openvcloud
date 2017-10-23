
def main(j, args, params, tags, tasklet):
    models = j.portal.tools.models.cloudbroker
    page = args.page
    modifier = j.portal.tools.html.htmlfactory.getPageModifierGridDataTables(page)

    stackid = args.getTag('stackid')
    filters = {'status': {'$ne': 'DESTROYED'}}
    if stackid:
        stack = models.Stack.get(stackid)
        filters['_id'] = {'$in': [img.id for img in stack.images]}

    fields = [
        {'name': 'Name',
         'id': 'name',
         'value': "<a href='/cbgrid/image?id=%(id)s'>%(name)s</a>"
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
