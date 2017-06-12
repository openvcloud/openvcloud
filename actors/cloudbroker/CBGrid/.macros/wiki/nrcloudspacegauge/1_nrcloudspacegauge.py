
def main(j, args, params, tags, tasklet):
    models = j.portal.tools.models.cloudbroker
    doc = args.doc
    id = args.getTag('id')
    locationid = args.getTag('locationid')
    width = args.getTag('width')
    height = args.getTag('height')
    result = "{{jgauge width:%(width)s id:%(id)s height:%(height)s val:%(running)s start:0 end:%(total)s}}"
    qkwargs = {}
    if locationid:
        qkwargs['location'] = locationid

    total = models.Cloudspace.objects(**qkwargs).count()
    running = models.Cloudspace.objects(status__ne='DESTROYED', **qkwargs).count()
    result = result % {'height': height,
                       'width': width,
                       'running': running,
                       'id': id,
                       'total': total}
    params.result = (result, doc)
    return params
