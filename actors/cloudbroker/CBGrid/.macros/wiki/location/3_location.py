def main(j, args, params, tags, tasklet):
    params.result = (args.doc, args.doc)
    locationid = args.requestContext.params.get('id')
    if not locationid:
        args.doc.applyTemplate({})
        return params

    models = j.portal.tools.models.cloudbroker
    location = models.Location.get(locationid)
    if not location:
        args.doc.applyTemplate({'id': None})
        return params

    args.doc.applyTemplate(location.to_dict(), True)
    return params


def match(j, args, params, tags, tasklet):
    return True
