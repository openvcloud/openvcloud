
def main(j, args, params, tags, tasklet):
    models = j.portal.tools.models.cloudbroker
    params.result = (args.doc, args.doc)
    stackId = args.requestContext.params.get('id')
    if not stackId:
        args.doc.applyTemplate({})
        return params

    stack = models.Stack.get(stackId)
    if not stack:
        args.doc.applyTemplate({'id': None})
        return params

    args.doc.applyTemplate(stack.to_dict(), True)

    return params


def match(j, args, params, tags, tasklet):
    return True
