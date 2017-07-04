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

    popup = Popup(id='resizemachine', header='Resize Machine', submit_url='/restmachine/cloudbroker/machine/resize')
    popup.addNumber('Number of VCPUS', 'vcpus')
    popup.addNumber('Amount of Memory in MiB', 'memory')
    popup.addHiddenField('machineId', machineId)
    popup.write_html(page)

    return params


def match(j, args, params, tags, tasklet):
    return True
