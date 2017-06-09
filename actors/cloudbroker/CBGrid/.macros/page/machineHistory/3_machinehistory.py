
def main(j, args, params, tags, tasklet):
    page = args.page
    machineId = args.getTag('machineid')
    if not machineId:
        page.addMessage('Missing machineId')
        params.result = page
        return params

    modifier = j.portal.tools.html.htmlfactory.getPageModifierGridDataTables(page)
    j.apps.actorsloader.getActor('cloudbroker', 'machine')

    def _formatdata(histories):
        aaData = list()
        for history in histories:
            epoch = j.base.time.epoch2HRDateTime(history['epoch']) if not history['epoch']==0 else 'N/A'
            itemdata = [j.tools.text.toStr(history['message']), epoch]
            aaData.append(itemdata)
        return aaData

    histories = j.apps.cloudbroker.machine.getHistory(machineId)
    if not isinstance(histories, list):
        page.addMessage(histories)
        params.result = page
        return params
        
    histories = _formatdata(histories)

    fieldnames = ('Action', 'At')
    tableid = modifier.addTableFromData(histories, fieldnames)

    modifier.addSearchOptions('#%s' % tableid)

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
