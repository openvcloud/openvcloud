
def main(j, args, params, tags, tasklet):
    params.result = (args.doc, args.doc)
    storagenodedict = dict()
#   import ipdb; ipdb.set_trace()
    scl = j.clients.osis.getNamespace('system')
    nodes = scl.node.search({"roles": "storagedriver"})[1:]
    for idx, node in enumerate(nodes):
        node["ips"] = ", ".join(node["ipaddr"])
        for nic in node["netaddr"]:
            if nic["name"] == "backplane1":
                node['publicip'] = nic["ip"][0]
                nodes[idx] = node



    storagenodedict['nodes'] = nodes


    args.doc.applyTemplate(storagenodedict, True)
    return params


def match(j, args, params, tags, tasklet):
    return True
