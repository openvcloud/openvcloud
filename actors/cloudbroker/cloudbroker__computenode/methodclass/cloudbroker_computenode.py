from js9 import j
from JumpScale9Portal.portal.auth import auth
import functools
from JumpScale9Portal.portal import exceptions
from cloudbroker.actorlib.baseactor import BaseActor
import random
from cloudbroker.actorlib.gridmanager.client import getGridClient


class cloudbroker_computenode(BaseActor):
    """
    Operator actions for handling interventsions on a computenode
    """
    def _getStack(self, id):
        stack = self.models.Stack.get(id)
        if not stack:
            raise exceptions.NotFound('ComputeNode with id %s not found' % id)
        return stack

    @auth(['level1', 'level2', 'level3'])
    def setStatus(self, id, gid, status, **kwargs):
        """
        Set different stack statusses, options are 'ENABLED(creation and actions on machines is possible)','DISABLED(Only existing machines are started)', 'OFFLINE(Machine is not available'
        param:statckid id of the stack to update
        param:status status e.g ENABLED, DISABLED, or OFFLINE
        result
        """
        statusses = ['ENABLED', 'DECOMMISSIONED', 'MAINTENANCE']
        stack = self._getStack(id, gid)
        if status not in statusses:
            return exceptions.BadRequest('Invalid status %s should be in %s' % (status, ', '.join(statusses)))
        if status == 'ENABLED':
            if stack['status'] not in ('MAINTENANCE', 'ENABLED', 'ERROR'):
                raise exceptions.PreconditionFailed("Can not enable ComputeNode in state %s" % (stack['status']))

        if status == 'DECOMMISSIONED':
            return self.decommission(id, gid, '')

        elif status == 'MAINTENANCE':
            return self.maintenance(id, gid)
        else:
            return self._changeStackStatus(stack, status)

    def _changeStackStatus(self, stack, status):
        stack.status = status
        stack.save()
        return status

    def _errorcb(self, stack, eco):
        stack['status'] = 'ERROR'
        stack['eco'] = eco.guid
        self.models.stack.set(stack)

    @auth(['level1', 'level2', 'level3'], True)
    def list(self, gid=None, **kwargs):
        query = {}
        if gid:
            query['gid'] = gid
        return self.models.stack.search(query)[1:]

    @auth(['level1', 'level2', 'level3'], True)
    def sync(self, locationId, **kwargs):
        location = self.models.Location.get(locationId)
        if not location:
            raise exceptions.BadRequest("Invalid location passed")
        gc = getGridClient(location, self.models)
        nodes = gc.getNodes()
        locationstacks = {stack.referenceId: stack for stack in self.models.Stack.objects(location=location)}
        for node, status in nodes:
            nodeid = node['id']
            stack = locationstacks.pop(nodeid, None)
            state = 'ENABLED' if status else 'INACTIVE'
            if stack:
                stack.modify(status=state, version=node['version'])
            else:
                stack = self.models.Stack(
                    name=node['hostname'] or node['id'],
                    referenceId=node['id'],
                    type='Zero-OS',
                    status=state,
                    description='Zero-OS',
                    location=location,
                    version=node['version']
                )
                stack.save()
        for node in locationstacks.values():
            node.update(status='INACTIVE')

    @auth(['level2', 'level3'], True)
    def enableStacks(self, ids, **kwargs):
        kwargs['ctx'].events.runAsync(self._enableStacks,
                                      args=(ids),
                                      kwargs=kwargs,
                                      title='Enabling Stacks',
                                      success='Successfully Scheduled Stacks Enablement',
                                      error='Failed to Enable Stacks')

    def _enableStacks(self, ids, **kwargs):
        for stackid in ids:
            stack = self.models.stack.get(stackid)
            self.enable(stack.id, stack.gid, '', **kwargs)

    @auth(['level2', 'level3'], True)
    def enable(self, id, message, **kwargs):
        title = "Enabling Stack"
        stack = self._getStack(id)
        errorcb = functools.partial(self._errorcb, stack)
        status = self._changeStackStatus(stack, 'ENABLED')
        machines = self.models.VMachine.objects(tags__contains='stopped', stack=id, status__ne='DESTROYED')
        stopped_machineIds = [machine.id for machine in machines]
        # loop on machines and get those that were running (have 'start' in tags)
        if machines:
            j.apps.cloudbroker.machine.startMachines(stopped_machineIds, "", ctx=kwargs['ctx'])

        kwargs['ctx'].events.runAsync(self._start_vfws,
                                      args=(stack, title, kwargs['ctx']),
                                      kwargs={},
                                      title='Starting virtual Firewalls',
                                      success='Successfully started all Virtual Firewalls',
                                      error='Failed to Start Virtual Firewalls',
                                      errorcb=errorcb)
        return status

    @auth(['level2', 'level3'], True)
    def upgrade(self, id, message, force, **kwargs):
        kwargs['ctx'].events.runAsync(self._upgradeStack,
                                      args=(id, message, force),
                                      kwargs=kwargs,
                                      title='upgrading Stack',
                                      success='Successfully Upgraded stack',
                                      error='Failed to Upgrade Stacks')

    def _upgradeStack(self, id, message, force, **kwargs):
        stack = self.models.Stack.get(id)
        version = self.cb.rebootStack(stack, force)
        stack.version = version
        stack.save()
        kwargs['ctx'].events.sendMessage('Stack', 'Stack %s upgraded to\n%s' % (stack.name, version))
        responseMessage = "stack %s upgraded to version :\n %s" % (id, version)
        return responseMessage

    def _get_stack_machines(self, stackId, fields=None):
        machines = self.models.VMachine.objects(status__nin=['DESTROYED', 'ERROR'], stack=stackId)
        if fields:
            return machines.only(**fields)
        return machines

    @auth(['level2', 'level3'], True)
    def maintenance(self, id, vmaction, force, **kwargs):
        """
        :param id: stack Id
        :param vmaction: what to do with vms stop or migrate
        :return: bool
        """
        title = ""
        if vmaction not in ('migrate', 'stop'):
            raise exceptions.BadRequest("VMAction should either be migrate, stop")
        machines_actor = j.apps.cloudbroker.machine
        stack = self._getStack(id)
        errorcb = functools.partial(self._errorcb, stack)
        self._changeStackStatus(stack, "MAINTENANCE")

        if self.models.Cloudspace.objects(stack=stack, status="DEPLOYED").count() > 0 and vmaction == 'move':
            raise exceptions.BadRequest("Can not put stack in maintenance when it has VFW deployed")

        if vmaction == 'stop':
            stackmachines = self._get_stack_machines(stackId=stack.id)
            for machine in stackmachines:
                if machine.status == 'RUNNING':
                    if machine.tags is not None and 'stopped' not in machine.tags.split(" "):
                        machine.tags += " %s" % (machine.id, 'stopped')
                        machine.save()

            title = 'Putting Node in Maintenance'
            kwargs['ctx'].events.runAsync(self._stop_vfws,
                                          args=(stack, title, kwargs['ctx']),
                                          kwargs={},
                                          title='Stopping virtual Firewalls',
                                          success='Successfully Stopped all Virtual Firewalls',
                                          error='Failed to Stop Virtual Firewalls',
                                          errorcb=errorcb)
            machineIds = [machine.id for machine in stackmachines]
            machines_actor.stopMachines(machineIds, "", ctx=kwargs['ctx'])
        elif vmaction == 'migrate':
            kwargs['ctx'].events.runAsync(self._move_virtual_machines,
                                          args=(stack, title, kwargs['ctx'], force),
                                          kwargs={},
                                          title='Putting Node in Maintenance',
                                          success='Successfully moved all Virtual Machines',
                                          error='Failed to move Virtual Machines',
                                          errorcb=errorcb)
        return True

    def _stop_vfws(self, stack, title, ctx):
        cloudspaces = self.models.Cloudspace.objects(stack=stack, status__in=['DEPLOYED', 'VIRTUAL'])
        for cloudspace in cloudspaces:
            ctx.events.sendMessage(title, 'Stopping Virtual Firewal %s' % cloudspace.id)
            self.cb.netmgr.destroy(cloudspace)

    def _start_vfws(self, stack, title, ctx):
        cloudspaces = self.models.Cloudspace.objects(stack=stack, status__in=['DEPLOYED', 'VIRTUAL'])

        for cloudspace in cloudspaces:
            ctx.events.sendMessage(title, 'Starting Virtual Firewal %s' % cloudspace.id)
            self.cb.netmgr.create(cloudspace)
            cloudspace.status = 'DEPLOYED'
            cloudspace.save()

    def _move_virtual_machines(self, stack, title, ctx, force=True):
        machines_actor = j.apps.cloudbroker.machine
        stackmachines = self._get_stack_machines(stackId=stack.id)
        otherstacks = self.models.Stack.objects(location=stack.location, id__ne=stack.id)
        if not otherstacks:
            raise exceptions.ServiceUnavailable('There is no other node available to move the virtual mnachines to')

        for machine in stackmachines:
            ctx.events.sendMessage(title, 'Moving Virtual Machine %s' % machine['name'])
            machines_actor.moveToDifferentComputeNode(machine['id'], reason='Disabling source', force=force)

        # TODO: moving of vfw
        # vfwspaces = self.models.Cloudspace.objects(stack=stack)
        #for vfw in vfws:
        #    randomnode = random.choice(othernodes)
        #    ctx.events.sendMessage(title, 'Moving Virtual Firewal %s' % vfw['id'])
        #    self.cb.netmgr.fw_move(vfw['guid'], randomnode['id'])

    @auth(['level2', 'level3'], True)
    def decommission(self, id, gid, message, **kwargs):
        stack = self._getStack(id, gid)
        stacks = self.models.stack.search({'gid': gid, 'status': 'ENABLED'})[1:]
        if not stacks:
            raise exceptions.PreconditionFailed("Decommissioning stack not possible when there are no other enabled stacks")
        self._changeStackStatus(stack, 'DECOMMISSIONED')
        ctx = kwargs['ctx']
        title = 'Decommissioning Node'
        errorcb = functools.partial(self._errorcb, stack)
        ctx.events.runAsync(self._move_virtual_machines,
                            args=(stack, title, ctx),
                            kwargs={},
                            title=title,
                            success='Successfully moved all Virtual Machines.</br>Decommissioning finished.',
                            error='Failed to move all Virtual Machines',
                            errorcb=errorcb)
        return True

    def btrfs_rebalance(self, name, gid, mountpoint, uuid, **kwargs):
        """
        Rebalances the btrfs filesystem
        var:name str,, name of the computenode
        var:locationId str,, the grid this computenode belongs to
        var:mountpoint str,,the mountpoint of the btrfs
        var:uuid str,,if no mountpoint given, uuid is mandatory
        result: bool
        """
        raise NotImplemented()
