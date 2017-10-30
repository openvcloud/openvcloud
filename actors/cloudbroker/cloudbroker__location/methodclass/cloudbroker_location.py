from urllib import parse
from JumpScale9Portal.portal.auth import auth
from JumpScale9Portal.portal import exceptions
from cloudbroker.actorlib.baseactor import BaseActor
from cloudbroker.actorlib.gridmanager.client import getGridClient


class cloudbroker_location(BaseActor):
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
    def update(self, locationId, name, apiUrl, apiToken, **kwargs):
        location = self.models.Location.get(locationId)
        if not location:
            raise exceptions.NotFound('Could not find location with id %s' % locationId)
        update = {}
        if name:
            update['name'] = name
        if apiUrl:
            update['apiUrl'] = apiUrl
        if apiToken:
            update['apiToken'] = apiToken
        if update:
            location.modify(**update)
        return True

    @auth(['level1', 'level2', 'level3'])
    def delete(self, locationId, **kwargs):
        location = self.models.Location.get(locationId)
        if not location:
            raise exceptions.NotFound('Could not find location with id %s' % locationId)
        if self.models.Cloudspace.objects(location=location).count() > 0:
            raise exceptions.BadRequest('Can not delete location which has cloud spaces.')
        if self.models.Disk.objects(location=location).count() > 0:
            raise exceptions.BadRequest('Can not delete location which has disks.')
        if self.models.Stack.objects(location=location).count() > 0:
            raise exceptions.BadRequest('Can not delete location which has stacks.')
        self.models.ExternalNetwork.objects(location=location).delete()
        self.models.NetworkIds.objects(location=location).delete()

        client = getGridClient(location, self.models)
        client.webhook.delete(str(location.id))
        location.delete()
        return True

    @auth(['level1', 'level2', 'level3'])
    def add(self, name, apiUrl, apiToken, **kwargs):
        if self.models.Location.objects(name=name).count() > 0:
            raise exceptions.Conflict("Location with name %s already exists" % name)
        location = self.models.Location(
            name=name,
            apiUrl=apiUrl,
            apiToken=apiToken
        )
        location.save()
        self.models.NetworkIds(
            location=location,
            freeNetworkIds=list(range(1, 1000))
        ).save()

        client = getGridClient(location, self.models)
        client.webhook.create(
            str(location.id),
            ['ork'],
            parse.urljoin(self.config['portalurl'], '/restmachine/cloudbroker/qos/events'))

        return 'Location has been added successfully, do not forget to add and External Network'
