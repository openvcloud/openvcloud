def main(j, args, params, tags, tasklet):
    models = j.portal.tools.models.cloudbroker
    params.result = (args.doc, args.doc)
    networkid = args.requestContext.params.get('networkid')
    if not networkid:
        args.doc.applyTemplate({})
        return params

    pool = models.ExternalNetwork.get(networkid)
    if not pool:
        args.doc.applyTemplate({'externalnetwork': None}, True)
        return params

    networkinfo = j.apps.cloudbroker.iaas.getUsedIPInfo(pool)

    args.doc.applyTemplate({'externalnetwork': pool, 'networkinfo': networkinfo}, True)
    return params


def match(j, args, params, tags, tasklet):
    return True
