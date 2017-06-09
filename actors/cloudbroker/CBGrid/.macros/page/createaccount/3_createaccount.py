from JumpScale9Portal.portal.docgenerator.popup import Popup
from collections import OrderedDict


def main(j, args, params, tags, tasklet):
    params.result = page = args.page

    # Placeholder that -1 means no limits are set on the cloud unit
    culimitplaceholder = 'leave empty if no limits should be set'
    options = OrderedDict({
        'Yes': 1,
        'No': 0
    })
    popup = Popup(id='createaccount', header='Create Account', submit_url='/restmachine/cloudbroker/account/create')
    popup.addText('Name', 'name', required=True, placeholder='Account Name')
    popup.addText('Username', 'username', required=True,
                  placeholder='Owner of account, will be created if does not exist')
    popup.addText('Email Address', 'emailaddress', required=False,
                  placeholder='User email, only required if username does not exist')
    popup.addText('Max Memory Capacity (GB)', 'maxMemoryCapacity', placeholder=culimitplaceholder, type='float')
    popup.addText('Max VDisk Capacity (GB)', 'maxVDiskCapacity', placeholder=culimitplaceholder, type='number')
    popup.addText('Max Number of CPU Cores', 'maxCPUCapacity', placeholder=culimitplaceholder, type='number')
    popup.addText('Max External Network Transfer (GB)', 'maxNetworkPeerTransfer',
                  placeholder=culimitplaceholder, type='number')
    popup.addText('Max Number of Public IP Addresses', 'maxNumPublicIP', placeholder=culimitplaceholder, type='number')
    popup.addDropdown('Email is sent when a user is granted access to a resource', 'sendAccessEmails', list(options.items()))
    popup.write_html(page)
    return params


def match(j, args, params, tags, tasklet):
    return True
