
def main(j, args, params, tags, tasklet):
    doc = args.doc
    id = args.getTag('id')
    gid = args.getTag('gid')
    width = args.getTag('width')
    height = args.getTag('height')
    result = "{{jgauge width:%(width)s id:%(id)s height:%(height)s val:%(running)s start:0 end:%(total)s}}"
    ac = j.clients.osis.getCategory(j.core.portal.active.osis, 'system', 'user')
    total = ac.count()
    query = {'active': True}
    if gid:
        query['gid'] = int(gid)
    active = ac.count(query)
    result = result % {'height': height,
                       'width': width,
                       'running': active,
                       'id': id,
                       'total': total}
    params.result = (result, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True
