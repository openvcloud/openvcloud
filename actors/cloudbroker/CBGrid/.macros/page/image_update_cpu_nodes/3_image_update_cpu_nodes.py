from JumpScale9Portal.portal.docgenerator.popup import Popup

def main(j, args, params, tags, tasklet):
    params.result = page = args.page
    imageId = args.getTag('imageId')
    ccl = j.clients.osis.getNamespace('cloudbroker')
    images = ccl.image.search({'id': int(imageId)})[1:]
    if images:
        image = images[0]
    else:
        image = {'id': None}

    popup = Popup(id='image_update_cpu_nodes', header='Image Availability', submit_url='/restmachine/cloudbroker/image/updateNodes')

    options = list()
    for stack in ccl.stack.search({})[1:]:
        available = image['id'] in stack.get('images', [])
        options.append((stack['name'], stack['id'], available))

    popup.addCheckboxes('Select the Stacks you want to make this Image available on', 'enabledStacks', options)
    popup.addHiddenField('imageId', imageId)
    popup.write_html(page)

    return params
