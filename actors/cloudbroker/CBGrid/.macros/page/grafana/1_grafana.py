def main(j, args, params, tags, tasklet):
    page = args.page
    from cloudbroker.actorlib.gridmanager.client import getGridClient

    cfg = {'width': args.getTag('width'), 'height': args.getTag('height'), 'location': args.getTag('location'), 'node': args.getTag('node'), 'panels': args.getTag('panels')}

    models = j.portal.tools.models.cloudbroker
    location = models.Location.get(cfg['location'])
    client = getGridClient(location, models)
    entry = '/grafana/%(location)s' % cfg
    if entry not in j.portal.tools.server.active.proxies:
        # TODO: clean up
        url = client.graph.getGraphUrl('statsdb')
        if not url.endswith(entry):
            client.graph.setGraphUrl('statsdb', '%(protocol)s://%(domain)s:%(http_port)s/{}'.format(entry))
            url = client.graph.getGraphUrl('statsdb')
        j.portal.tools.server.active.proxies[entry] = {'path': entry, 'dest': url}

    res = ''
    for panel in cfg['panels'].split(','):
        res += '<iframe'
        if cfg['width'] is not None:
            res += ' width="%s"' % cfg['width']
        if cfg['height'] is not None:
            res += ' height="%s"' % cfg['height']
        res += ' src="/grafana/%s/dashboard-solo/db/zeroos-view?refresh=5m&orgId=1&panelId=%s&theme=light&var-node=%s" frameborder="0"></iframe>\n' % (cfg['location'], panel, cfg['node'])

    page.addHTML(res)
    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
