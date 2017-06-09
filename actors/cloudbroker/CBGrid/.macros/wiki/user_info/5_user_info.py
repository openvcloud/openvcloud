def main(j, args, params, tags, tasklet):
    params.result = (args.doc, args.doc)
    guid = args.requestContext.params.get('id')
    if not guid:
        args.doc.applyTemplate({})
        return params

    if not j.apps.system.usermanager.modelUser.exists(guid):
        args.doc.applyTemplate({})
        return params

    obj = j.apps.system.usermanager.modelUser.get(guid).dump()

    args.doc.applyTemplate(obj, True)
    return params
