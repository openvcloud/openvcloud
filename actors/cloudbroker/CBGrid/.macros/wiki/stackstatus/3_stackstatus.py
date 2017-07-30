
def main(j, args, params, tags, tasklet):
    import time
    params.result = (args.doc, args.doc)
    from cloudbroker.actorlib.gridmanager.client import getGridClient
    models = j.portal.tools.models.cloudbroker
    classmap = {'OK': 'success',
                'WARNING': 'warning',
                'EXPIRED': 'warning',
                'UNKNOWN': 'default',
                'HALTED': 'danger',
                'ERROR': 'danger'}
    colormap = {'OK': 'green', 'WARNING': 'orange', 'ERROR': 'red'}

    def colorwrap(msg):
        return "{color:%s}%s{color}" % (colormap.get(msg, 'red'), msg) 

    stackid = args.requestContext.params.get('id')
    if not stackid:
        args.doc.applyTemplate({})
        return params
    stack = models.Stack.get(stackid)
    if not stack:
        args.doc.applyTemplate({})
        return params
        
    client = getGridClient(stack.location, models)
    healthchecks = client.rawclient.health.ListNodeHealth(stack.referenceId).json()['healthchecks']
    categories = {}
    for healthcheck in healthchecks:
        category = healthcheck['category'] or 'Unknown'
        categoryid = j.data.hash.md5_string(category)
        catobj = categories.setdefault(categoryid, {'status': 'OK', 'healthchecks': [], 'name': category})
        for message in healthcheck['messages']:
            if catobj['status'] == 'OK' and message['status'] != 'OK':
                catobj['status'] = message['status']
            elif catobj['status'] == 'WARNING' and message['status'] == 'ERROR':
                catobj['status'] = 'ERROR'
            message['label'] = classmap.get(message['status'], 'default')
        healthcheck['lasttimetext'] = j.data.time.getSecondsInHR(abs(int(time.time()) - healthcheck['lasttime']))
        healthcheck['intervaltext'] = j.data.time.getSecondsInHR(healthcheck['interval'])
        catobj['healthchecks'].append(healthcheck)

    for category in categories.values():
        category['label'] = classmap.get(category['status'], 'default')

    args.doc.applyTemplate({
        'stack': stack, 
        'categories': categories,
        'colorwrap': colorwrap}, False)

    return params


def match(j, args, params, tags, tasklet):
    return True
