from JumpScale9Portal.portal.docgenerator.popup import Popup

def main(j, args, params, tags, tasklet):
    params.result = page = args.page
    cloudspaceId = int(args.getTag('cloudspaceId'))
    scl = j.clients.osis.getNamespace('cloudbroker')
    actors = j.apps.cloudbroker.iaas.cb.actors.cloudapi

    cloudspace = scl.cloudspace.get(cloudspaceId)
    stacks = scl.stack.search({'gid': cloudspace.gid, 'status': 'ENABLED'})[1:]

    sizes = scl.size.search({})[1:]
    images = actors.images.list(accountId=cloudspace.accountId, cloudspaceId=cloudspace.id)
    dropsizes = list()
    dropdisksizes = list()
    dropimages = list()
    dropstacks = list()
    disksizes = set()
    dropstacks.append(('Auto', 0))
    def sizeSorter(size):
        return size['memory']

    def imageSorter(image):
        return image['type'] + image['name']

    def sortName(item):
        return item['name']

    for image in sorted(images, key=imageSorter):
        dropimages.append(("%(type)s: %(name)s" % image, image['id']))

    for size in sorted(sizes, key=sizeSorter):
        disksizes.update(size['disks'])
        dropsizes.append(("%(memory)s MB,    %(vcpus)s core(s)" % size, size['id']))

    for size in sorted(disksizes):
        dropdisksizes.append(("%s GB" % size, str(size)))

    for stack in sorted(stacks, key=sortName):
        dropstacks.append((stack['name'], stack['id']))

    popup = Popup(id='createmachine', header='Create Machine On CPU Node',
                  submit_url='/restmachine/cloudbroker/machine/createOnStack')
    popup.addText('Machine Name', 'name', required=True)
    popup.addText('Machine Description', 'description', required=True)
    popup.addDropdown('Choose CPU Node', 'stackid', dropstacks)
    popup.addDropdown('Choose Image', 'imageId', dropimages)
    popup.addDropdown('Choose Size', 'sizeId', dropsizes)
    popup.addDropdown('Choose Disk Size', 'disksize', dropdisksizes)
    popup.addHiddenField('cloudspaceId', cloudspaceId)
    popup.write_html(page)

    return params


def match(j, args, params, tags, tasklet):
    return True
