from JumpScale9Portal.portal.docgenerator.popup import Popup


def main(j, args, params, tags, tasklet):
    models = j.portal.tools.models.cloudbroker
    params.result = page = args.page
    machineId = args.getTag('machineId')

    vmachine = models.VMachine.get(machineId)
    bootdisk = None
    for disk in vmachine.disks:
        if disk.type == 'BOOT':
            bootdisk = disk
            break
    if not bootdisk:
        return params

    sizes = models.Size.objects
    dropsizes = list()

    def sizeSorter(size):
        return size['memory']

    for size in sorted(sizes, key=sizeSorter):
        if bootdisk.size in size.disks:
            dropsizes.append(("VCPU %(vcpus)s / %(memory)s MB" % size, str(size.id)))

    if not dropsizes:
        return params

    popup = Popup(id='resizemachine', header='Resize Machine', submit_url='/restmachine/cloudbroker/machine/resize')
    popup.addDropdown('Choose Size', 'sizeId', dropsizes)
    popup.addHiddenField('machineId', machineId)
    popup.write_html(page)

    return params


def match(j, args, params, tags, tasklet):
    return True
