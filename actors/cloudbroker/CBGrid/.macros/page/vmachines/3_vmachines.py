
def main(j, args, params, tags, tasklet):
    import bson
    models = j.portal.tools.models.cloudbroker
    import cgi
    page = args.page
    modifier = j.portal.tools.html.htmlfactory.getPageModifierGridDataTables(page)
    stackid = args.getTag("stackid")
    cloudspaceId = args.getTag("cloudspaceid")
    imageid = args.getTag('imageid')
    locationid = args.getTag('locationid')
    filters = dict()

    if stackid:
        filters['stack'] = bson.ObjectId(stackid)
    if cloudspaceId:
        filters['cloudspace'] = bson.ObjectId(cloudspaceId)
    if imageid:
        filters['image'] = bson.ObjectId(imageid)

    if locationid:
        cloudspaces = models.Cloudspace.objects(location=locationid).only('id')
        filters['cloudspace'] = {'$in': [str(cs.id) for cs in cloudspaces]}

    def stackLinkify(row, field):
        return '[%s|stack?id=%s]' % (row[field], row[field])

    def nameLinkify(row, field):
        val = row[field]
        if not isinstance(row[field], int):
            val = cgi.escape(row[field])
        return '[%s|Virtual Machine?id=%s]' % (val, row['id'])

    def spaceLinkify(row, field):
        return '[%s|cloud space?id=%s]' % (row[field], row[field])

    fields = [
        {
            'name': 'Name',
            'value': nameLinkify,
            'id': 'name'
        }, {
            'name': 'Hostname',
            'value': 'hostName',
            'id': 'hostName'
        }, {
            'name': 'Status',
            'value': 'status',
            'id': 'status'
        }, {
            'name': 'Cloud Space',
            'value': spaceLinkify,
            'id': 'cloudspaceId'
        }, {
            'name': 'Stack ID',
            'value': stackLinkify,
            'id': 'stackId'
        }
    ]

    tableid = modifier.addTableFromModel('cloudbroker', 'VMachine', fields, filters, selectable='rows')
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 1, 'desc')

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
