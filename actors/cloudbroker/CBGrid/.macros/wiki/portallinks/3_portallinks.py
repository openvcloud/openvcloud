def main(j, args, params, tags, tasklet):
    out = []
    config = j.application.config.getDictFromPrefix('portallinks')    
    for key, cfg in config.items():
        out.append("* [{name}|{url}]".format(**cfg))
    params.result = ("\n".join(out), args.doc)
    return params
    
def match(j, args, params, tags, tasklet):
    return True
