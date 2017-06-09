def main(j, args, params, tags, tasklet):
    acl = j.clients.agentcontroller.get()
    jobinfo = acl.executeJumpscript('cloudscalers', 'ovspackages', role='storagedriver', gid=j.application.whoAmI.gid)
    wiki = []
    if jobinfo['state'] == 'NOWORK':
        wiki.append("Not installed")
    elif jobinfo['state'] != 'OK':
        wiki.append("Failed to retreive OVS version.")
    else:
        for name, version in jobinfo['result'].items():
            wiki.append("* %s: %s" % (name, version))

    params.result = ('\n'.join(wiki), args.doc)
    return params


def match(j, args, params, tags, tasklet):
    return True
