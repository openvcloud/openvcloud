def main(j, args, params, tags, tasklet):
    params.result = (args.doc, args.doc)
    from cloudbroker.actorlib.gridmanager.client import getGridClient
    models = j.portal.tools.models.cloudbroker
    stacks = models.Stack.objects
    statuses = {}
    for healthcheck in models.Healthcheck.objects:
        if not statuses.get(healthcheck.stack.referenceId):
            statuses[healthcheck.stack.referenceId] = set()
        for message in healthcheck.messages:
            statuses[healthcheck.stack.referenceId].add(message.flaps[-1].status)
    prio = ['EXPIRED', 'ERROR', 'WARNING', 'OK', 'MISSING', 'SKIPPED', 'EMPTY']
    res = {}
    for n, s in statuses.items():
        res[n] = prio.index('EMPTY')
        for k in s:
            p = prio.index(k)
            if p < res[n]:
                res[n] = p
        res[n] = prio[res[n]]

    colormap = {'OK': 'green', 'WARNING': 'orange', 'ERROR': 'red'}

    def colorwrap(msg):
        return "{color:%s}%s{color}" % (colormap.get(msg, 'red'), msg)

    args.doc.applyTemplate({'stacks': stacks, 'healthchecks': res, 'colorwrap': colorwrap}, True)
    return params


def match(j, args, params, tags, tasklet):
    return True
