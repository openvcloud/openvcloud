def main(j, args, params, tags, tasklet):
    models = j.portal.tools.models.cloudbroker
    params.result = (args.doc, args.doc)
    imageid = args.requestContext.params.get('id')
    if not imageid:
        args.doc.applyTemplate({})
        return params

    image = models.Image.get(imageid)
    if not image:
        args.doc.applyTemplate({}, True)
        return params

    args.doc.applyTemplate({'image': image}, True)

    return params
