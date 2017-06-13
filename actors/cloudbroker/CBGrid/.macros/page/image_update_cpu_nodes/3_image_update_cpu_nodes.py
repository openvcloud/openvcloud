from JumpScale9Portal.portal.docgenerator.popup import Popup


def main(j, args, params, tags, tasklet):
    models = j.portal.tools.models.cloudbroker
    params.result = page = args.page
    imageId = args.getTag('imageId')
    image = models.Image.get(imageId)

    popup = Popup(id='image_update_cpu_nodes', header='Image Availability', submit_url='/restmachine/cloudbroker/image/updateNodes')

    options = list()
    for stack in models.Stack.objects:
        available = image in stack.images
        options.append((stack.name, str(stack.id), available))

    popup.addCheckboxes('Select the Stacks you want to make this Image available on', 'enabledStacks', options)
    popup.addHiddenField('imageId', imageId)
    popup.write_html(page)

    return params
