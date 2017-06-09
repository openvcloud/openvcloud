
def main(j, args, params, tags, tasklet):
    params.result = (args.doc, args.doc)
    stackId = args.requestContext.params.get('id')
    try:
        stackId = int(stackId)
    except:
        pass

    if not isinstance(stackId, int):
        args.doc.applyTemplate({})
        return params

    stackId = int(stackId)
    ccl = j.clients.osis.getNamespace('cloudbroker')

    if not ccl.stack.exists(stackId):
        args.doc.applyTemplate({'id': None}, True)
        return params

    stack = ccl.stack.get(stackId).dump()
    args.doc.applyTemplate(stack, True)

    return params


def match(j, args, params, tags, tasklet):
    return True
