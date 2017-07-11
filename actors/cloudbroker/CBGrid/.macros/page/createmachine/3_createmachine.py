from JumpScale9Portal.portal.docgenerator.popup import Popup


def main(j, args, params, tags, tasklet):
    models = j.portal.tools.models.cloudbroker
    params.result = page = args.page
    cloudspaceId = args.getTag('cloudspaceId')
    actors = j.apps.cloudbroker.iaas.cb.actors.cloudapi

    cloudspace = models.Cloudspace.get(cloudspaceId)
    stacks = models.Stack.objects(location=cloudspace.location, status='ENABLED')

    images = actors.images.list(accountId=cloudspace.account.id, cloudspaceId=cloudspace.id)
    dropimages = list()
    dropstacks = list()
    dropstacks.append(('Auto', ''))

    def imageSorter(image):
        return image['type'] + image['name']

    def sortName(item):
        return item['name']

    for image in sorted(images, key=imageSorter):
        dropimages.append(("%(type)s: %(name)s" % image, image['id']))

    for stack in sorted(stacks, key=sortName):
        dropstacks.append((stack['name'], stack['id']))

    popup = Popup(id='createmachine', header='Create Machine On CPU Node',
                  submit_url='/restmachine/cloudbroker/machine/createOnStack')
    popup.addText('Machine Name', 'name', required=True)
    popup.addText('Machine Description', 'description', required=True)
    popup.addTextArea('Public SSH key to grant access one per line', 'publicsshkeys')
    popup.addDropdown('Choose Image', 'imageId', dropimages)
    popup.addNumber('Number of VCPUS', 'vcpus', required=True)
    popup.addNumber('Amount of Memory in MiB', 'memory', required=True)
    popup.addNumber('Choose Disk Size in MiB', 'disksize', required=True)
    popup.addDropdown('Choose CPU Node', 'stackId', dropstacks)
    popup.addHiddenField('cloudspaceId', cloudspaceId)
    popup.write_html(page)

    return params
