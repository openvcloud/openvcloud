from JumpScale9Portal.portal.docgenerator.popup import Popup

def main(j, args, params, tags, tasklet):
    params.result = page = args.page
    machineId = int(args.getTag('machineId'))
    ccl = j.clients.osis.getNamespace('cloudbroker')
    actors = j.apps.cloudbroker.iaas.cb.actors.cloudapi

    vmachine = ccl.vmachine.get(machineId)
    bootdisks = ccl.disk.search({'id': {'$in': vmachine.disks}, 'type': 'B'})[1:]
    if len(bootdisks) != 1:
        return params
    bootdisk = bootdisks[0]

    sizes = ccl.size.search({})[1:]
    dropsizes = list()

    def sizeSorter(size):
        return size['memory']

    for size in sorted(sizes, key=sizeSorter):
        if bootdisk['sizeMax'] in size['disks']:
            dropsizes.append(("VCPU %(vcpus)s / %(memory)s MB" % size, size['id']))

    if not dropsizes:
        return params

    popup = Popup(id='resizemachine', header='Resize Machine', submit_url='/restmachine/cloudbroker/machine/resize')
    popup.addDropdown('Choose Size', 'sizeId', dropsizes)
    popup.addHiddenField('machineId', machineId)
    popup.write_html(page)

    return params


def match(j, args, params, tags, tasklet):
    return True
