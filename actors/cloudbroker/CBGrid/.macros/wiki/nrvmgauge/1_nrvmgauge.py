
def main(j, args, params, tags, tasklet):
    doc = args.doc
    id = args.getTag('id')
    locationid = args.getTag('locationid')
    width = args.getTag('width')
    height = args.getTag('height')
    result = "{{jgauge width:%(width)s id:%(id)s height:%(height)s val:%(running)s start:0 end:%(total)s}}"
    if locationid:
        pass
    running = j.portal.tools.models.cloudbroker.VMachine.objects(status='RUNNING').count()
    total = j.portal.tools.models.cloudbroker.VMachine.objects(status__ne='DESTROYED').count()
    result = result % {'height': height,
                       'width': width,
                       'running': running,
                       'id': id,
                       'total': total}
    params.result = (result, doc)
    return params
