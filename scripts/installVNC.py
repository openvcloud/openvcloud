from JumpScale9 import j
from cloudbroker.data import Models


def install(url):
    # create the vnc instance
    vnc_url = '{}/vnc_auto.html?token='.format(url)
    models = Models()
    if not models.VNC.objects(url=vnc_url).count() > 0:
        vnc = models.VNC()
        vnc.url = vnc_url
        vnc.save()

    # install noVNC
    j.tools.prefab.local.apps.novnc.install()

    # copy websockify_ovc to the noVNC repo
    noVNC = j.sal.fs.joinPaths(j.dirs.CODEDIR, "github/gigforks/noVNC/")
    from_file = j.sal.fs.joinPaths(j.dirs.CODEDIR, "github/openvcloud/openvcloud/apps/vncproxy/utils/websockify_ovc")
    to_file = j.sal.fs.joinPaths(noVNC, "utils/websockify_ovc")
    j.sal.fs.copyFile(from_file, to_file)

    # start noVNC in a tmux
    cmd = "python3 {} --host 0.0.0.0 --web {}".format(to_file, noVNC)
    pm = j.tools.prefab.local.processmanager.get("tmux")
    pm.ensure(name='noVNC', cmd=cmd)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', help='URL for accessing noVNC', required=True)
    options = parser.parse_args()
    install(options.url)
