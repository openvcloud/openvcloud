
def main(j, args, params, tags, tasklet):
    page = args.page
    machineId = args.getTag('machineid')
    if not machineId:
        page.addMessage('Missing machineId')
        params.result = page
        return params

    modifier = j.portal.tools.html.htmlfactory.getPageModifierGridDataTables(page)
    j.apps.actorsloader.getActor('cloudbroker', 'machine')

    def _formatdata(snapshots):
        aaData = list()
        for snapshot in snapshots:
            epoch = j.base.time.epoch2HRDateTime(snapshot['epoch']) if not snapshot['epoch']==0 else 'N/A'
            itemdata = [j.tools.text.toStr(snapshot['name']), epoch]
            aaData.append(itemdata)
        return aaData

    snapshots = j.apps.cloudbroker.machine.listSnapshots(machineId)
    if not isinstance(snapshots, list):
        page.addMessage(snapshots)
        params.result = page
        return params
        
    snapshots = _formatdata(snapshots)

    fieldnames = ('Name', 'Taken at')
    tableid = modifier.addTableFromData(snapshots, fieldnames)

    modifier.addSearchOptions('#%s' % tableid)

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
