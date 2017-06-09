def main(j, args, params, tags, tasklet):
    doc = args.doc
    id = args.getTag('id')
    locationid = args.getTag('locationid')
    width = args.getTag('width')
    height = args.getTag('height')
    result = "{{jgauge width:%(width)s id:%(id)s height:%(height)s val:%(running)s start:0 end:%(total)s}}"
    models = j.portal.tools.models.cloudbroker
    images = models.Image.objects(type='Windows')
    qkwargs = {'image__in': images, 'status': 'RUNNING'}
    if locationid:
        pass
    active = models.VMachine.objects(**qkwargs).count()
    total = models.VMachine.objects(status__ne='DESTROYED').count()
    result = result % {'height': height,
                       'width': width,
                       'running': active,
                       'id': id,
                       'total': total}
    params.result = (result, doc)
    return params
