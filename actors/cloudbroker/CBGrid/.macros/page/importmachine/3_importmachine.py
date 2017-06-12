from JumpScale9Portal.portal.docgenerator.popup import Popup


def main(j, args, params, tags, tasklet):
    models = j.portal.tools.models.cloudbroker
    params.result = page = args.page
    cloudspaceId = args.getTag('cloudspaceId')

    cloudspace = models.Cloudspace.get(cloudspaceId)
    stacks = models.Stack.objects(location=cloudspace.location, status='ENABLED')
    sizes = list(models.Size.objects)

    dropdisksizes = list()
    dropstacks = list()
    disksizes = set()
    dropsizes = list()

    def sizeSorter(size):
        return size['memory']

    def sortName(item):
        return item['name']

    for size in sorted(disksizes):
        dropdisksizes.append(("%s GB" % size, str(size)))

    for size in sorted(sizes, key=sizeSorter):
        disksizes.update(size['disks'])
        dropsizes.append(("%(memory)s MB,    %(vcpus)s core(s)" % size, size['id']))

    for stack in sorted(stacks, key=sortName):
        dropstacks.append((stack['name'], stack['id']))

    popup = Popup(id='importmachine', header='Import Machine',
                  submit_url='/restmachine/cloudapi/machines/importOVF',
                  reload_on_success=False)
    popup.addText('Machine Name', 'name', required=True)
    popup.addText('Machine Description', 'desc', required=True)
    popup.addText('Import Link', 'link', required=True)
    popup.addText('OVF path', 'path')
    popup.addText('Username for Link', 'username')
    popup.addText('Password for Link', 'passwd', type='password')
    popup.addDropdown('Choose Memory', 'sizeId', dropsizes)
    popup.addHiddenField('cloudspaceId', cloudspaceId)
    popup.write_html(page)

    return params


def match(j, args, params, tags, tasklet):
    return True
