
def main(j, args, params, tags, tasklet):
    import time
    models = j.portal.tools.models.cloudbroker
    params.result = (args.doc, args.doc)
    stackid = args.requestContext.params.get('id')
    healthchecks = models.Healthcheck.objects(stack=stackid)
    classmap = {'OK': 'success',
                'WARNING': 'warning',
                'EXPIRED': 'warning',
                'UNKNOWN': 'default',
                'HALTED': 'danger',
                'ERROR': 'danger'}
    colormap = {'OK': 'green', 'WARNING': 'orange', 'ERROR': 'red'}

    def colorwrap(msg):
        return "{color:%s}%s{color}" % (colormap.get(msg, 'red'), msg)

    if not stackid:
        args.doc.applyTemplate({'stack': None})
        return params
    stack = models.Stack.get(stackid)
    if not stack:
        args.doc.applyTemplate({'stack': None})
        return params

    categories = {}
    for h in healthchecks:
        healthcheck = h.to_dict()
        category = healthcheck['category'] or 'Unknown'
        categoryid = j.data.hash.md5_string(category)
        catobj = categories.setdefault(categoryid, {'status': 'OK', 'healthchecks': [], 'name': category})
        for message in healthcheck['messages']:
            status = message['flaps'][-1]['status']
            message['flaps'][-1]['lasttimetext'] = j.data.time.getSecondsInHR(abs(int(time.time()) - message['flaps'][-1]['lasttime']))
            message['label'] = classmap.get(status, 'default')
            if status in ['MISSING', 'SKIPPED']:
                continue
            if catobj['status'] == 'OK' and status != 'OK':
                catobj['status'] = status
            elif catobj['status'] == 'WARNING' and status == 'ERROR':
                catobj['status'] = 'ERROR'
        healthcheck['lasttimetext'] = j.data.time.getSecondsInHR(abs(int(time.time()) - healthcheck['lasttime']))
        healthcheck['intervaltext'] = j.data.time.getSecondsInHR(healthcheck['interval'])
        catobj['healthchecks'].append(healthcheck)

    for category in categories.values():
        category['label'] = classmap.get(category['status'], 'default')

    args.doc.applyTemplate({
        'stack': stack,
        'categories': categories,
        'colorwrap': colorwrap
    }, False)

    return params


def match(j, args, params, tags, tasklet):
    return True
