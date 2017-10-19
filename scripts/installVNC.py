from JumpScale9 import j
from cloudbroker.data import Models


def install(ip):
    # create the vnc instance
    url = 'http://{}:8091/vnc_auto.html?token='.format(ip)
    models = Models()
    if not models.VNC.find(query={"url": url}):
        vnc = models.VNC()
        vnc.url = url
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
    parser.add_argument('-i', '--ip', help='IP on which the noVNC is running', required=True)
    options = parser.parse_args()
    install(options.ip)
