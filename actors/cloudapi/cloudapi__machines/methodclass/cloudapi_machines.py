from js9 import j
from JumpScale9Portal.portal import exceptions
from cloudbroker.actorlib import authenticator, enums, network
from cloudbroker.actorlib.baseactor import BaseActor
import time
import re
import requests
import gevent


class RequireState(object):

    def __init__(self, state, msg):
        self.state = state
        self.msg = msg

    def __call__(self, func):
        def wrapper(s, **kwargs):
            machineId = int(kwargs['machineId'])
            if not s.models.vmachine.exists(machineId):
                raise exceptions.NotFound("Machine with id %s was not found" % machineId)

            machine = s.get(machineId)
            if not machine['status'] == self.state:
                raise exceptions.Conflict(self.msg)
            return func(s, **kwargs)

        return wrapper


class cloudapi_machines(BaseActor):
    """
    API Actor api, this actor is the final api a enduser uses to manage his resources

    """

    def __init__(self):
        super(cloudapi_machines, self).__init__()
        self.network = network.Network(self.models)
        self.netmgr = self.cb.netmgr

    def _updatestatus(self, machineId, actiontype, newstatus):
        """
        Update status and log action.
        """
        self.models.vmachine.updateSearch({'id': machineId}, {'$set': {'status': newstatus}})
        j.logger.log(actiontype.capitalize(), category='machine.history.ui', tags=str(machineId))

    @authenticator.auth(acl={'machine': set('X')})
    def start(self, machineId, **kwargs):
        """
        Start the machine

        :param machineId: id of the machine
        """
        machine = self.models.VMachine.get(machineId)
        if "start" in machine.tags.split(" "):
            j.apps.cloudbroker.machine.untag(machineId=machine.id, tagName="start")
        if machine.status not in ['RUNNING', 'PAUSED']:
            self.cb.machine.start(machine)
            self._updatestatus(machineId, 'start', enums.MachineStatus.running)
        return True

    @authenticator.auth(acl={'machine': set('X')})
    def stop(self, machineId, force=False, **kwargs):
        """
        Stop the machine

        :param machineId: id of the machine
        """
        machine = self.models.VMachine.get(machineId)
        if machine.status not in ['HALTED']:
            self.cb.machine.stop(machine, force)
            self._updatestatus(machineId, 'stop', enums.MachineStatus.halted)
        return True

    @authenticator.auth(acl={'machine': set('X')})
    def reboot(self, machineId, **kwargs):
        """
        Reboot the machine

        :param machineId: id of the machine
        """
        machine = self.models.VMachine.get(machineId)
        if machine.status in ['HALTED']:
            self.cb.machine.start(machine)
        elif machine.status in ['RUNNING', 'PAUSED']:
            self.cb.machine.stop(machine)
            self.cb.machine.start(machine)

        self._updatestatus(machineId, 'soft_reboot', enums.MachineStatus.running)
        return True

    @authenticator.auth(acl={'machine': set('X')})
    def reset(self, machineId, **kwargs):
        """
        Reset the machine, force reboot

        :param machineId: id of the machine
        """
        machine = self.models.VMachine.get(machineId)
        if machine.status in ['HALTED']:
            self.cb.machine.start(machine)
        elif machine.status in ['RUNNING', 'PAUSED']:
            self.cb.machine.stop(machine, force=True)
            self.cb.machine.start(machine)

        self._updatestatus(machineId, 'hard_reboot', enums.MachineStatus.running)
        return True

    @authenticator.auth(acl={'machine': set('X')})
    def pause(self, machineId, **kwargs):
        """
        Pause the machine

        :param machineId: id of the machine
        """
        machine = self.models.VMachine.get(machineId)
        if machine.status in ['RUNNING']:
            self.cb.machine.pause(machine)
            self._updatestatus(machineId, 'pause', enums.MachineStatus.paused)
        return True

    @authenticator.auth(acl={'machine': set('X')})
    def resume(self, machineId, **kwargs):
        """
        Resume the machine

        :param machineId: id of the machine
        """
        machine = self.models.VMachine.get(machineId)
        if machine.status in ['PAUSED']:
            self.cb.machine.resume(machine)
            self._updatestatus(machineId, 'resume', enums.MachineStatus.running)
        return True

    @authenticator.auth(acl={'cloudspace': set('C')})
    def addDisk(self, machineId, diskName, description, size=10, type='D', ssdSize=0, iops=2000, **kwargs):
        """
        Create and attach a disk to the machine

        :param machineId: id of the machine
        :param diskName: name of disk
        :param description: optional description
        :param size: size in GByte default=10
        :param type: (B;D;T)  B=Boot;D=Data;T=Temp default=B
        :return int, id of the disk

        """
        machine = self.models.VMachine.get(machineId)
        if len(machine.disks) >= 25:
            raise exceptions.BadRequest("Cannot create more than 25 disk on a machine")
        cloudspace = self.models.cloudspace.get(machine.cloudspaceId)
        # Validate that enough resources are available in the CU limits to add the disk
        j.apps.cloudapi.cloudspaces.checkAvailableMachineResources(cloudspace.id, vdisksize=size)
        disk = j.apps.cloudapi.disks._create(accountId=cloudspace.accountId, gid=cloudspace.gid,
                                             name=diskName, description=description, size=size,
                                             type=type, iops=iops, **kwargs)
        machine.disks.append(disk.id)
        self.models.vmachine.set(machine)
        self.cb.machine.update(machine)
        return disk.id

    @authenticator.auth(acl={'cloudspace': set('X')})
    def detachDisk(self, machineId, diskId, **kwargs):
        """
        Detach a disk from the machine

        :param machineId: id of the machine
        :param diskId: id of disk to detach
        :return: True if disk was detached successfully
        """
        machine = self.models.VMachine.get(machineId)
        diskId = int(diskId)
        if diskId not in machine.disks:
            return True
        machine.disks.remove(diskId)
        self.cb.machine.update(machine)
        self.models.vmachine.set(machine)
        return True

    @authenticator.auth(acl={'cloudspace': set('X')})
    def attachDisk(self, machineId, diskId, **kwargs):
        """
        Attach a disk to the machine

        :param machineId: id of the machine
        :param diskId: id of disk to attach
        :return: True if disk was attached successfully
        """
        provider, node, machine = self.cb.getProviderAndNode(machineId)
        diskId = int(diskId)
        if diskId in machine.disks:
            return True
        if len(machine.disks) >= 25:
            raise exceptions.BadRequest("Cannot attach more than 25 disk to a machine")
        disk = self.models.disk.get(int(diskId))
        vmachines = self.models.vmachine.search({'disks': diskId})[1:]
        if vmachines:
            if vmachines[0]["cloudspaceId"] != machine.cloudspaceId:
                # Validate that enough resources are available in the CU limits of the new cloudspace to add the disk
                j.apps.cloudapi.cloudspaces.checkAvailableMachineResources(
                    machine.cloudspaceId, vdisksize=disk.sizeMax, checkaccount=False)
            self.detachDisk(machineId=vmachines[0]['id'], diskId=diskId)
        else:
            # the disk was not attached to any machines so check if there is enough resources in the cloudspace
            j.apps.cloudapi.cloudspaces.checkAvailableMachineResources(
                machine.cloudspaceId, vdisksize=disk.sizeMax, checkaccount=False)
        volume = j.apps.cloudapi.disks.getStorageVolume(disk, provider, node)
        provider.client.attach_volume(node, volume)
        machine.disks.append(diskId)
        self.models.vmachine.set(machine)
        return True

    @authenticator.auth(acl={'account': set('C')})
    @RequireState(enums.MachineStatus.halted, 'Can only convert a stopped machine.')
    def convertToTemplate(self, machineId, templatename, **kwargs):
        """
        Create a template from the active machine

        :param machineId: id of the machine
        :param templatename: name of the template
        :param basename: snapshot id on which the template is based
        :return True if template was created
        """
        machine = self.models.VMachine.get(machineId)
        origimage = self.models.image.get(machine.imageId)
        if origimage.accountId:
            raise exceptions.Conflict("Can not make template from a machine which was created from a custom template.")
        node = self.cb.getNode(machine.referenceId)
        provider = self.cb.getProvider(machine)
        cloudspace = self.models.cloudspace.get(machine.cloudspaceId)
        image = self.models.image.new()
        image.name = templatename
        image.type = 'Custom Templates'
        image.username = machine.accounts[0].login
        image.password = machine.accounts[0].password
        m = {}
        m['stackId'] = machine.stackId
        m['disks'] = machine.disks
        m['sizeId'] = machine.sizeId
        firstdisk = self.models.disk.get(machine.disks[0])
        image.size = firstdisk.sizeMax
        image.accountId = cloudspace.accountId
        image.status = 'CREATING'
        imageid = self.models.image.set(image)[0]
        image.id = imageid
        image.gid = cloudspace.gid
        try:
            referenceId = provider.client.ex_create_template(node, templatename)
        except:
            image = self.models.image.get(imageid)
            if image.status == 'CREATING':
                image.status = 'ERROR'
                self.models.image.set(image)
            raise
        image.referenceId = referenceId
        image.status = 'CREATED'
        self.models.image.set(image)
        for stack in self.models.stack.search({'gid': cloudspace.gid})[1:]:
            stack.setdefault('images', []).append(imageid)
            self.models.stack.set(stack)
        machine.type = 'TEMPLATE'
        self.models.vmachine.set(machine)

        return imageid

    def _sendImportCompletionMail(self, emailaddress, link, success=True, error=False):
        fromaddr = self.hrd.get('instance.openvcloud.supportemail')
        if isinstance(emailaddress, list):
            toaddrs = emailaddress
        else:
            toaddrs = [emailaddress]

        success = "successfully" if success else "not successfully"
        args = {
            'error': error,
            'success': success,
            'email': emailaddress,
            'link': link,
        }

        message = j.core.portal.active.templates.render('cloudbroker/email/users/import_completion.html', **args)
        subject = j.core.portal.active.templates.render('cloudbroker/email/users/import_completion.subject.txt', **args)

        j.clients.email.send(toaddrs, fromaddr, subject, message, files=None)

    def _sendExportCompletionMail(self, emailaddress, success=True, error=False):
        fromaddr = self.hrd.get('instance.openvcloud.supportemail')
        if isinstance(emailaddress, list):
            toaddrs = emailaddress
        else:
            toaddrs = [emailaddress]

        success = "successfully" if success else "not successfully"
        args = {
            'error': error,
            'success': success,
            'email': emailaddress,
        }

        message = j.core.portal.active.templates.render('cloudbroker/email/users/export_completion.html', **args)
        subject = j.core.portal.active.templates.render('cloudbroker/email/users/export_completion.subject.txt', **args)

        j.clients.email.send(toaddrs, fromaddr, subject, message, files=None)

    def syncImportOVF(self, uploaddata, envelope, cloudspace, name, description, sizeId, callbackUrl, user):
        try:
            error = False
            userobj = j.core.portal.active.auth.getUserInfo(user)

            vm = self.models.vmachine.new()
            vm.cloudspaceId = cloudspace.id

            machine = ovf.ovf_to_model(envelope)

            vm.name = name
            vm.descr = description
            vm.sizeId = sizeId
            vm.imageId = j.apps.cloudapi.images.get_or_create_by_name('Unknown').id
            vm.creationTime = int(time.time())
            vm.updateTime = int(time.time())

            totaldisksize = 0
            bootdisk = None
            for i, diskobj in enumerate(machine['disks']):
                disk = self.models.disk.new()
                disk.gid = cloudspace.gid
                disk.order = i
                disk.accountId = cloudspace.accountId
                disk.type = 'B' if i == 0 else 'D'
                disk.sizeMax = diskobj['size'] / 1024 / 1024 / 1024
                totaldisksize += disk.sizeMax
                diskid = self.models.disk.set(disk)[0]
                disk.id = diskid
                if i == 0:
                    bootdisk = disk
                vm.disks.append(diskid)
                diskobj['id'] = diskid
                diskobj['path'] = 'disk-%i.vmdk' % i
            # Validate that enough resources are available in the CU limits to clone the machine
            size = self.models.size.get(vm.sizeId)
            j.apps.cloudapi.cloudspaces.checkAvailableMachineResources(cloudspace.id, size.vcpus,
                                                                       size.memory / 1024.0, totaldisksize)

            vm.id = self.models.vmachine.set(vm)[0]
            stack = self.cb.getBestStack(cloudspace.gid, vm.imageId)
            provider = self.cb.getProviderByStackId(stack['id'])

            machine['id'] = vm.id

            # the disk objects in the machine gets changed in the jumpscript and a guid is added to them
            jobargs = uploaddata.copy()
            jobargs['machine'] = machine
            machine = self.acl.execute('greenitglobe', 'cloudbroker_import',
                                       gid=cloudspace.gid, role='storagedriver',
                                       timeout=3600,
                                       args=jobargs)
            try:
                # TODO: custom disk sizes doesn't work
                sizeobj = provider.getSize(size, bootdisk)
                provider.client.ex_extend_disk(machine['disks'][0]['guid'], sizeobj.disk, cloudspace.gid)
                node = provider.client.ex_import(sizeobj, vm.id, cloudspace.networkId, machine['disks'])
                self.cb.machine.updateMachineFromNode(vm, node, stack['id'], sizeobj)
            except:
                self.cb.machine.cleanup(vm)
                raise
            if not callbackUrl:
                url = j.apps.cloudapi.locations.getUrl() + '/g8vdc/#/edit/%s' % vm.id
                [self._sendImportCompletionMail(email, url, success=True) for email in userobj.emails]
            else:
                requests.get(callbackUrl)
        except Exception as e:
            eco = j.errorhandler.processPythonExceptionObject(e)
            eco.process()
            error = True
            if not callbackUrl:
                [self._sendImportCompletionMail(email, '', success=False, error=error) for email in userobj.emails]
            else:
                requests.get(callbackUrl)

    def syncExportOVF(self, uploaddata, vm, provider, cloudspace, user, callbackUrl):
        try:
            error = False
            diskmapping = list()
            userobj = j.core.portal.active.auth.getUserInfo(user)
            disks = self.models.disk.search({'id': {'$in': vm.disks}})[1:]
            for disk in disks:
                diskmapping.append((j.apps.cloudapi.disks.getStorageVolume(disk, provider),
                                    "export/clonefordisk_%s" % disk['referenceId'].split('@')[1]))
            snapshotTimestamp = self.snapshot(vm.id, vm.name)
            volumes = provider.client.ex_clone_disks(diskmapping, snapshotTimestamp)
            diskguids = [volume.vdiskguid for volume in volumes]
            disknames = [volume.id.split('@')[0] for volume in volumes]
            size = self.models.size.get(vm.sizeId)
            osname = self.models.image.get(vm.imageId).name
            os = re.match('^[a-zA-Z]+', osname).group(0).lower()
            envelope = ovf.model_to_ovf({
                'name': vm.name,
                'description': vm.descr,
                'cpus': size.vcpus,
                'mem': size.memory,
                'os': os,
                'osname': osname,
                'disks': [{
                    'name': 'disk-%i.vmdk' % i,
                    'size': disk['sizeMax'] * 1024 * 1024 * 1024
                } for i, disk in enumerate(disks)]
            })
            jobargs = uploaddata.copy()
            jobargs.update({'envelope': envelope, 'disks': disknames})
            export_job = self.acl.executeJumpscript('greenitglobe', 'cloudbroker_export', gid=cloudspace.gid,
                                                    role='storagedriver', timeout=3600, args=jobargs)
            # TODO: the url to be sent to the user
            provider.client.ex_delete_disks(diskguids)
            if export_job['state'] == 'ERROR':
                raise exceptions.Error("Failed to export Virtaul Machine")
            if not callbackUrl:
                [self._sendExportCompletionMail(email, success=True) for email in userobj.emails]
            else:
                requests.get(callbackUrl)
        except:
            error = True
            if not callbackUrl:
                [self._sendExportCompletionMail(email, success=False, error=error) for email in userobj.emails]
            else:
                requests.get(callbackUrl)
            raise

    @authenticator.auth(acl={'cloudspace': set('C')})
    def importOVF(self, link, username, passwd, path, cloudspaceId, name, description, sizeId, callbackUrl, **kwargs):
        """
        Import a machine from owncloud(ovf)
        param:link WebDav link to owncloud
        param:username WebDav Username
        param:passwd WebDav Password
        param:path Path to ovf file in WebDav share
        param:cloudspaceId id of the cloudspace in which the vm should be created
        param:name name of machine
        param:description optional description
        param:sizeId the size id of the machine
        param:callbackUrl callback url so that the API caller can be notified. If this is specified the G8 will not send an email itself upon completion.
        """
        ctx = kwargs['ctx']
        user = ctx.env['beaker.session']['user']
        uploaddata = {'link': link, 'passwd': passwd, 'path': path, 'username': username}
        cloudspace = self.models.cloudspace.get(cloudspaceId)
        job = self.acl.executeJumpscript('greenitglobe', 'cloudbroker_getenvelope', gid=cloudspace.gid,
                                         role='storagedriver', args=uploaddata)
        if job['state'] == 'ERROR':
            import json
            try:
                msg = json.loads(job['result']['exceptioninfo'])['message']
            except:
                msg = 'Failed to retreive envelope'
            raise exceptions.BadRequest(msg)

        gevent.spawn(self.syncImportOVF, uploaddata, job['result'], cloudspace, name, description, sizeId, callbackUrl, user)

    @authenticator.auth(acl={'machine': set('X')})
    def exportOVF(self, link, username, passwd, path, machineId, callbackUrl, **kwargs):
        """
        Export a machine with it's disks to owncloud(ovf)
        param:link WebDav link to owncloud
        param:username WebDav Username
        param:passwd WebDav Password
        param:path Path to ovf file in WebDav share
        param:machineId id of the machine to export
        param:callbackUrl callback url so that the API caller can be notified. If this is specified the G8 will not send an email itself upon completion.
        """
        ctx = kwargs['ctx']
        user = ctx.env['beaker.session']['user']
        provider, node, vm = self.cb.getProviderAndNode(machineId)
        cloudspace = self.models.cloudspace.get(vm.cloudspaceId)
        uploaddata = {'link': link, 'passwd': passwd, 'path': path, 'username': username}
        job = self.acl.executeJumpscript('greenitglobe', 'cloudbroker_export_readme', gid=cloudspace.gid,
                                         role='storagedriver', timeout=3600, args=uploaddata)
        if job['state'] == 'ERROR':
            import json
            try:
                msg = json.loads(job['result']['exceptioninfo'])['message']
            except:
                msg = 'Failed to upload to link'
            raise exceptions.BadRequest(msg)
        gevent.spawn(self.syncExportOVF, uploaddata, vm, provider, cloudspace, user, callbackUrl)
        return True

    @authenticator.auth(acl={'machine': set('X')})
    def backup(self, machineId, backupName, **kwargs):
        """
        backup is in fact an export of the machine to a cloud system close to the IAAS system on which the machine is running
        param:machineId id of machine to backup
        param:backupName name of backup
        result int

        """
        storageparameters = {'storage_type': 'ceph',
                             'bucket': 'vmbackup',
                             'mdbucketname': 'mdvmbackup'}

        return self._export(machineId, backupName, storageparameters)

    @authenticator.auth(acl={'cloudspace': set('C')})
    def create(self, cloudspaceId, name, description, sizeId, imageId, disksize, datadisks, **kwargs):
        """
        Create a machine based on the available sizes, in a certain cloud space
        The user needs write access rights on the cloud space

        :param cloudspaceId: id of cloud space in which we want to create a machine
        :param name: name of machine
        :param description: optional description
        :param sizeId: id of the specific size
        :param imageId: id of the specific image
        :param disksize: size of base volume
        :param datadisks: list of extra data disks
        :return bool

        """
        datadisks = datadisks or []
        cloudspace = self.models.Cloudspace.get(cloudspaceId)

        size, image = self.cb.machine.validateCreate(cloudspace, name, sizeId, imageId, disksize, datadisks)
        # Validate that enough resources are available in the CU limits to create the machine
        totaldisksize = sum(datadisks + [disksize])
        j.apps.cloudapi.cloudspaces.checkAvailableMachineResources(cloudspace, size.vcpus,
                                                                   size.memory / 1024.0, totaldisksize)
        machine = self.cb.machine.createModel(name, description, cloudspace, image,
                                              size, disksize, datadisks)
        try:
            self.cb.netmgr.update(cloudspace)
            self.cb.machine.create(machine, cloudspace, image, None)
        except:
            self.cb.machine.cleanup(machine)
            raise
        return str(machine.id)

    @authenticator.auth(acl={'cloudspace': set('X')})
    def delete(self, machineId, **kwargs):
        """
        Delete the machine

        :param machineId: id of the machine
        :return True if machine was deleted successfully

        """
        vmachinemodel = self.models.VMachine.get(machineId)
        vms = self.models.vmachine.search({'cloneReference': machineId, 'status': {'$ne': 'DESTROYED'}})[1:]
        if vms:
            clonenames = ['  * %s' % vm['name'] for vm in vms]
            raise exceptions.Conflict(
                "Can not delete a Virtual Machine which has clones.\nExisting Clones Are:\n%s" % '\n'.join(clonenames))
        self. _detachExternalNetworkFromModel(vmachinemodel)
        if not vmachinemodel.status == 'DESTROYED':
            vmachinemodel.deletionTime = int(time.time())
            vmachinemodel.status = 'DESTROYED'
            self.models.vmachine.set(vmachinemodel)

        tags = str(machineId)
        j.logger.log('Deleted', category='machine.history.ui', tags=tags)
        try:
            j.apps.cloudapi.portforwarding.deleteByVM(vmachinemodel)
        except Exception as e:
            j.errorhandler.processPythonExceptionObject(
                e, message="Failed to delete portforwardings for vm with id %s" % machineId)
        except exceptions.BaseError as berror:
            j.errorhandler.processPythonExceptionObject(
                berror, message="Failed to delete pf for vm with id %s can not apply config" % machineId)
        self.cb.machine.destroy(vmachinemodel)

        for disk in self.models.disk.search({'id': {'$in': vmachinemodel.disks}})[1:]:
            disk['status'] = 'DESTROYED'
            self.models.disk.set(disk)

        return True

    @authenticator.auth(acl={'machine': set('R')})
    def get(self, machineId, **kwargs):
        """
        Get information from a certain object.
        This contains all information about the machine.
        param:machineId id of machine
        result

        """
        machine = self.models.VMachine.get(machineId)
        if machine.status in ['DESTROYED', 'DESTROYING']:
            raise exceptions.NotFound('Machine %s not found' % machineId)
        locked = False
        storage = sum(disk.size for disk in machine.disks)
        disks = [disk.to_dict() for disk in machine.disks]
        machinedict = machine.to_dict()
        osImage = machine.image.name
        updateTime = machine.updateTime
        creationTime = machine.creationTime
        acl = list()
        machine_acl = authenticator.auth().getVMachineAcl(machine)
        for _, ace in machine_acl.items():
            acl.append({'userGroupId': ace['userGroupId'], 'type': ace['type'], 'canBeDeleted': ace[
                       'canBeDeleted'], 'right': ''.join(sorted(ace['right'])), 'status': ace['status']})
        return {'id': str(machine.id), 'cloudspaceid': str(machine.cloudspace.id), 'acl': acl, 'disks': disks,
                'name': machine.name, 'description': machine.description, 'hostname': machine.hostName,
                'status': machine.status, 'imageid': str(machine.image.id), 'osImage': osImage, 'sizeid': str(machine.size.id),
                'interfaces': machinedict['nics'], 'storage': storage, 'accounts': machinedict['accounts'], 'locked': locked,
                'updateTime': updateTime, 'creationTime': creationTime}

    # Authentication (permissions) are checked while retrieving the machines
    def list(self, cloudspaceId, **kwargs):
        """
        List the deployed machines in a space. Filtering based on status is possible
        :param cloudspaceId: id of cloud space in which machine exists @tags: optional
        :return list of dict with each element containing the machine details

        """
        ctx = kwargs['ctx']
        if not cloudspaceId:
            raise exceptions.BadRequest('Please specify a cloudsapce ID.')
        fields = ['id', 'referenceId', 'cloudspace', 'hostName', 'image', 'name',
                  'nics', 'size', 'status', 'stack', 'disks', 'creationTime', 'updateTime']

        user = ctx.env['beaker.session']['user']
        userobj = j.portal.tools.server.active.auth.getUserInfo(user)
        groups = userobj.groups
        cloudspace = self.models.Cloudspace.get(cloudspaceId)
        auth = authenticator.auth()
        acl = auth.expandAclFromCloudspace(user, groups, cloudspace)
        q = {"cloudspace": cloudspace.id,
             "status": {"$nin": ["DESTROYED", "ERROR", ""]},
             "type": "VIRTUAL"}
        if 'R' not in acl and 'A' not in acl:
            q['acl.userGroupId'] = user

        results = self.models.VMachine.find(q).only(*fields)
        machines = []
        for machine in results:
            res = machine.to_dict()
            size = sum(d.size for d in machine.disks)
            res['storage'] = size
            machines.append(res)
        return machines

    @authenticator.auth(acl={'machine': set('C')})
    def snapshot(self, machineId, name, **kwargs):
        """
        Take a snapshot of the machine

        :param machineId: id of the machine to snapshot
        :param name: name to give snapshot
        :return the timestamp
        """
        machine = self.models.VMachine.get(machineId)
        for disk in machine.disks:
            snapshot = self.models.Snapshot(
                timestamp=int(time.time()),
                label=name
            )
            disk.update(push__snapshots=snapshot)

    @authenticator.auth(acl={'machine': set('R')})
    def listSnapshots(self, machineId, **kwargs):
        """
        List the snapshots of the machine

        :param machineId: id of the machine
        :return: list with the available snapshots
        """
        snapshots = set()
        out = list()
        machine = self.models.VMachine.get(machineId)
        for disk in machine.disks:
            for snapshot in disk.snapshots:
                data = {(snapshot.label, snapshot.timestamp)}
                snapshots.update(data)

        for ss in snapshots:
            out.append({'label': ss[0], 'timestamp': ss[1]})
        return out

    @authenticator.auth(acl={'machine': set('X')})
    def deleteSnapshot(self, machineId, epoch, **kwargs):
        """
        Delete a snapshot of the machine

        :param machineId: id of the machine
        :param epoch: epoch time of snapshot
        """
        machine = self.models.VMachine.get(machineId)
        for disk in machine.disks:
            disk.update(pull__snapshots__timestamp=epoch)

    @authenticator.auth(acl={'machine': set('X')})
    @RequireState(enums.MachineStatus.halted, 'A snapshot can only be rolled back to a stopped Machine')
    def rollbackSnapshot(self, machineId, epoch, **kwargs):
        """
        Rollback a snapshot of the machine

        :param machineId: id of the machine
        :param epoch: epoch time of snapshot
        """
        machine = self.models.machine.get(machineId)
        self.cb.machine.rollback(machine, epoch)
        tags = str(machineId)
        j.logger.log('Snapshot rolled back', category='machine.history.ui', tags=tags)
        return

    @authenticator.auth(acl={'machine': set('C')})
    def update(self, machineId, name=None, description=None, **kwargs):
        """
        Change basic properties of a machine
        Name, description can be changed with this action.

        :param machineId: id of the machine
        :param name: name of the machine
        :param description: description of the machine
        """
        machine = self.models.VMachine.get(machineId)
        if name:
            self.cb.machine.assertName(machine.cloudspaceId, name)
            machine.name = name
        if description:
            machine.descr = description
        return self.models.vmachine.set(machine)[0]

    @authenticator.auth(acl={'machine': set('R')})
    def getConsoleUrl(self, machineId, **kwargs):
        """
        Get url to connect to console

        :param machineId: id of the machine to connect to console
        :return one time url used to connect ot console

        """
        machine = self.models.VMachine.get(machineId)
        if machine.status in ['DESTROYED', 'DESTROYING']:
            raise exceptions.NotFound('Machine %s not found' % machineId)
        if machine.status != enums.MachineStatus.running:
            return None
        return self.cb.machine.getConsoleUrl(machine)

    @authenticator.auth(acl={'cloudspace': set('C')})
    @RequireState(enums.MachineStatus.halted, 'A clone can only be taken from a stopped Virtual Machine')
    def clone(self, machineId, name, cloudspaceId=None, snapshotTimestamp=None, **kwargs):
        """
        Clone the machine

        :param machineId: id of the machine to clone
        :param name: name of the cloned machine
        :return id of the new cloned machine
        """
        machine = self.models.VMachine.get(machineId)
        if cloudspaceId is None:
            cloudspace = self.models.cloudspace.get(machine.cloudspaceId)
        else:
            arg_cloudspace = self.models.cloudspace.get(cloudspaceId)
            if not arg_cloudspace:
                raise exceptions.NotFound("Cloudspace %s not found" % cloudspaceId)
            vm_cloudspace = self.models.cloudspace.get(machine.cloudspaceId)
            if arg_cloudspace.accountId != vm_cloudspace.accountId:
                raise exceptions.MethodNotAllowed('Cannot clone a machine from a different account.')
            cloudspace = arg_cloudspace

        if machine.cloneReference:
            raise exceptions.MethodNotAllowed('Cannot clone a cloned machine.')

        # validate capacity of the vm
        size = self.models.size.get(machine.sizeId)
        query = {'$fields': ['id', 'sizeMax'],
                 '$query': {'id': {'$in': machine.disks}}}
        totaldisksize = sum([disk['sizeMax'] for disk in self.models.disk.search(query)[1:]])
        j.apps.cloudapi.cloudspaces.checkAvailableMachineResources(cloudspace.id, size.vcpus,
                                                                   size.memory / 1024.0, totaldisksize)

        # clone vm model
        self.cb.machine.assertName(machine.cloudspaceId, name)
        clone = self.models.vmachine.new()
        clone.cloudspaceId = cloudspace.id
        clone.name = name
        clone.descr = machine.descr
        clone.sizeId = machine.sizeId
        clone.imageId = machine.imageId
        clone.cloneReference = machine.id
        clone.acl = machine.acl
        clone.creationTime = int(time.time())
        clone.type = 'VIRTUAL'
        for account in machine.accounts:
            newaccount = clone.new_account()
            newaccount.login = account.login
            newaccount.password = account.password
        clone.id = self.models.vmachine.set(clone)[0]

        diskmapping = []

        _, node, machine = self.cb.getProviderAndNode(machineId)
        stack = self.cb.getBestStack(cloudspace.gid, machine.imageId)
        provider = self.cb.getProviderByStackId(stack['id'])

        totaldisksize = 0
        for diskId in machine.disks:
            origdisk = self.models.disk.get(diskId)
            clonedisk = self.models.disk.new()
            clonedisk.name = origdisk.name
            clonedisk.gid = origdisk.gid
            clonedisk.order = origdisk.order
            clonedisk.accountId = origdisk.accountId
            clonedisk.type = origdisk.type
            clonedisk.descr = origdisk.descr
            clonedisk.sizeMax = origdisk.sizeMax
            clonediskId = self.models.disk.set(clonedisk)[0]
            clone.disks.append(clonediskId)
            volume = j.apps.cloudapi.disks.getStorageVolume(origdisk, provider, node)
            if clonedisk.type == 'B':
                name = 'vm-{0}/bootdisk-vm-{0}'.format(clone.id)
            else:
                name = 'volumes/volume_{}'.format(clonediskId)
            diskmapping.append((volume, name))
            totaldisksize += clonedisk.sizeMax

        clone.id = self.models.vmachine.set(clone)[0]
        size = self.cb.machine.getSize(provider, clone)
        if not snapshotTimestamp:
            snapshotTimestamp = self.snapshot(machineId, name)

        try:
            node = provider.client.ex_clone(node, size, clone.id, cloudspace.networkId, diskmapping, snapshotTimestamp)
            self.cb.machine.updateMachineFromNode(clone, node, stack['id'], size)
        except:
            self.cb.machine.cleanup(clone)
            raise
        tags = str(machineId)
        j.logger.log('Cloned', category='machine.history.ui', tags=tags)
        return clone.id

    @authenticator.auth(acl={'machine': set('R')})
    def getHistory(self, machineId, size, **kwargs):
        """
        Get machine history

        :param machineId: id of the machine
        :param size: number of entries to return
        :return: list of the history of the machine
        """
        provider, node, machine = self.cb.getProviderAndNode(machineId)
        if machine.status in ['DESTROYED', 'DESTROYING']:
            raise exceptions.NotFound('Machine %s not found' % machineId)
        tags = str(machineId)
        query = {'category': 'machine_history_ui', 'tags': tags}
        return self.osis_logs.search(query, size=size)[1:]

    @authenticator.auth(acl={'cloudspace': set('X'), 'machine': set('U')})
    def addUser(self, machineId, userId, accesstype, **kwargs):
        """
        Give a registered user access rights

        :param machineId: id of the machine
        :param userId: username or emailaddress of the user to grant access
        :param accesstype: 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        :return True if user was added successfully
        """
        user = self.cb.checkUser(userId, activeonly=False)
        if not user:
            raise exceptions.NotFound("User is not registered on the system")
        else:
            # Replace email address with ID
            userId = user['id']

        self._addACE(machineId, userId, accesstype, userstatus='CONFIRMED')
        try:
            j.apps.cloudapi.users.sendShareResourceEmail(user, 'machine', machineId, accesstype)
            return True
        except:
            self.deleteUser(machineId, userId, recursivedelete=False)
            raise

    def _addACE(self, machineId, userId, accesstype, userstatus='CONFIRMED'):
        """
        Add a new ACE to the ACL of the vmachine

        :param:machineId id of the vmachine
        :param userId: userid for registered users or emailaddress for unregistered users
        :param accesstype: 'R' for read only access, 'W' for Write access
        :param userstatus: status of the user (CONFIRMED or INVITED)
        :return True if ACE was successfully added
        """
        self.cb.isValidRole(accesstype)
        machineId = int(machineId)
        vmachine = self.models.vmachine.get(machineId)
        vmachineacl = authenticator.auth().getVMachineAcl(machineId)
        if userId in vmachineacl:
            raise exceptions.BadRequest('User already has access rights to this machine')

        ace = vmachine.new_acl()
        ace.userGroupId = userId
        ace.type = 'U'
        ace.right = accesstype
        ace.status = userstatus
        self.models.vmachine.updateSearch({'id': machineId},
                                          {'$push': {'acl': ace.obj2dict()}})
        return True

    def _updateACE(self, machineId, userId, accesstype, userstatus):
        """
        Update an existing ACE in the ACL of a machine

        :param machineId: id of the cloudspace
        :param userId: userid for registered users or emailaddress for unregistered users
        :param accesstype: 'R' for read only access, 'W' for Write access
        :param userstatus: status of the user (CONFIRMED or INVITED)
        :return True if ACE was successfully updated, False if no update is needed
        """
        self.cb.isValidRole(accesstype)
        machineId = int(machineId)
        vmachine = self.models.vmachine.get(machineId)
        vmachine_acl = authenticator.auth().getVMachineAcl(machineId)
        if userId in vmachine_acl:
            useracl = vmachine_acl[userId]
        else:
            raise exceptions.NotFound('User does not have any access rights to update')

        # If user has higher access rights on cloudspace then do not update, raise error
        if 'account_right' in useracl and set(accesstype) != set(useracl['account_right']) and \
                set(accesstype).issubset(set(useracl['account_right'])):
            raise exceptions.Conflict('User already has a higher access level to owning account')
        # If user has higher access rights on cloudspace then do not update, raise error
        elif 'cloudspace_right' in useracl and set(accesstype) != set(useracl['cloudspace_right']) \
                and set(accesstype).issubset(set(useracl['cloudspace_right'])):
            raise exceptions.Conflict('User already has a higher access level to cloudspace')
        # If user has the same access level on account or cloudspace then do not update,
        # fail silently
        if ('account_right' in useracl and set(accesstype) == set(useracl['account_right'])) or \
                ('cloudspace_right' in useracl and
                    set(accesstype) == set(useracl['cloudspace_right'])):
            # Remove machine level access rights if present, cleanup for backwards comparability
            self.models.vmachine.updateSearch({'id': machineId},
                                              {'$pull': {'userGroupId': userId, 'type': 'U'}})
            return False
        else:
            # grant higher access level
            ace = vmachine.new_acl()
            ace.userGroupId = userId
            ace.type = 'U'
            ace.right = accesstype
            ace.status = userstatus
            self.models.vmachine.updateSearch({'id': machineId},
                                              {'$pull': {'acl': {'type': 'U', 'userGroupId': userId}}})
            self.models.vmachine.updateSearch({'id': machineId},
                                              {'$push': {'acl': ace.obj2dict()}})
        return True

    @authenticator.auth(acl={'cloudspace': set('X'), 'machine': set('U')})
    def deleteUser(self, machineId, userId, **kwargs):
        """
        Revoke user access from the vmachine

        :param machineId: id of the machine
        :param userId: id or emailaddress of the user to remove
        :return True if user access was revoked from machine
        """

        result = self.models.vmachine.updateSearch({'id': machineId},
                                                   {'$pull': {'acl': {'type': 'U', 'userGroupId': userId}}})
        if result['nModified'] == 0:
            # User was not found in access rights
            raise exceptions.NotFound('User "%s" does not have access on the machine' % userId)
        return True

    @authenticator.auth(acl={'cloudspace': set('X'), 'machine': set('U')})
    def updateUser(self, machineId, userId, accesstype, **kwargs):
        """
        Update user access rights. Returns True only if an actual update has happened.

        :param machineId: id of the machineId
        :param userId: userid/email for registered users or emailaddress for unregistered users
        :param accesstype: 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        :return True if user access was updated successfully
        """
        # Check if user exists in the system or is an unregistered invited user
        existinguser = self.systemodel.user.search({'id': userId})[1:]
        if existinguser:
            userstatus = 'CONFIRMED'
        else:
            userstatus = 'INVITED'
        return self._updateACE(machineId, userId, accesstype, userstatus)

    @authenticator.auth(acl={'cloudspace': set('X')})
    def attachExternalNetwork(self, machineId, **kwargs):
        """
         Attach a external network to the machine

        :param machineId: id of the machine
        :return: True if a external network was attached to the machine
        """
        provider, node, vmachine = self.cb.getProviderAndNode(machineId)
        for nic in vmachine.nics:
            if nic.type == 'vlan':
                return True
        cloudspace = self.models.cloudspace.get(vmachine.cloudspaceId)
        # Check that attaching a external network will not exceed the allowed CU limits
        j.apps.cloudapi.cloudspaces.checkAvailablePublicIPs(vmachine.cloudspaceId, 1)
        networkid = cloudspace.networkId
        netinfo = self.network.getExternalIpAddress(cloudspace.gid, cloudspace.externalnetworkId)
        if netinfo is None:
            raise RuntimeError("No available externalnetwork IPAddresses")
        pool, externalnetworkip = netinfo
        if not externalnetworkip:
            raise RuntimeError("Failed to get externalnetworkip for networkid %s" % networkid)
        nic = vmachine.new_nic()
        nic.ipAddress = str(externalnetworkip)
        nic.params = j.core.tags.getTagString([], {'gateway': pool.gateway, 'externalnetworkId': str(pool.id)})
        nic.type = 'vlan'
        self.models.vmachine.set(vmachine)
        iface = provider.client.attach_public_network(node, pool.vlan)
        nic.deviceName = iface.target
        nic.macAddress = iface.mac
        self.models.vmachine.set(vmachine)
        return True

    @authenticator.auth(acl={'cloudspace': set('X')})
    @RequireState(enums.MachineStatus.halted, 'Can only resize a halted Virtual Machine')
    def resize(self, machineId, sizeId, **kwargs):
        provider, node, vmachine = self.cb.getProviderAndNode(machineId)
        bootdisks = self.models.disk.search({'id': {'$in': vmachine.disks}, 'type': 'B'})[1:]
        if len(bootdisks) != 1:
            raise exceptions.Error('Failed to retreive first disk')
        bootdisk = self.models.disk.get(bootdisks[0]['id'])
        size = self.models.size.get(sizeId)
        providersize = provider.getSize(size, bootdisk)

        # Validate that enough resources are available in the CU limits if size will be increased
        oldsize = self.models.size.get(vmachine.sizeId)
        # Calcultate the delta in memory and vpcu only if new size is bigger than old size
        deltacpu = max(size.vcpus - oldsize.vcpus, 0)
        deltamemory = max((size.memory - oldsize.memory) / 1024.0, 0)
        j.apps.cloudapi.cloudspaces.checkAvailableMachineResources(vmachine.cloudspaceId,
                                                                   numcpus=deltacpu,
                                                                   memorysize=deltamemory)
        provider.client.ex_resize(node=node, size=providersize)
        vmachine.sizeId = sizeId
        self.models.vmachine.set(vmachine)
        return True

    @authenticator.auth(acl={'cloudspace': set('X')})
    def detachExternalNetwork(self, machineId, **kwargs):
        """
        Detach the external network from the machine

        :param machineId: id of the machine
        :return: True if external network was detached from the machine
        """

        provider, node, vmachine = self.cb.getProviderAndNode(machineId)

        for nic in vmachine.nics:
            nicdict = nic.obj2dict()
            if 'type' not in nicdict or nicdict['type'] != 'PUBLIC':
                continue

            provider.client.detach_public_network(node)
        self._detachExternalNetworkFromModel(vmachine)
        return True

    def _detachExternalNetworkFromModel(self, vmachine):
        for nic in vmachine.nics:
            nicdict = nic.obj2dict()
            if 'type' not in nicdict or nicdict['type'] != 'PUBLIC':
                continue
            vmachine.nics.remove(nic)
            self.models.vmachine.set(vmachine)
            tags = j.core.tags.getObject(nic.params)
            self.network.releaseExternalIpAddress(int(tags.tags.get('externalnetworkId')), nic.ipAddress)
