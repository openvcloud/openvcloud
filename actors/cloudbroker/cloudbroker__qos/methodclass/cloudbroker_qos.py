from js9 import j
from JumpScale9Portal.portal.auth import auth
from JumpScale9Portal.portal import exceptions
from cloudbroker.actorlib.baseactor import BaseActor
import itertools


class cloudbroker_qos(BaseActor):
    def limitCPU(self, machineId, **kwargs):
        """
        Limit CPU quota
        param:machineId Id of the machine to limit
        result bool
        """
        raise NotImplementedError("not implemented method limitCPU")

    def limitIO(self, diskId, iops, **kwargs):
        """
        Limit IO done on a certain disk
        param:diskId Id of the disk to limit
        param:iops Max IO per second, 0 means unlimited
        result bool
        """
        return self.cb.actors.cloudapi.disks.limitIO(diskId=diskId, iops=iops)

    def limitInternalBandwith(self, cloudspaceId, machineId, machineMAC, rate, burst, **kwargs):
        """
        This will put a limit on the VIF of all VMs within the cloudspace
        Pass either cloudspaceId, machineId, or machineMac depending what you want to filter down.
        param:cloudspaceId Id of the cloudspace to limit
        param:machineId Id of the machine to limit
        param:machineMAC MAC of themachine to limit
        param:rate maximum speed in kilobytes per second, 0 means unlimited
        param:burst maximum speed in kilobytes per second, 0 means unlimited
        result bool
        """
        if [bool(machineId), bool(cloudspaceId), bool(machineMAC)].count(True) != 1:
            raise exceptions.ValueError("Either cloudspaceId, machineId, or machineMAC should be given")

        machines = []
        query = {'status': 'RUNNING'}
        if machineId:
            query['id'] = machineId
        elif machineMAC:
            query['nics.macAddress'] = machineMAC
        else:
            query['cloudspaceId'] = cloudspaceId
        machines = self.ccl.vmachine.search(query)[1:]
        stackids = list(set(vm['stackId'] for vm in machines))
        stacks = {stack['id']: stack for stack in self.ccl.stack.search({'id': {'$in': stackids}})[1:]}

        for stackId, machines in itertools.groupby(machines, lambda vm: vm['stackId']):
            stack = stacks.get(stackId)
            if stack:
                machineids = [vm['referenceId'] for vm in machines]
                args = {'machineids': machineids, 'rate': rate, 'burst': burst}
                self.acl.execute('cloudscalers', 'limitnics',
                                 gid=stack['gid'], nid=int(stack['referenceId']),
                                 args=args)
        return True

    def limitInternetBandwith(self, cloudspaceId, rate, burst, **kwargs):
        """
        This will put a limit on the outgoing traffic on the public VIF of the VFW on the physical machine
        param:cloudspaceId Id of the cloudspace to limit
        param:reate maximum speeds in kilobytes per second, 0 means unlimited
        param:burst maximum speed in kilobytes per second, 0 means unlimited
        result bool
        """
        cloudspace = self.ccl.cloudspace.get(cloudspaceId)
        vfwid = '%s_%s' % (cloudspace.gid, cloudspace.networkId)
        if not self.vcl.virtualfirewall.exists(vfwid):
            raise exceptions.NotFound("VFW for cloudspace %s does not exists" % cloudspaceId)
        vfw = self.vcl.virtualfirewall.get(vfwid)
        self.acl.executeJumpscript('cloudscalers', 'limitpublicnet', gid=vfw.gid, nid=vfw.nid,
                                   args={'networkId': cloudspace.networkId, 'rate': rate, 'burst': burst})

    def vm_events(self, event, state, name):
        """
        This will handle vm qos events and send the relevant users emails notifying them

        param:event the event to handle
        param:state the state of the event (WARNING, SUCCESS)
        param:name the name of the vm
        """
        vm = self.cb.cbcl.VMachine.objects(id=name.replace('vm-', '')).first()
        if not vm:
            return

        vm_name = vm.name

        acls = list()
        acls.extend(vm.acl)
        acls.extend(vm.cloudspace.acl)
        acls.extend(vm.cloudspace.account.acl)
        emails = set()

        for acl in acls:
            if acl.type != 'U':
                continue
            user = self.cb.checkUser(acl.userGroupId)
            if user:
                emails.update(user.emails)

        if not emails:
            return

        if event == 'VM_QUARANTINE' and state == 'WARNING':
            template = 'cloudbroker/email/qos/vm_quarantine_warning.html'
        elif event == 'VM_QUARANTINE' and state == 'SUCCESS':
            template = 'cloudbroker/email/qos/vm_quarantine.html'
        elif event == 'VM_UNQUARANTINE' and state == 'SUCCESS':
            template = 'cloudbroker/email/qos/vm_unquarantine.html'
        else:
            return

        message = j.portal.tools.server.active.templates.render(template, vm_name=vm_name)
        j.clients.email.send(emails, self.config.get('supportemail'), 'CPU fair use alert', message)

    @auth(['level1'])
    def events(self, event, state, name, **kwargs):
        """
        This will handle qos events

        param:event the event to handle
        param:state the state of the event (WARNING, SUCCESS)
        param:name the name of the affected resource
        """
        if event.startswith('VM'):
            self.vm_events(event, state, name)
