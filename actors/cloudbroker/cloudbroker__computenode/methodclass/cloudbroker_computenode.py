from js9 import j
from JumpScale.portal.portal.auth import auth
import functools
from JumpScale9Portal.portal import exceptions
from cloudbrokerlib.baseactor import BaseActor, wrap_remote
import random
from cloudbrokerlib.gridmanager.client import getGridClient


class cloudbroker_computenode(BaseActor):
    """
    Operator actions for handling interventsions on a computenode
    """
    def __init__(self):
        super(cloudbroker_computenode, self).__init__()
        self.scl = j.clients.osis.getNamespace('system')
        self._vcl = j.clients.osis.getCategory(j.core.portal.active.osis, 'vfw', 'virtualfirewall')
        self.acl = j.clients.agentcontroller.get()

    def _getStack(self, id, gid):
        stacks = self.models.stack.search({'id': int(id), 'gid': int(gid)})[1:]
        if not stacks:
            raise exceptions.NotFound('ComputeNode with id %s not found' % id)
        return stacks[0]

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
        stack['status'] = status
        if status == 'ENABLED':
            stack['eco'] = None
        self.models.stack.set(stack)
        if status in ['ENABLED', 'MAINTENANCE', 'DECOMMISSIONED', 'ERROR']:
            nodes = self.scl.node.search({'id': int(stack['referenceId']), 'gid': stack['gid']})[1:]
            if len(nodes) > 0:
                node = nodes[0]
                node['active'] = True if status == 'ENABLED' else False
                self.scl.node.set(node)
        return stack['status']

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
    def sync(self, gid, **kwargs):
        gc = getGridClient(gid, self.models)
        nodes = gc.getNodes()
        for node, status in nodes:
            nodeid = node['id']
            res = self.models.stack.search({'referenceId': nodeid, 'gid': gid})
            if len(res) > 1:
                if status:
                    self.models.stack.updateSearch({'referenceId': nodeid, 'gid': gid, 'status': {'$in': ['INACTIVE']}}, {'$set': {'status': 'ENABLED'}})
                else:
                    self.models.stack.updateSearch({'referenceId': nodeid, 'gid': gid, 'status': {'$in': ['ENABLED', 'ERROR']}}, {'$set': {'status': 'INACTIVE'}})
            else:
                self.models.stack.set({
                    'referenceId': node['id'],
                    'status': 'ENABLED' if status else 'INACTIVE',
                    'name': node['hostname'] or node['id'],
                    'type': 'Zero-OS',
                    'descr': 'Zero-OS node',
                    'gid': gid,
                })

    @auth(['level2', 'level3'], True)
    def enableStacks(self, ids, **kwargs):
        kwargs['ctx'].events.runAsync(self._enableStacks,
                                      args=(ids, ),
                                      kwargs=kwargs,
                                      title='Enabling Stacks',
                                      success='Successfully Scheduled Stacks Enablement',
                                      error='Failed to Enable Stacks')

    def _enableStacks(self, ids, **kwargs):
        for stackid in ids:
            stack = self.models.stack.get(stackid)
            self.enable(stack.id, stack.gid, '', **kwargs)

    @auth(['level2', 'level3'], True)
    def enable(self, id, gid, message, **kwargs):
        title = "Enabling Stack"
        stack = self._getStack(id, gid)
        errorcb = functools.partial(self._errorcb, stack)
        status = self._changeStackStatus(stack, 'ENABLED')
        startmachines = []
        machines = self._get_stack_machines(id)
        # loop on machines and get those that were running (have 'start' in tags)
        for machine in machines:
            tags = j.core.tags.getObject(machine['tags'])
            if tags.labelExists("start"):
                startmachines.append(machine['id'])
        if startmachines:
            j.apps.cloudbroker.machine.startMachines(startmachines, "", ctx=kwargs['ctx'])

        kwargs['ctx'].events.runAsync(self._start_vfws,
                                      args=(stack, title, kwargs['ctx']),
                                      kwargs={},
                                      title='Starting virtual Firewalls',
                                      success='Successfully started all Virtual Firewalls',
                                      error='Failed to Start Virtual Firewalls',
                                      errorcb=errorcb)
        return status

    def _get_stack_machines(self, stackId, fields=None):
        querybuilder = {}
        if fields:
            querybuilder['$fields'] = fields
        querybuilder['$query'] = {'stackId': stackId, 'status': {'$nin': ['DESTROYED', 'ERROR']}}
        machines = self.models.vmachine.search(querybuilder)[1:]
        return machines

    @auth(['level2', 'level3'], True)
    @wrap_remote
    def maintenance(self, id, gid, vmaction, **kwargs):
        """
        :param id: stack Id
        :param gid: Grid id
        :param vmaction: what to do with vms stop or move
        :return: bool
        """
        if vmaction not in ('move', 'stop'):
            raise exceptions.BadRequest("VMAction should either be move or stop")
        stack = self._getStack(id, gid)
        errorcb = functools.partial(self._errorcb, stack)
        self._changeStackStatus(stack, "MAINTENANCE")
        title = 'Putting Node in Maintenance'
        if vmaction == 'stop':
            machines_actor = j.apps.cloudbroker.machine
            stackmachines = self._get_stack_machines(stack['id'], ['id', 'status', 'tags'])
            for machine in stackmachines:
                if machine['status'] == 'RUNNING':
                    if 'start' not in machine['tags'].split(" "):
                        machines_actor.tag(machine['id'], 'start')

            kwargs['ctx'].events.runAsync(self._stop_vfws,
                                          args=(stack, title, kwargs['ctx']),
                                          kwargs={},
                                          title='Stopping virtual Firewalls',
                                          success='Successfully Stopped all Virtual Firewalls',
                                          error='Failed to Stop Virtual Firewalls',
                                          errorcb=errorcb)

            machineIds = [machine['id'] for machine in stackmachines]
            machines_actor.stopMachines(machineIds, "", ctx=kwargs['ctx'])
        elif vmaction == 'move':
            kwargs['ctx'].events.runAsync(self._move_virtual_machines,
                                          args=(stack, title, kwargs['ctx']),
                                          kwargs={},
                                          title='Putting Node in Maintenance',
                                          success='Successfully moved all Virtual Machines',
                                          error='Failed to move Virtual Machines',
                                          errorcb=errorcb)
        return True

    def _stop_vfws(self, stack, title, ctx):
        vfws = self._vcl.search({'gid': stack['gid'],
                                 'nid': int(stack['referenceId'])})[1:]
        for vfw in vfws:
            ctx.events.sendMessage(title, 'Stopping Virtual Firewal %s' % vfw['id'])
            self.cb.netmgr.fw_stop(vfw['guid'])

    def _start_vfws(self, stack, title, ctx):
        vfws = self._vcl.search({'gid': stack['gid'],
                                 'nid': int(stack['referenceId'])})[1:]
        for vfw in vfws:
            ctx.events.sendMessage(title, 'Starting Virtual Firewal %s' % vfw['id'])
            self.cb.netmgr.fw_start(vfw['guid'])

    def _move_virtual_machines(self, stack, title, ctx):
        machines_actor = j.apps.cloudbroker.machine
        stackmachines = self.models.vmachine.search({'stackId': stack['id'],
                                                     'status': {'$nin': ['DESTROYED', 'ERROR']}
                                                     })[1:]
        othernodes = self.scl.node.search({'gid': stack['gid'], 'active': True, 'roles': 'fw'})[1:]
        if not othernodes:
            raise exceptions.ServiceUnavailable('There is no other Firewall node available to move the Virtual Firewall to')

        for machine in stackmachines:
            ctx.events.sendMessage(title, 'Moving Virtual Machine %s' % machine['name'])
            machines_actor.moveToDifferentComputeNode(machine['id'], reason='Disabling source', force=True)

        vfws = self._vcl.search({'gid': stack['gid'],
                                 'nid': int(stack['referenceId'])})[1:]
        for vfw in vfws:
            randomnode = random.choice(othernodes)
            ctx.events.sendMessage(title, 'Moving Virtual Firewal %s' % vfw['id'])
            self.cb.netmgr.fw_move(vfw['guid'], randomnode['id'])

    @auth(['level2', 'level3'], True)
    @wrap_remote
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
        var:gid int,, the grid this computenode belongs to
        var:mountpoint str,,the mountpoint of the btrfs
        var:uuid str,,if no mountpoint given, uuid is mandatory
        result: bool
        """
        raise NotImplemented()
