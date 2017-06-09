from js9 import j
from JumpScale9Portal.portal import exceptions
from cloudbrokerlib import enums, network
from .gridmanager.client import getGridClient
from .netmgr import NetManager
import netaddr
import uuid
import random
import time
import string
import re
import json

models = j.clients.osis.getNamespace('cloudbroker')


def removeConfusingChars(input):
    return input.replace('0', '').replace('O', '').replace('l', '').replace('I', '')


class CloudBroker(object):
    _resourceProviderId2StackId = dict()

    def __init__(self):
        self._actors = None
        self.syscl = j.clients.osis.getNamespace('system')
        self.cbcl = models
        self.machine = Machine(self)
        self.cloudspace = CloudSpace(self)
        self.netmgr = NetManager(self, models)

    @property
    def actors(self):
        ctx = j.core.portal.active.requestContext
        hrd = j.application.getAppInstanceHRD(name="portal_client", instance='cloudbroker')
        addr = hrd.get('instance.param.addr')
        port = hrd.getInt('instance.param.port')
        secret = hrd.getStr('instance.param.secret')
        cl = j.clients.portal.get2(ip=addr, port=port, secret=secret)
        oldauth = ctx.env.get('HTTP_AUTHORIZATION', None)
        if oldauth is not None:
            cl._session.headers.update({'Authorization': oldauth})
        elif ctx.env.get('HTTP_COOKIE', None):
            cookie = ctx.env.get('HTTP_COOKIE', None)
            cl._session.headers.update({'Cookie': cookie})
        elif 'authkey' in ctx.params:
            secret = ctx.params['authkey']
            cl._session.headers.update({'Authorization': 'authkey {}'.format(secret)})
        return cl

    def markProvider(self, stackId, eco):
        stack = models.stack.get(stackId)
        stack.error += 1
        if stack.error >= 2:
            stack.status = 'ERROR'
            stack.eco = eco.guid
        models.stack.set(stack)

    def clearProvider(self, stackId):
        stack = models.stack.get(stackId)
        stack.error = 0
        stack.eco = None
        stack.status = 'ENABLED'
        models.stack.set(stack)

    def getBestStack(self, gid, imageId=None, excludelist=[]):
        client = getGridClient(gid, models)
        capacityinfo = self.getCapacityInfo(gid, client, imageId)
        if not capacityinfo:
            return -1
        capacityinfo = [node for node in capacityinfo if node['id'] not in excludelist]
        if not capacityinfo:
            return -1

        return capacityinfo[0]  # is sorted by least used

    def getProvider(self, machine):
        if machine.referenceId and machine.stackId:
            return self.getProviderByStackId(machine.stackId)
        return None

    def chooseProvider(self, machine):
        cloudspace = models.cloudspace.get(machine.cloudspaceId)
        newstack = self.getBestStack(cloudspace.gid, machine.imageId)
        if newstack == -1:
            raise exceptions.ServiceUnavailable('Not enough resources available to start the requested machine')
        machine.stackId = newstack['id']
        models.vmachine.set(machine)
        return True

    def getCapacityInfo(self, gid, client, imageId=None):
        resourcesdata = list()
        activenodes = [node['id'] for node in client.getActiveNodes()]
        if imageId:
            stacks = models.stack.search({"images": imageId, 'gid': gid})[1:]
        else:
            stacks = models.stack.search({'gid': gid})[1:]
        sizes = {s['id']: s['memory'] for s in models.size.search({'$fields': ['id', 'memory']})[1:]}
        for stack in stacks:
            if stack.get('status', 'ENABLED') == 'ENABLED':
                if stack['referenceId'] not in activenodes:
                    continue
                # search for all vms running on the stacks
                usedvms = models.vmachine.search({'$fields': ['id', 'sizeId'],
                                                  '$query': {'stackId': stack['id'],
                                                             'status': {'$nin': ['HALTED', 'ERROR', 'DESTROYED']}}
                                                  }
                                                 )[1:]
                if usedvms:
                    stack['usedmemory'] = sum(sizes[vm['sizeId']] for vm in usedvms)
                else:
                    stack['usedmemory'] = 0
                resourcesdata.append(stack)
        resourcesdata.sort(key=lambda s: s['usedmemory'])
        return resourcesdata

    def stackImportImages(self, stackId):
        """
        Sync Provider images [Deletes obsolete images that are deleted from provider side/Add new ones]
        """
        raise NotImplemented()

    def registerNetworkIdRange(self, gid, start, end, **kwargs):
        """
        Add a new network idrange
        param:start start of the range
        param:end end of the range
        result
        """
        newrange = set(range(int(start), int(end) + 1))
        if models.networkids.exists(gid):
            cloudspaces = models.cloudspace.search({'$fields': ['networkId'],
                                                    '$query': {'status': {'$in': ['DEPLOYED', 'VIRTUAL']},
                                                               'gid': gid}
                                                    })[1:]
            usednetworkids = {space['networkId'] for space in cloudspaces}
            if usednetworkids.intersection(newrange):
                raise exceptions.Conflict("Atleast one networkId conflicts with deployed networkids")
            models.networkids.updateSearch({'id': gid},
                                           {'$addToSet': {'networkids': {'$each': newrange}}})
        else:
            networkids = {'id': gid, 'networkids': newrange}
            models.networkids.set(networkids)
        return True

    def getFreeNetworkId(self, gid, **kwargs):
        """
        Get a free NetworkId
        result
        """
        for netid in models.networkids.get(gid).freeNetworkIds:
            res = models.networkids.updateSearch({'id': gid},
                                                 {'$pull': {'freeNetworkIds': netid}})
            if res['nModified'] == 1:
                models.networkids.updateSearch({'id': gid},
                                               {'$push': {'usedNetworkIds': netid}})
                return netid

    def releaseNetworkId(self, gid, networkid, **kwargs):
        """
        Release a networkid.
        param:networkid int representing the netowrkid to release
        result bool
        """
        models.networkids.updateSearch({'id': gid},
                                       {'$pull': {'usedNetworkIds': networkid},
                                        '$addToSet': {'freeNetworkIds': networkid}})
        return True

    def checkUser(self, username, activeonly=True):
        """
        Check if a user exists with the given username or email address

        :param username: username or emailaddress of the user
        :param activeonly: only return activated users if set to True
        :return: User if found
        """
        query = {'$or': [{'id': username}, {'emails': username}]}
        if activeonly:
            query['active'] = True
        users = self.syscl.user.search(query)[1:]
        if users:
            return users[0]
        else:
            return None

    def updateResourceInvitations(self, username, emailaddress):
        """
        Update the invitations in ACLs of Accounts, Cloudspaces and Machines after user registration

        :param username: username the user has registered with
        :param emailaddress: emailaddress of the registered users
        :return: True if resources were updated
        """
        # Validate that only one email address was sent for updating the resources
        if len(emailaddress.split(',')) > 1:
            raise exceptions.BadRequest('Cannot update resource invitations for a list of multiple '
                                        'email addresses')

        for account in self.cbcl.account.search({'acl.userGroupId': emailaddress})[1:]:
            accountobj = self.cbcl.account.get(account['guid'])
            for ace in accountobj.acl:
                if ace.userGroupId == emailaddress:
                    # Update userGroupId and status after user registration
                    ace.userGroupId = username
                    ace.status = 'CONFIRMED'
                    self.cbcl.account.set(accountobj)
                    break

        for cloudspace in self.cbcl.cloudspace.search({'acl.userGroupId': emailaddress})[1:]:
            cloudspaceobj = self.cbcl.cloudspace.get(cloudspace['guid'])
            for ace in cloudspaceobj.acl:
                if ace.userGroupId == emailaddress:
                    # Update userGroupId and status after user registration
                    ace.userGroupId = username
                    ace.status = 'CONFIRMED'
                    self.cbcl.cloudspace.set(cloudspaceobj)
                    break

        for vmachine in self.cbcl.vmachine.search({'acl.userGroupId': emailaddress})[1:]:
            vmachineobj = self.cbcl.vmachine.get(vmachine['guid'])
            for ace in cloudspaceobj.acl:
                if ace.userGroupId == emailaddress:
                    # Update userGroupId and status after user registration
                    ace.userGroupId = username
                    ace.status = 'CONFIRMED'
                    self.cbcl.vmachine.set(vmachineobj)
                    break

        return True

    def isaccountuserdeletable(self, userace, acl):
        if set(userace.right) != set('ARCXDU'):
            return True
        else:
            otheradmins = filter(lambda a: set(a.right) == set('ARCXDU') and a != userace, acl)
            if not otheradmins:
                return False
            else:
                return True

    def isValidEmailAddress(self, emailaddress):
        r = re.compile('^[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}$')
        return r.match(emailaddress) is not None

    def isValidRole(self, accessrights):
        """
        Validate that the accessrights map to a valid access role on a resource
        'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin

        :param accessrights: string with the accessrights to verify
        :return: role name if a valid set of permissions, otherwise fail with an exception
        """
        if accessrights == 'R':
            return 'Read'
        elif set(accessrights) == set('RCX'):
            return 'Read/Write'
        elif set(accessrights) == set('ARCXDU'):
            return 'Admin'
        else:
            raise exceptions.BadRequest('Invalid set of access rights "%s". Please only use "R" '
                                        'for Read, "RCX" for Read/Write and "ARCXDU" for Admin '
                                        'access.' % accessrights)

    def fillResourceLimits(self, resource_limits, preserve_none=False):
        for limit_type in ['CU_M', 'CU_D', 'CU_C', 'CU_NP', 'CU_I']:
            if limit_type not in resource_limits or resource_limits[limit_type] is None:
                resource_limits[limit_type] = None if preserve_none else -1
            elif resource_limits[limit_type] < -1 or resource_limits[limit_type] == 0:
                raise exceptions.BadRequest('A resource limit should be a positive number or -1 (unlimited).')
            if limit_type == 'CU_M':
                resource_limits[limit_type] = resource_limits[limit_type] and float(resource_limits[limit_type])
            else:
                resource_limits[limit_type] = resource_limits[limit_type] and int(resource_limits[limit_type])
        maxVDiskCapacity = resource_limits['CU_D']
        if maxVDiskCapacity is not None and maxVDiskCapacity != -1 and maxVDiskCapacity < 10:
            raise exceptions.BadRequest("Minimum disk capacity for cloudspace is 10GB.")


class CloudSpace(object):

    def __init__(self, cb):
        self.cb = cb
        self.network = network.Network(models)

    def release_resources(self, cloudspace, releasenetwork=True):
        #  delete routeros
        if cloudspace.stackId:
            self.cb.netmgr.destroy(cloudspace)
        if cloudspace.networkId and releasenetwork:
            self.cb.releaseNetworkId(cloudspace.gid, cloudspace.networkId)
            cloudspace.networkId = None
        if cloudspace.externalnetworkip:
            self.network.releaseExternalIpAddress(cloudspace.externalnetworkId, cloudspace.externalnetworkip)
            cloudspace.externalnetworkip = None
        return cloudspace


class Machine(object):

    def __init__(self, cb):
        self.cb = cb
        self.rcl = j.clients.redis.getByInstance('system')

    def cleanup(self, machine):
        # this method might be called by muiltiple layers so we dont care of delete fails
        for diskid in machine.disks:
            try:
                models.disk.delete(diskid)
            except:
                pass
        try:
            models.vmachine.delete(machine.id)
        except:
            pass

    def validateCreate(self, cloudspace, name, sizeId, imageId, disksize, datadisks):
        self.assertName(cloudspace.id, name)
        if not disksize:
            raise exceptions.BadRequest("Invalid disksize %s" % disksize)

        for datadisksize in datadisks:
            if datadisksize > 2000:
                raise exceptions.BadRequest("Invalid data disk size {}GB max size is 2000GB".format(datadisksize))

        if cloudspace.status == 'DESTROYED':
            raise exceptions.BadRequest('Can not create machine on destroyed Cloud Space')

        image = models.image.get(imageId)
        if disksize < image.size:
            raise exceptions.BadRequest(
                "Disk size of {}GB is to small for image {}, which requires at least {}GB.".format(disksize, image.name, image.size))
        if image.status != "CREATED":
            raise exceptions.BadRequest("Image {} is disabled.".format(imageId))

        if models.vmachine.count({'status': {'$ne': 'DESTROYED'}, 'cloudspaceId': cloudspace.id}) >= 250:
            raise exceptions.BadRequest("Can not create more than 250 Virtual Machines per Cloud Space")

        sizes = j.apps.cloudapi.sizes.list(cloudspace.id)
        if sizeId not in [s['id'] for s in sizes]:
            raise exceptions.BadRequest("Cannot create machine with specified size on this cloudspace")

        size = models.size.get(sizeId)
        if disksize not in size.disks:
            raise exceptions.BadRequest("Disk size of {}GB is invalid for sizeId {}.".format(disksize, sizeId))

    def assertName(self, cloudspaceId, name):
        if not name or not name.strip():
            raise ValueError("Machine name can not be empty")
        results = models.vmachine.search({'cloudspaceId': cloudspaceId, 'name': name,
                                          'status': {'$nin': ['DESTROYED', 'ERROR']}})[1:]
        if results:
            raise exceptions.Conflict('Selected name already exists')

    def getFreeMacAddress(self, gid, **kwargs):
        """
        Get a free macaddres in this environment
        result
        """
        mac = models.macaddress.set(key=gid, obj=1)
        firstmac = netaddr.EUI('52:54:00:00:00:00')
        newmac = int(firstmac) + mac
        macaddr = netaddr.EUI(newmac)
        macaddr.dialect = netaddr.mac_eui48
        return str(macaddr).replace('-', ':').lower()

    def createModel(self, name, description, cloudspace, imageId, sizeId, disksize, datadisks):
        datadisks = datadisks or []

        image = models.image.get(imageId)
        machine = models.vmachine.new()
        machine.cloudspaceId = cloudspace.id
        machine.descr = description
        machine.name = name
        machine.status = 'HALTED'
        machine.sizeId = sizeId
        machine.imageId = imageId
        machine.creationTime = int(time.time())
        machine.updateTime = int(time.time())
        machine.type = 'VIRTUAL'

        def addDisk(order, size, type, name=None):
            disk = models.disk.new()
            disk.name = name or 'Disk nr %s' % order
            disk.descr = 'Machine disk of type %s' % type
            disk.sizeMax = size
            disk.iops = 2000
            disk.accountId = cloudspace.accountId
            disk.gid = cloudspace.gid
            disk.order = order
            disk.type = type
            diskid = models.disk.set(disk)[0]
            machine.disks.append(diskid)
            return diskid

        addDisk(-1, disksize, 'B', 'Boot disk')
        diskinfo = []
        for order, datadisksize in enumerate(datadisks):
            diskid = addDisk(order, int(datadisksize), 'D')
            diskinfo.append((diskid, int(datadisksize)))

        account = machine.new_account()
        if hasattr(image, 'username') and image.username:
            account.login = image.username
        elif image.type != 'Custom Templates':
            account.login = 'gig'
        else:
            account.login = 'Custom login'
            account.password = 'Custom password'

        if hasattr(image, 'password') and image.password:
            account.password = image.password

        if not account.password:
            length = 6
            chars = removeConfusingChars(string.letters + string.digits)
            letters = [removeConfusingChars(string.ascii_lowercase), removeConfusingChars(string.ascii_uppercase)]
            passwd = ''.join(random.choice(chars) for _ in range(length))
            passwd = passwd + random.choice(string.digits) + random.choice(letters[0]) + random.choice(letters[1])
            account.password = passwd
        machine.id = models.vmachine.set(machine)[0]

        nic = machine.new_nic()
        nic.macAddress = self.getFreeMacAddress(cloudspace.gid)
        nic.deviceName = 'vm-{}-{:04x}'.format(machine.id, cloudspace.networkId)
        nic.networkId = cloudspace.networkId
        nic.type = 'vxlan'
        with models.cloudspace.lock(cloudspace.id):
            nic.ipAddress = self.cb.netmgr.getFreeIPAddress(cloudspace)
            machine.id = models.vmachine.set(machine)[0]

        return machine

    def _getBestClient(self, machine, gid, newstackId, excludelist, imageId=None):
        client = None
        if not newstackId:
            stack = self.cb.getBestStack(gid, imageId, excludelist)
            if stack == -1:
                raise exceptions.ServiceUnavailable(
                    'Not enough resources available to provision the requested machine')
            client = getGridClient(stack['gid'], models)
        else:
            stack = models.stack.get(newstackId).dump()
            client = getGridClient(stack['gid'], models)
            activenodes = [node['id']for node in client.getActiveNodes()]
            if stack['referenceId'] not in activenodes:
                raise exceptions.ServiceUnavailable(
                    'Not enough resources available to provision the requested machine')
        return stack, client

    def create(self, machine, cloudspace, imageId, stackId):
        excludelist = []
        newstackId = stackId
        machine.hostName = 'vm-{}'.format(machine.id)
        while True:
            disks = []
            stack, client = self._getBestClient(machine, cloudspace.gid, newstackId, excludelist, imageId)
            machine.stackId = stack['id']

            if imageId not in stack['images']:
                self.cleanup(machine)
                raise exceptions.BadRequest("Image is not available on requested stack")
            image = models.image.get(imageId)

            try:
                for diskId in machine.disks:
                    disk = models.disk.get(diskId)
                    disks.append(disk)
                    if disk.type == 'B':
                        client.storage.createVolume(disk, image)
                    else:
                        client.storage.createVolume(disk)
            except Exception as e:
                eco = j.errorconditionhandler.processPythonExceptionObject(e)
                self.cleanup(machine)
                raise exceptions.ServiceUnavailable('Not enough storage resources available to provision the requested machine')
            try:
                models.vmachine.set(machine)
                client.machine.create(machine, disks, stack['referenceId'])
                break
            except Exception as e:
                eco = j.errorconditionhandler.processPythonExceptionObject(e)
                self.cb.markProvider(stack['id'], eco)
                newstackId = 0
                models.vmachine.updateSearch({'id': machine.id}, {'$set': {'status': 'ERROR'}})
                if stackId:
                    self.cleanup(machine)
                    raise exceptions.ServiceUnavailable('Not enough cpu resources available to provision the requested machine')
                else:
                    excludelist.append(stack['id'])
                    newstackId = 0
        self.cb.clearProvider(stack['id'])
        models.vmachine.updateSearch({'id': machine.id},
                                     {'$set': {'stackId': stack['id'],
                                               'status': 'RUNNING'}})
        return machine.id

    def get_cloudinit_data(self, machine):
        image = models.image.get(machine['imageId'])
        hostname = 'vm-{}'.format(machine['id'])
        userdata = {}
        if image.type.lower().strip() != 'windows':
            userdata = {'users': [],
                        # 'password': password  # might break cloud init reminder for further testing.
                        'ssh_pwauth': True,
                        'manage_etc_hosts': True,
                        'chpasswd': {'expire': False}}
            for account in machine['accounts']:
                userdata['users'].append({'name': account['login'],
                                          'plain_text_passwd': account['password'],
                                          'lock-passwd': False,
                                          'shell': '/bin/bash',
                                          'sudo': 'ALL=(ALL) ALL'})
            metadata = {'local-hostname': hostname}
        else:
            admin = machine['accounts'][0]
            metadata = {'admin_pass': admin['password'], 'hostname': hostname}
        return {'userdata': json.dumps(userdata), 'metadata': json.dumps(metadata)}

    def start(self, machine, stackId=None):
        excludelist = []
        newstackId = stackId
        imageId = machine.imageId
        cloudspace = models.cloudspace.get(machine.cloudspaceId)

        while True:
            stack, client = self._getBestClient(machine, cloudspace.gid, newstackId, excludelist, imageId)
            try:
                client.machine.start(machine.id, stack['referenceId'])
                break
            except Exception as e:
                eco = j.errorconditionhandler.processPythonExceptionObject(e)
                self.cb.markProvider(stack['id'], eco)
                newstackId = 0
                models.vmachine.updateSearch({'id': machine.id}, {'$set': {'status': 'ERROR'}})
                if stackId:
                    raise exceptions.ServiceUnavailable('Not enough cpu resources available to provision the requested machine')
                else:
                    excludelist.append(stack['id'])
                    newstackId = 0
                self.cb.clearProvider(stack['id'])
        models.vmachine.updateSearch({'id': machine.id}, {'$set': {'stackId': stack['id']}})
        return machine.id

    def stop(self, machine, force=False):
        stackId = machine.stackId
        stack = models.stack.get(stackId)
        client = getGridClient(stack.gid, models)
        try:
            if force:
                client.machine.shutdown(machine.id, stack.referenceId)
            else:
                client.machine.stop(machine.id, stack.referenceId)
        except Exception as e:
            eco = j.errorconditionhandler.processPythonExceptionObject(e)
            self.cb.markProvider(stack.id, eco)
            models.vmachine.updateSearch({'id': machine.id}, {'$set': {'status': 'ERROR'}})
            raise
        return machine.id

    def get(self, machine):
        stackId = machine.stackId
        stack = models.stack.get(stackId)
        client = getGridClient(stack.gid, models)
        return client.machine.get(machine.id, stack.referenceId)

    def getConsoleUrl(self, machine):
        stackId = machine.stackId
        stack = models.stack.get(stackId)
        token = str(uuid.uuid4())
        vncs = models.vnc.search({'gid': stack.gid})[1:]
        if not vncs:
            raise exceptions.BadRequest("Not console output available")
        self.rcl.set('vnc:{}'.format(token), str(machine.id), ex=60)
        vnc = random.choice(vncs)
        return "{url}{token}".format(url=vnc['url'], token=token)

    def getConsoleInfo(self, token):
        machineId = int(self.rcl.get('vnc:{}'.format(token)))
        machine = models.vmachine.get(machineId)
        machineinfo = self.get(machine)
        stackId = machine.stackId
        stack = models.stack.get(stackId)
        client = getGridClient(stack.gid, models)
        nodeinfo = client.getNode(stack.referenceId)
        return {'ipaddress': nodeinfo['ipaddress'], 'port': machineinfo['vnc']}

    def pause(self, machine):
        stackId = machine.stackId
        stack = models.stack.get(stackId)
        client = getGridClient(stack.gid, models)
        try:
            client.machine.pause(machine.id, stack.referenceId)
        except Exception as e:
            eco = j.errorconditionhandler.processPythonExceptionObject(e)
            self.cb.markProvider(stack.id, eco)
            models.vmachine.updateSearch({'id': machine.id}, {'$set': {'status': 'ERROR'}})
            raise
        return machine.id

    def update(self, machine):
        stackId = machine.stackId
        stack = models.stack.get(stackId)
        client = getGridClient(stack.gid, models)
        return client.machine.update(machine, stack.referenceId)

    def resume(self, machine):
        stackId = machine.stackId
        stack = models.stack.get(stackId)
        client = getGridClient(stack.gid, models)
        try:
            client.machine.resume(machine.id, stack.referenceId)
        except Exception as e:
            eco = j.errorconditionhandler.processPythonExceptionObject(e)
            self.cb.markProvider(stack.id, eco)
            models.vmachine.updateSearch({'id': machine.id}, {'$set': {'status': 'ERROR'}})
            raise
        return machine.id

    def destroy(self, machine):
        stackId = machine.stackId
        if stackId:
            stack = models.stack.get(stackId)
            client = getGridClient(stack.gid, models)
            client.machine.destroy(machine.id, stack.referenceId)
        for diskId in machine.disks:
            disk = models.disk.get(diskId)
            client.storage.deleteVolume(disk)

# not api not implemented use start and stop instead
    # def reboot(self, machine):
    #     stackId = machine.stackId
    #     stack = models.stack.get(stackId)
    #     client = getGridClient(stack.gid, models)
    #     try:
    #         client.machine.reboot(machine.id, stack.refrenceId)
    #     except Exception as e:
    #         eco = j.errorconditionhandler.processPythonExceptionObject(e)
    #         self.cb.markProvider(stack.id, eco)
    #         machine.status = 'ERROR'
    #         models.vmachine.updateSearch({'id': machine.id}, {'$set': {'status': 'ERROR'}})
    #         raise
    #     tags = str(machine.id)
    #     return machine.id

    def status(self, machine):
        stackId = machine.stackId
        stack = models.stack.get(stackId)
        client = getGridClient(stack.gid, models)
        status = client.machine.status(machine.id, stack.refrenceId)
        models.vmachine.updateSearch({'id': machine.id},
                                     {'$set': {'status': getattr(enums.MachineStatus, status.capitalize())}})
        return status

    def rollback(self, machine, epoch):
        stackId = machine.stackId
        stack = models.stack.get(stackId)
        client = getGridClient(stack.gid, models)
        for diskId in machine.disks:
            disk = models.disk.get(diskId)
            client.storage.rollbackVolume(disk, epoch)
