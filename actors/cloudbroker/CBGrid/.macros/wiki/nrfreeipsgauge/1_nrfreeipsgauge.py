
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
    freeips = list()
    [freeips.extend(externalnetwork['ips']) for externalnetwork in models.ExternalNetwork.objects(**qkwargs)]
    total = len(freeips) + models.Cloudspace.objects(status='DEPLOYED', **qkwargs).count()
    if total < 10:
        result += '\n{color:red}** *LESS THAN 10 FREE IPs*{color}'
    result = result % {'height': height,
                       'width': width,
                       'running': len(freeips),
                       'id': id,
                       'total': total}
    params.result = (result, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True
