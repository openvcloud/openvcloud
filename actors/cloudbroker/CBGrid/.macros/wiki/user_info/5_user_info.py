def main(j, args, params, tags, tasklet):
    params.result = (args.doc, args.doc)
    userid = args.requestContext.params.get('id')
    if not userid:
        args.doc.applyTemplate({})
        return params

    user = j.portal.tools.models.system.User.get(userid)
    if not user:
        args.doc.applyTemplate({})
        return params

    args.doc.applyTemplate(user.to_dict(), True)
    return params
