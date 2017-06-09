from js9 import j
from JumpScale.portal.portal.auth import auth
from JumpScale9Portal.portal import exceptions


class cloudbroker_grid(object):
    def __init__(self):
        self.models = j.clients.osis.getNamespace('cloudbroker')
        self.acl = j.clients.agentcontroller.get()

    @auth(['level1', 'level2', 'level3'])
    def purgeLogs(self, gid, age='-3d', **kwargs):
        return self.acl.executeJumpscript('cloudscalers', 'logs_purge', args={'age': age}, gid=gid, role='master', wait=False)['result']

    @auth(['level1', 'level2', 'level3'])
    def checkVMs(self, **kwargs):
        sessions = self.acl.listSessions()
        for nodeid, roles in sessions.items():
            if 'master' in roles:
                gid = int(nodeid.split('_')[0])
                self.acl.executeJumpscript('jumpscale', 'vms_check', gid=gid, role='master', wait=False)
        return 'Scheduled check on VMS'

    @auth(['level1', 'level2', 'level3'])
    def rename(self, name, gid, **kwargs):
        location = next(iter(self.models.location.search({'gid': gid})[1:]), None)
        if not location:
            raise exceptions.NotFound('Could not find location with gid %s' % gid)
        location['name'] = name
        self.models.location.set(location)
        return True

    @auth(['level1', 'level2', 'level3'])
    def add(self, name, gid, locationcode, apiUrl, **kwargs):
        location = next(iter(self.models.location.search({'gid': gid})[1:]), None)
        if location:
            raise exceptions.Conflict("Location with gid %s already exists" % gid)
        location = self.models.location.new()
        location.gid = gid
        location.apiUrl = apiUrl
        location.flag = 'black'
        location.locationCode = locationcode
        location.name = name
        self.models.location.set(location)
        return 'Location has been added successfully, do not forget to add networkids and public IPs'
