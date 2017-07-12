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

Clone the openvcloud repo at a path of your choice
Example:
```
mkdir -p /opt/code/docs.greenitglobe.com/openvcloud
cd /opt/code/docs.greenitglobe.com/openvcloud
git clone ssh://git@docs.greenitglobe.com:10022/openvcloud/openvcloud.git
cd openvcloud
pip3 install -e .
```

Add contentdir in `/optvar/cfg/portals/main/config.yaml`:  
`contentdirs:  '/opt/code/docs.greenitglobe.com/openvcloud/openvcloud/actors'`

Also check the [config](configuration.md) for specific OpenvCloud configuration

Restart portal:
```
js9 'j.tools.prefab.local.apps.portal.stop(); j.tools.prefab.local.apps.portal.start()'
```

## Initialize database

```
(gig) root@js9:/opt/code/docs.greenitglobe.com/openvcloud/openvcloud/scripts# python3 addlocation.py --help
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
