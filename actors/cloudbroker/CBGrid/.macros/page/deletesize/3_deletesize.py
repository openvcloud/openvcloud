from JumpScale9Portal.portal.docgenerator.popup import Popup


def main(j, args, params, tags, tasklet):
    models = j.portal.tools.models.cloudbroker
    params.result = page = args.page

    unused_sizes = list()
    for size in models.Size.objects:
        if models.VMachine.objects(size=size.id).count() == 0:
            unused_sizes.append(("   Memory %(memory)s,   Vcpus %(vcpus)s,   Disks %(disks)s" % size,
                                 size["id"]))

    if unused_sizes:
        popup = Popup(id='deletesize',
                      header='Delete Unused VM Size',
                      submit_url='/restmachine/cloudbroker/iaas/deleteSize')

        popup.addDropdown('Choose size', 'size_id', unused_sizes, required=True)
        popup.write_html(page)

    return params


def match(j, args, params, tags, tasklet):
    return True
