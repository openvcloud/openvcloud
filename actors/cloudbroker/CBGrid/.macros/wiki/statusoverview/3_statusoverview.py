def main(j, args, params, tags, tasklet):
    params.result = (args.doc, args.doc)
    from cloudbroker.actorlib.gridmanager.client import getGridClient
    models = j.portal.tools.models.cloudbroker
    stacks = models.Stack.objects
    healthchecks = {}
    colormap = {'OK': 'green', 'WARNING': 'orange', 'ERROR': 'red'}

    def colorwrap(msg):
        return "{color:%s}%s{color}" % (colormap.get(msg, 'red'), msg) 

    for location in models.Location.objects:
        client = getGridClient(location, models)
        for nodehealth in client.rawclient.health.ListNodesHealth().json():
            healthchecks[nodehealth['id']] = nodehealth

    args.doc.applyTemplate({'stacks': stacks, 'healthchecks': healthchecks, 'colorwrap': colorwrap}, True)
    return params


def match(j, args, params, tags, tasklet):
    return True
