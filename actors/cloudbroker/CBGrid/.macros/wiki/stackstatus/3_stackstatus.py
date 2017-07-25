
def main(j, args, params, tags, tasklet):
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
    for message in healthchecks:
        category = message['category'] or 'Unknown'
        catobj = categories.setdefault(category, {'status': 'OK', 'messages': []})
        if catobj['status'] == 'OK' and message['status'] != 'OK':
            catobj['status'] = message['status']
        elif catobj['status'] == 'WARNING' and message['status'] == 'ERROR':
            catobj['status'] = 'ERROR'
        message['label'] = classmap.get(message['status'], 'default')
        catobj['messages'].append(message)

    for category in categories.values():
        category['label'] = classmap.get(category['status'], 'default')

    args.doc.applyTemplate({
        'stack': stack, 
        'categories': categories,
        'colorwrap': colorwrap}, True)

    return params


def match(j, args, params, tags, tasklet):
    return True
