from JumpScale9Portal.portal.docgenerator.popup import Popup


def main(j, args, params, tags, tasklet):
    models = j.portal.tools.models.cloudbroker
    params.result = page = args.page
    machineId = args.getTag('machineId')

    vmachine = models.VMachine.get(machineId)
    stacks = models.Stack.objects(status='ENABLED', location=vmachine.cloudspace.location, images=vmachine.image)
    cpu_nodes = [(stack.name, str(stack.id)) for stack in stacks if vmachine.stack != stack]

    popup = Popup(id='movemachine', header='Move machine to another CPU node',
                  submit_url='/restmachine/cloudbroker/machine/moveToDifferentComputeNode',
                  reload_on_success=False)
    popup.addDropdown('Target CPU Node', 'targetStackId', cpu_nodes, required=True)
    popup.addDropdown('Force (might require VM to restart)', 'force', (('No', 'false'), ('Yes', 'true'), ), required=True)
    popup.addText('Reason', 'reason', required=True)
    popup.addHiddenField('machineId', machineId)
    popup.addHiddenField('async', 'true')
    popup.write_html(page)

    return params
