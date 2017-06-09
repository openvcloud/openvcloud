from JumpScale9Portal.portal.docgenerator.popup import Popup

def main(j, args, params, tags, tasklet):
    #import ipdb; ipdb.set_trace()
    params.result = page = args.page
    reload = 'noreload' not in args.tags.labels
    scl = j.clients.osis.getNamespace('system')

    popup = Popup(id='createuser', header='Create User', submit_url='/restmachine/cloudbroker/user/create', reload_on_success=reload)

    options = list()
    popup.addText('Enter Username', 'username')
    popup.addText('Enter Email Address', 'emailaddress')
    popup.addHiddenField('domain', '')
    popup.addText('Enter Password', 'password', type='password',
                  placeholder='If left empty, a random password will be generated')
    for group in scl.group.search({})[1:]:
        options.append((group['id'], group['id'], False))

    popup.addCheckboxes('Select Groups', 'groups', options)
    popup.write_html(page)

    return params
