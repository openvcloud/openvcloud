from JumpScale9Portal.portal.docgenerator.popup import Popup


def main(j, args, params, tags, tasklet):
    models = j.portal.tools.models.cloudbroker
    locations = models.Location.objects.only('id', 'name')
    params.result = page = args.page

    popup = Popup(id='addexternalnetwork', header='Add External Network',
                  submit_url='/restmachine/cloudbroker/iaas/addExternalNetwork')
    popup.addText('Name', 'name', required=True)
    popup.addText('Subnet CIDR', 'subnet', required=True)
    popup.addText('Gateway IP Address', 'gateway', required=True)
    popup.addText('Start IP Address', 'startip', required=True)
    popup.addText('End IP Address', 'endip', required=True)
    popup.addNumber('VLAN Tag (leave empty if its the standard public bridge)', 'vlan', required=False)
    popup.addNumber('AccountId (make external network exclusive to this accountId otherwise leave empty)', 'accountId', required=False)
    popup.addDropdown('Choose Location', 'locationId', [(location.name, str(location.id)) for location in locations])
    popup.write_html(page)

    return params


def match(j, args, params, tags, tasklet):
    return True
