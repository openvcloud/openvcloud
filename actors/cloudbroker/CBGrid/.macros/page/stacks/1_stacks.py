
def main(j, args, params, tags, tasklet):
    import bson
    page = args.page
    modifier = j.portal.tools.html.htmlfactory.getPageModifierGridDataTables(page)

    imageid = args.getTag("imageid")
    locationid = args.getTag("locationid")
    filters = dict()

    if imageid:
        args.tags.tags.pop('imageid')
        filters['images'] = bson.ObjectId(imageid)
    if locationid:
        args.tags.tags.pop('locationid')
        filters['location'] = bson.ObjectId(locationid)

    for tag, val in args.tags.tags.items():
        val = args.getTag(tag)
        if val:
            filters[tag] = j.data.types.int.fromString(val) if j.data.types.int.checkString(val) else val

    def makeLocationLink(row, field):
        return '[%(name)s|/CBGrid/location?id=%(id)s]' % row.location

    fields = [
        {
            'name': 'Name',
            'value': "<a href='/cbgrid/Stack?id=%(id)s'>%(name)s</a>",
            'id': 'name'
        }, {
            'name': 'Location',
            'value': makeLocationLink,
            'id': 'location'
        }, {
            'name': 'Status',
            'value': 'status',
            'id': 'status'
        }, {
            'name': 'Reference ID',
            'value': 'referenceId',
            'id': 'referenceId'
        }, {
            'name': 'Type',
            'value': 'type',
            'id': 'type'
        }, {
            'name': 'Version',
            'value': 'version',
            'id': 'version'
        }
    ]

    tableid = modifier.addTableFromModel('cloudbroker', 'Stack', fields, filters, selectable="rows")
    modifier.addSearchOptions('#%s' % tableid)

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
