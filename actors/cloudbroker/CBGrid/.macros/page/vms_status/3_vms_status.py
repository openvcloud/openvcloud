try:
    import ujson as json
except Exception:
    import json

def main(j, args, params, tags, tasklet):

    def _formatdata(vms):
        aaData = list()
        for vmachine, data in vms.items():
            itemdata = ['<a href=vmachine?id=%s>%s</a>' % (vmachine, vmachine)]
            for field in ["state", "ping", "hdtest"]:
                itemdata.append(str(data[field]))
            itemdata.append(str('<a href=grid node?id=%s>%s</a>' % (data['cpu_node_id'], data['cpu_node_name'])))
            itemdata.append(j.base.time.epoch2HRDateTime(data["epoch"]))
            aaData.append(itemdata)
        return aaData

    cl = j.clients.redis.getByInstance('system')

    vms = cl.hgetall("vmachines.status")
    vmachines = dict([(vms[i], json.loads(vms[i+1])) for i, _ in enumerate(vms) if i % 2 == 0])
    vms = _formatdata(vmachines)


    page = args.page
    modifier = j.portal.tools.html.htmlfactory.getPageModifierGridDataTables(page)

    fieldnames = ('Name', 'State', 'Pingable', 'HardDisk Test', 'Stack', 'Time')
    tableid = modifier.addTableFromData(vms, fieldnames)

    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 1, 'desc')

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
