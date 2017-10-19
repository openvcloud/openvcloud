# Installing OpenvCloud

## Requirements:

### Install JumpScale9 + Portal

See JumpScale/developer install on [github](https://github.com/Jumpscale/developer)

### Install mongodb

```
js9 j.tools.prefab.local.apps.mongodb.install()
```


### Make sure you have 0-orchestrator client installed

```
export BRANCH=master
pip3 install -U "git+https://github.com/zero-os/0-orchestrator.git@${BRANCH}#subdirectory=pyclient"
```

### Add OpenvCloud contentdir and python library

1. Clone the openvcloud repo at a path of your choice
Example:
```
mkdir -p /opt/code/github/openvcloud
cd /opt/code/github/openvcloud
git clone git@github.com:openvcloud/openvcloud.git
cd openvcloud
pip3 install -e .
```

2. Add contentdir in `/opt/cfg/portals/main/config.yaml`:
`contentdirs:  '/opt/code/github/openvcloud/openvcloud/actors'`

3. Also check the [config](configuration.md) for specific OpenvCloud configuration

4. Restart portal:
```
js9 'j.tools.prefab.local.apps.portal.stop(); j.tools.prefab.local.apps.portal.start()'
```

## Initialize database

```
(gig) root@js9:/opt/code/github/openvcloud/openvcloud/scripts# python3 addlocation.py --help
usage: addlocation.py [-h] [-u URL] [-n NAME] [-p PUBLICCIDR] [-g GATEWAY]
                      [-s START] [-e END] [-v VLAN]

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     Location URL
  -n NAME, --name NAME  Location Name
  -p PUBLICCIDR, --publiccidr PUBLICCIDR
                        CIDR of external network ex. 175.12.12.0/24
  -g GATEWAY, --gateway GATEWAY
                        Gateway of external network ex. 175.12.12.1
  -s START, --start START
                        Start IP of external network ex. 175.12.12.10
  -e END, --end END     End IP of external network ex. 175.12.12.20
  -v VLAN, --vlan VLAN  VLAN for external network
```

## Install noVNC

Running installVNC.py will do the following:
1. Install noVNC using prefab9.
2. Copy apps/vncproxy/utils/websockify_ovc to the noVNC repo.
3. Start noVNC by running websockify_ovc on port 8091.
4. Create a vnc instance in our database.

For development the url passed to the script will be   `http://<ip>:8091` where <ip> is the ip of the host.

```
gig:js9:/opt/code/github/openvcloud/openvcloud/scripts$ python3 installVNC.py --help
usage: installVNC.py [-h] -u URL

optional arguments:
  -h, --help         show this help message and exit
  -u URL, --url URL  URL for accessing noVNC

  ```