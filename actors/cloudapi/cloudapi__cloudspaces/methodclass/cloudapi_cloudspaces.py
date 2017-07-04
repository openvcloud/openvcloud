from js9 import j
from JumpScale9Portal.portal import exceptions
from cloudbroker.actorlib import authenticator, network, netmgr
from cloudbroker.actorlib.baseactor import BaseActor
import netaddr
import uuid
import time
import gevent


def getIP(network):
    if not network:
        return network
    return str(netaddr.IPNetwork(network).ip)


class cloudapi_cloudspaces(BaseActor):
    """
    API Actor api for managing cloudspaces, this actor is the final api a enduser uses to manage cloudspaces

    """

    def __init__(self):
        super(cloudapi_cloudspaces, self).__init__()
        self.netmgr = self.cb.netmgr
        self.network = network.Network(self.models)

    @authenticator.auth(acl={'cloudspace': set('U')})
    def addUser(self, cloudspaceId, userId, accesstype, **kwargs):
        """
        Give a registered user access rights

        :param cloudspaceId: id of the cloudspace
        :param userId: username or emailaddress of the user to grant access
        :param accesstype: 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        :return True if user was added successfully
        """
        user = self.cb.checkUser(userId, activeonly=False)
        if not user:
            raise exceptions.NotFound("User is not registered on the system")
        else:
            # Replace email address with name
            userId = user.name
        cloudspace = self.cb.cloudspace.get(cloudspaceId)

        self._addACE(cloudspace, userId, accesstype, userstatus='CONFIRMED')
        try:
            j.apps.cloudapi.users.sendShareResourceEmail(user, 'cloudspace', cloudspace, accesstype)
            return True
        except:
            self.deleteUser(cloudspaceId, userId, recursivedelete=False)
            raise

    def _addACE(self, cloudspace, userId, accesstype, userstatus='CONFIRMED'):
        """
        Add a new ACE to the ACL of the cloudspace

        :param cloudspace: cloudspace object
        :param userId: userid/email for registered users or emailaddress for unregistered users
        :param accesstype: 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        :param userstatus: status of the user (CONFIRMED or INVITED)
        :return True if ACE was added successfully
        """
        self.cb.isValidRole(accesstype)
        cloudspaceacl = authenticator.auth().getCloudspaceAcl(cloudspace)
        if userId in cloudspaceacl:
            raise exceptions.BadRequest('User already has access rights to this cloudspace')

        ace = self.models.ACE(
            userGroupId=userId,
            type='U',
            right=accesstype,
            status=userstatus
        )
        cloudspace.update(add_to_set__acl=ace)
        return True

    def _updateACE(self, cloudspace, userId, accesstype, userstatus):
        """
        Update an existing ACE in the ACL of a cloudspace

        :param cloudspaceId: id of the cloudspace
        :param userId: userid/email for registered users or emailaddress for unregistered users
        :param accesstype: 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        :param userstatus: status of the user (CONFIRMED or INVITED)
        :return True if ACE was successfully updated, False if no update is needed
        """
        self.cb.isValidRole(accesstype)
        cloudspace_acl = authenticator.auth().getCloudspaceAcl(cloudspace)
        if userId in cloudspace_acl:
            useracl = cloudspace_acl[userId]
        else:
            raise exceptions.NotFound('User does not have any access rights to update')

        if 'account_right' in useracl and set(accesstype) == set(useracl['account_right']):
            # No need to add any access rights as same rights are inherited
            # Remove cloudspace level access rights if present, cleanup for backwards comparability
            cloudspace.update(pull__acl={'type': 'U', 'userGroupId': userId})
            return False
        # If user has higher access rights on owning account level, then do not update
        elif 'account_right' in useracl and set(accesstype).issubset(set(useracl['account_right'])):
            raise exceptions.Conflict('User already has a higher access level to owning account')
        else:
            # grant higher access level
            ace = self.models.ACE(
                userGroupId=userId,
                type='U',
                right=accesstype,
                status=userstatus
            )
            cloudspace.update(pull__acl={'type': 'U', 'userGroupId': userId})
            cloudspace.update(add_to_set__acl=ace)
        return True

    @authenticator.auth(acl={'cloudspace': set('U')})
    def updateUser(self, cloudspaceId, userId, accesstype, **kwargs):
        """
        Update user access rights. Returns True only if an actual update has happened.

        :param cloudspaceId: id of the cloudspace
        :param userId: userid/email for registered users or emailaddress for unregistered users
        :param accesstype: 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        :return True if user access was updated successfully
        """
        # Check if user exists in the system or is an unregistered invited user
        cloudspace = self.cb.cloudspace.get(cloudspaceId)
        user = self.cb.checkUser(userId, activeonly=False)
        if not user:
            userstatus = 'INVITED'
        else:
            userstatus = 'CONFIRMED'
            # Replace email address with name
            userId = user.name
        return self._updateACE(cloudspace, userId, accesstype, userstatus)

    def _listActiveCloudSpaces(self, accountId):
        account = self.models.Account.get(accountId)
        if account.status == 'DISABLED':
            return []
        results = self.models.Cloudspace.objects(account=account, status__ne='DESTROYED')
        return results

    def validate_name(self, account, name):
        if self.models.Cloudspace.objects(account=account.id, name=name, status__ne='DESTROYED').count() > 0:
            raise exceptions.BadRequest("Cloudspace with name %s already exists" % name)

    @authenticator.auth(acl={'account': set('C')})
    def create(self, accountId, locationId, name, access, maxMemoryCapacity=-1, maxVDiskCapacity=-1,
               maxCPUCapacity=-1, maxNetworkPeerTransfer=-1, maxNumPublicIP=-1,
               externalnetworkId=None, allowedVMSizes=[], **kwargs):
        """
        Create an extra cloudspace

        :param accountId: id of acount this cloudspace belongs to
        :param locationId: if of location
        :param name: name of cloudspace to create
        :param access: username of a user which has full access to this space
        :param maxMemoryCapacity: max size of memory in GB
        :param maxVDiskCapacity: max size of aggregated vdisks in GB
        :param maxCPUCapacity: max number of cpu cores
        :param maxNetworkPeerTransfer: max sent/received network transfer peering
        :param maxNumPublicIP: max number of assigned public IPs
        :param externalnetworkId: Id of externalnetwork
        :return: True if update was successful
        :return int with id of created cloudspace
        """
        accountId = accountId
        account = self.models.Account.get(accountId)
        if not account or account.status in ['DESTROYED', 'DESTROYING']:
            raise exceptions.NotFound('Account does not exist')
        location = self.models.Location.get(locationId)
        if not location:
            raise exceptions.BadRequest('Location %s does not exists' % location)
        if externalnetworkId:
            externalnetwork = self.models.ExternalNetwork.get(externalnetworkId)
            if not externalnetwork:
                raise exceptions.BadRequest('Could not find externalnetwork with id %s' % externalnetworkId)
            if externalnetwork.account and externalnetwork.account.id != account.id:
                raise exceptions.BadRequest('ExternalNetwork belongs to another account')
            if externalnetwork.location.id != location.id:
                raise exceptions.BadRequest('ExternalNetwork does not belong to currenct location')
        else:
            externalnetwork = None

        self.validate_name(account, name)

        ace = self.models.ACE(
            userGroupId=access,
            status='CONFIRMED',
            type='U',
            right='CXDRAU'
        )

        resourceLimits = {'CU_M': maxMemoryCapacity,
                          'CU_D': maxVDiskCapacity,
                          'CU_C': maxCPUCapacity,
                          'CU_NP': maxNetworkPeerTransfer,
                          'CU_I': maxNumPublicIP}
        self.cb.fillResourceLimits(resourceLimits)

        if resourceLimits['CU_I'] != -1 and resourceLimits['CU_I'] < 1:
            raise exceptions.BadRequest("Cloudspace must have reserve at least 1 Public IP "
                                        "address for its VFW")

        networkid = self.cb.getFreeNetworkId(location)
        if not networkid:
            raise exceptions.ServiceUnavailable("Failed to get networkid")

        netinfo = self.network.getExternalIpAddress(location, externalnetwork)
        if netinfo is None:
            raise exceptions.ServiceUnavailable("No available external IP Addresses")

        pool, externalipaddress = netinfo

        cs = self.models.Cloudspace(
            name=name,
            account=account,
            externalnetwork=pool.id,
            externalnetworkip=str(externalipaddress),
            networkcidr=netmgr.DEFAULTCIDR,
            allowedVMSizes=allowedVMSizes,
            location=location,
            acl=[ace],
            resourceLimits=resourceLimits,
            status='VIRTUAL',
            networkId=networkid,
        )

        # Validate that the specified CU limits can be reserved on account, since there is a
        # validation earlier that maxNumPublicIP > 0 (or -1 meaning unlimited), this check will
        # make sure that 1 Public IP address will be reserved for this cloudspace
        try:
            self._validateAvaliableAccountResources(cs, maxMemoryCapacity, maxVDiskCapacity,
                                                    maxCPUCapacity, maxNetworkPeerTransfer, maxNumPublicIP)
        except:
            self.network.releaseExternalIpAddress(pool, str(externalipaddress))
            self.cb.releaseNetworkId(location, networkid)
            raise

        # deploy async.
        cs.save()
        try:
            self._deploy(cs)
        except:
            cs.delete()
            raise
        ctx = kwargs['ctx']
        ctx.env['tags'] += 'cloudspaceId:{}'.format(cs.id)

        return str(cs.id)

    @authenticator.auth(acl={'cloudspace': set('C')})
    def deploy(self, cloudspaceId, **kwargs):
        cloudspace = self.cb.cloudspace.get(cloudspaceId)
        return self._deploy(cloudspace)

    def _deploy(self, cloudspace, **kwargs):
        """
        Create VFW for cloudspace

        :param cloudspaceId: id of the cloudspace
        :return: status of deployment
        """
        try:
            if cloudspace.status != 'VIRTUAL':
                return
            cloudspace.modify(status='DEPLOYING')
            pool = cloudspace.externalnetwork
            if cloudspace.externalnetworkip is None:
                pool, externalipaddress = self.network.getExternalIpAddress(cloudspace.location, cloudspace.externalnetwork)
                cloudspace.externalnetworkip = str(externalipaddress)
                cloudspace.modify(externalnetworkip=str(externalipaddress))

            externalipaddress = netaddr.IPNetwork(cloudspace.externalnetworkip)

            try:
                self.netmgr.create(cloudspace)
            except:
                self.network.releaseExternalIpAddress(pool, str(externalipaddress))
                cloudspace.modify(status='VIRTUAL', externalnetworkip=None)
                raise

            cloudspace.modify(status='DEPLOYED', updateTime=int(time.time()))
            return 'DEPLOYED'
        except Exception as e:
            j.errorhandler.processPythonExceptionObject(e, message="Cloudspace deploy aysnc call exception.")
            raise

    @authenticator.auth(acl={'cloudspace': set('D')})
    def delete(self, cloudspaceId, **kwargs):
        """
        Delete the cloudspace

        :param cloudspaceId: id of the cloudspace
        :return True if deletion was successful
        """
        # A cloudspace may not contain any resources any more
        cloudspace = self.models.Cloudspace.get(cloudspaceId)
        if self.models.VMachine.objects(cloudspace=cloudspace.id, status__ne='DESTROYED').count() > 0:
            raise exceptions.Conflict(
                'In order to delete a CloudSpace it can not contain Machines.')
        if cloudspace.status == 'DEPLOYING':
            raise exceptions.BadRequest('Can not delete a CloudSpace that is being deployed.')

        cloudspace.modify(status='DESTROYING')
        cloudspace = self.cb.cloudspace.release_resources(cloudspace)
        cloudspace.modify(status='DESTROYED', deletionTime=int(time.time()), updateTime=int(time.time()))
        return True

    @authenticator.auth(acl={'account': set('A')})
    def disable(self, cloudspaceId, reason, **kwargs):
        """
        Disable a cloud space
        :param cloudspaceId id of the cloudspace
        :param reason reason of disabling
        :return True if cloudspace is disabled
        """
        cloudspaceId = int(cloudspaceId)
        cloudspace = self.models.cloudspace.get(cloudspaceId)
        vmachines = self.models.vmachine.search({'cloudspaceId': cloudspaceId,
                                                 'status': {'$in': ['RUNNING', 'PAUSED']}
                                                 })[1:]
        for vmachine in vmachines:
            self.cb.actors.cloudapi.machines.stop(machineId=vmachine['id'])
        self.netmgr.fw_stop(cloudspace.networkId)
        self.models.cloudspace.updateSearch({'id': cloudspaceId}, {'$set': {'status': 'DISABLED'}})
        return True

    @authenticator.auth(acl={'account': set('A')})
    def enable(self, cloudspaceId, reason, **kwargs):
        """
        Enable a cloud space
        :param cloudspaceId id of the cloudspaceId
        :param reason reason of enabling
        :return True if cloudspace is enabled
        """
        cloudspaceId = int(cloudspaceId)
        cloudspace = self.models.cloudspace.get(cloudspaceId)
        self.netmgr.fw_start(cloudspace.networkId)
        self.models.cloudspace.updateSearch({'id': cloudspaceId}, {'$set': {'status': 'DEPLOYED'}})
        return True

    @authenticator.auth(acl={'cloudspace': set('R')})
    def get(self, cloudspaceId, **kwargs):
        """
        Get cloudspace details

        :param cloudspaceId: id of the cloudspace
        :return dict with cloudspace details
        """
        cloudspaceObject = self.models.Cloudspace.get(cloudspaceId)

        cloudspace_acl = authenticator.auth({}).getCloudspaceAcl(cloudspaceObject)
        cloudspace = {"accountId": str(cloudspaceObject.account.id),
                      "acl": [{"right": ''.join(sorted(ace['right'])), "type": ace['type'],
                               "userGroupId": ace['userGroupId'], "status": ace['status'],
                               "canBeDeleted": ace['canBeDeleted']} for _, ace in
                              cloudspace_acl.items()],
                      "description": cloudspaceObject.description,
                      'updateTime': cloudspaceObject.updateTime,
                      'creationTime': cloudspaceObject.creationTime,
                      "id": str(cloudspaceObject.id),
                      "locationId": str(cloudspaceObject.location.id),
                      "name": cloudspaceObject.name,
                      "resourceLimits": cloudspaceObject.resourceLimits,
                      "externalnetworkip": getIP(cloudspaceObject.externalnetworkip),
                      "status": cloudspaceObject.status}
        return cloudspace

    @authenticator.auth(acl={'cloudspace': set('U')})
    def deleteUser(self, cloudspaceId, userId, recursivedelete=False, **kwargs):
        """
        Revoke user access from the cloudspace

        :param cloudspaceId: id of the cloudspace
        :param userId: id or emailaddress of the user to remove
        :param recursivedelete: recursively revoke access permissions from owned cloudspaces
                                and machines
        :return True if user access was revoked from cloudspace
        """

        cloudspace = self.cb.cloudspace.get(cloudspaceId)
        ace = {'type': 'U', 'userGroupId': userId}
        result = cloudspace.update(full_result=True, pull__acl=ace)
        if result['nModified'] == 0:
            raise exceptions.NotFound('User "%s" does not have access on the cloudspace' % userId)

        cloudspace.update(updateTime=int(time.time()))

        if recursivedelete:
            # Delete user accessrights from related machines (part of owned cloudspaces)
            self.models.VMachine.objects(cloudspace=cloudspace).update(pull__acl=ace)
        return True

    def list(self, **kwargs):
        """
        List all cloudspaces the user has access to

        :return list with every element containing details of a cloudspace as a dict
        """
        ctx = kwargs['ctx']
        user = ctx.env['beaker.session']['user']
        cloudspaceaccess = set()

        # get cloudspaces access via account
        q = {'acl.userGroupId': user}
        accountaccess = set(ac.id for ac in self.models.Account.find(q).only('id'))
        q = {'account': {'$in': list(accountaccess)}}
        cloudspaceaccess.update(cs.id for cs in self.models.Cloudspace.find(q).only('id'))

        # get cloudspaces access via atleast one vm
        q = {'acl.userGroupId': user, 'status': {'$ne': 'DESTROYED'}}
        cloudspaceaccess.update(vm['cloudspaceId'] for vm in self.models.VMachine.find(q).only('id'))

        q = {"$or": [{"acl.userGroupId": user},
                     {"id": {"$in": list(cloudspaceaccess)}}],
             "status": {"$ne": "DESTROYED"}}
        cloudspaces = self.models.Cloudspace.find(q)

        result = list()
        for cloudspaceobj in cloudspaces:
            cloudspace = cloudspaceobj.to_dict()
            cloudspace['externalnetworkip'] = getIP(cloudspaceobj.externalnetworkip)
            cloudspace['accountName'] = cloudspaceobj.account.name
            cloudspace_acl = authenticator.auth({}).getCloudspaceAcl(cloudspaceobj)
            cloudspace['acl'] = [{"right": ''.join(sorted(ace['right'])), "type": ace['type'],
                                  "status": ace['status'],
                                  "userGroupId": ace['userGroupId'],
                                  "canBeDeleted": ace['canBeDeleted']} for _, ace in
                                 cloudspace_acl.items()]
            for acl in cloudspaceobj.account.acl:
                if acl.userGroupId == user.lower() and acl.type == 'U':
                    cloudspace['accountAcl'] = acl.to_dict()
            result.append(cloudspace)

        return result

    # Unexposed actor
    def getConsumedMemoryCapacity(self, machines):
        """
        Calculate the total consumed memory by the machines in the cloudspace in GB

        :param cloudspaceId: id of the cloudspace that should be checked
        :return: the total consumed memory
        """
        consumedmemcapacity = 0

        for machine in machines:
            consumedmemcapacity += machine.memory

        return consumedmemcapacity / 1024.0

    # Unexposed actor
    def getConsumedCPUCores(self, machines):
        """
        Calculate the total number of consumed cpu cores by the machines in the cloudspace

        :param cloudspaceId: id of the cloudspace that should be checked
        :return: the total number of consumed cpu cores
        """
        numcpus = 0
        for machine in machines:
            numcpus += machine.vcpus

        return numcpus

    # Unexposed actor
    def getConsumedVDiskCapacity(self, machines):
        """
        Calculate the total consumed disk storage by the machines in the cloudspace in GB

        :param cloudspaceId: id of the cloudspace that should be checked
        :return: the total consumed disk storage
        """
        consumeddiskcapacity = 0

        for machine in machines:
            for disk in machine.disks:
                consumeddiskcapacity += disk.size

        return consumeddiskcapacity

    # Unexposed actor
    def getConsumedPublicIPs(self, cloudspace):
        """
        Calculate the total number of consumed public IPs by the machines in the cloudspace and the
        cloudspace itself

        :param cloudspaceId: id of the cloudspace that should be checked
        :return: the total number of consumed public IPs
        """
        numpublicips = 0

        # Add the public IP directly attached to the cloudspace
        if cloudspace.externalnetworkip:
            numpublicips += 1

        # Add the number of machines in cloudspace that have public IPs attached to them
        numpublicips += self.models.VMachine.find({'cloudspace': cloudspace.id,
                                                   'nics.type': 'PUBLIC',
                                                   'status': {'$nin': ['DESTROYED', 'ERROR']}}).count()

        return numpublicips

        # Unexposed actor

    def getConsumedNASCapacity(self, cloudspace):
        """
        Calculate the total consumed primary disk storage (NAS) by the machines in the cloudspace
        in TB

        :param cloudspaceId: id of the cloudspace that should be checked
        :return: the total consumed primary disk storage (NAS)
        """
        return 0

        # Unexposed actor

    # Unexposed actor
    def getConsumedNetworkOptTransfer(self, cloudspace):
        """
        Calculate the total sent/received network transfer in operator by the machines in the
        cloudspace in GB

        :param cloudspaceId: id of the cloudspace that should be checked
        :return: the total sent/received network transfer in operator
        """
        return 0

    # Unexposed actor
    def getConsumedNetworkPeerTransfer(self, cloudspace):
        """
        Calculate the total sent/received network transfer peering by the machines in the
        cloudspace in GB

        :param cloudspaceId: id of the cloudspace that should be checked
        :return: the total sent/received network transfer peering
        """
        return 0

    def _validateAvaliableAccountResources(self, cloudspace, maxMemoryCapacity=None,
                                           maxVDiskCapacity=None, maxCPUCapacity=None,
                                           maxNetworkPeerTransfer=None, maxNumPublicIP=None, excludecloudspace=True):
        """
        Validate that the required CU limits to be reserved for the cloudspace are available in
        the account

        :param cloudspace: cloudspace object
        :param maxMemoryCapacity: max size of memory in GB
        :param maxVDiskCapacity: max size of aggregated vdisks in GB
        :param maxCPUCapacity: max number of cpu cores
        :param maxNetworkPeerTransfer: max sent/received network transfer peering
        :param maxNumPublicIP: max number of assigned public IPs
        :param excludecloudspace: exclude the cloudspace being validated while performing the
            calculations
        :return: True if all required CUs are available in account
        """
        accountcus = cloudspace.account.resourceLimits
        self.cb.fillResourceLimits(accountcus)
        if excludecloudspace:
            excludecloudspaceid = cloudspace.id
        else:
            excludecloudspaceid = None

        reservedcus = j.apps.cloudapi.accounts.getReservedCloudUnits(cloudspace.account,
                                                                     excludecloudspaceid)

        if maxMemoryCapacity:
            avaliablememorycapacity = accountcus['CU_M'] - reservedcus['CU_M']
            if maxMemoryCapacity != -1 and accountcus['CU_M'] != -1 and maxMemoryCapacity > avaliablememorycapacity:
                raise exceptions.BadRequest("Owning account has only %s GB of unreserved memory, "
                                            "cannot reserve %s GB for this cloudspace" %
                                            (avaliablememorycapacity, maxMemoryCapacity))

        if maxVDiskCapacity:
            avaliablevdiskcapacity = accountcus['CU_D'] - reservedcus['CU_D']
            if maxVDiskCapacity != -1 and accountcus['CU_D'] != -1 and maxVDiskCapacity > avaliablevdiskcapacity:
                raise exceptions.BadRequest("Owning account has only %s GB of unreserved vdisk "
                                            "storage, cannot reserve %s GB for this cloudspace" %
                                            (avaliablevdiskcapacity, maxVDiskCapacity))

        if maxCPUCapacity:
            avaliablecpucapacity = accountcus['CU_C'] - reservedcus['CU_C']
            if maxCPUCapacity != -1 and accountcus['CU_C'] != -1 and maxCPUCapacity > avaliablecpucapacity:
                raise exceptions.BadRequest("Owning account has only %s unreserved CPU cores,  "
                                            "cannot reserve %s cores for this cloudspace" %
                                            (avaliablecpucapacity, maxCPUCapacity))

        if maxNetworkPeerTransfer:
            avaliablenetworkpeertransfer = accountcus['CU_NP'] - reservedcus['CU_NP']
            if maxNetworkPeerTransfer != -1 and accountcus['CU_NP'] != -1 and maxNetworkPeerTransfer > avaliablenetworkpeertransfer:
                raise exceptions.BadRequest("Owning account has only %s GB of unreserved network "
                                            "transfer, cannot reserve %s GB for this cloudspace" %
                                            (avaliablenetworkpeertransfer, maxNetworkPeerTransfer))
        if maxNumPublicIP:
            avaliablepublicips = accountcus['CU_I'] - reservedcus['CU_I']
            if maxNumPublicIP != -1 and accountcus['CU_I'] != -1 and maxNumPublicIP > avaliablepublicips:
                raise exceptions.BadRequest("Owning account has only %s unreserved public IPs, "
                                            "cannot reserve %s for this cloudspace" %
                                            (avaliablepublicips, maxNumPublicIP))
        return True

    @authenticator.auth(acl={'cloudspace': set('A')})
    def addAllowedSize(self, cloudspaceId, sizeId, **kwargs):
        """
        Adds size to the allowed set of sizes
        :param cloudspaceId: id of the cloudspace
        :param sizeId: id of the required size
        """
        if not self.models.size.exists(sizeId):
            raise exceptions.BadRequest("Please select a valid size")
        self.models.cloudspace.updateSearch({'id': cloudspaceId},
                                            {'$addToSet': {'allowedVMSizes': sizeId}})
        return True

    @authenticator.auth(acl={'cloudspace': set('A')})
    def removeAllowedSize(self, cloudspaceId, sizeId, **kwargs):
        """
        removes size to the allowed set of sizes
        :param cloudspaceId: id of the cloudspace
        :param sizeId: id of the required size
        """
        cloudspace = self.models.cloudspace.get(cloudspaceId)
        if sizeId in cloudspace.allowedVMSizes:
            self.models.cloudspace.updateSearch({'id': cloudspaceId},
                                                {'$pull': {'allowedVMSizes': sizeId}})
        else:
            raise exceptions.BadRequest("Specified size isn't included in the allowed sizes")
        return True

    @authenticator.auth(acl={'cloudspace': set('A')})
    def update(self, cloudspaceId, name=None, maxMemoryCapacity=None, maxVDiskCapacity=None,
               maxCPUCapacity=None, maxNetworkPeerTransfer=None, maxNumPublicIP=None, allowedVMSizes=None, **kwargs):
        """
        Update the cloudspace name and capacity parameters

        :param cloudspaceId: id of the cloudspace
        :param name: name of the cloudspace
        :param maxMemoryCapacity: max size of memory in GB
        :param maxVDiskCapacity: max size of aggregated vdisks in GB
        :param maxCPUCapacity: max number of cpu cores
        :param maxNetworkPeerTransfer: max sent/received network transfer peering
        :param maxNumPublicIP: max number of assigned public IPs
        :return: True if update was successful
        """
        cloudspace = self.models.Cloudspace.get(cloudspaceId)
        active_cloudspaces = self._listActiveCloudSpaces(cloudspace.accountId)
        machines = self.models.VMachine.objects(status__nin=['DESTROYED', 'ERROR'], cloudspace=cloudspace).only('id', 'size', 'disks')

        if name in [space['name'] for space in active_cloudspaces] and name != cloudspace.name:
            raise exceptions.Conflict('Cloud Space with name %s already exists.' % name)

        if name:
            cloudspace.name = name

        if allowedVMSizes:
            cloudspace.allowedVMSizes = allowedVMSizes

        if maxMemoryCapacity or maxVDiskCapacity or maxCPUCapacity or maxNetworkPeerTransfer or maxNumPublicIP:
            self._validateAvaliableAccountResources(cloudspace, maxMemoryCapacity,
                                                    maxVDiskCapacity, maxCPUCapacity,
                                                    maxNetworkPeerTransfer, maxNumPublicIP)

        if maxMemoryCapacity is not None:
            consumedmemcapacity = self.getConsumedMemoryCapacity(machines)
            if maxMemoryCapacity != -1 and maxMemoryCapacity < consumedmemcapacity:
                raise exceptions.BadRequest("Cannot set the maximum memory capacity to a value "
                                            "that is less than the current consumed memory "
                                            "capacity %s GB." % consumedmemcapacity)
            else:
                cloudspace.resourceLimits['CU_M'] = maxMemoryCapacity

        if maxVDiskCapacity is not None:
            consumedvdiskcapacity = self.getConsumedVDiskCapacity(machines)
            if maxVDiskCapacity != -1 and maxVDiskCapacity < consumedvdiskcapacity:
                raise exceptions.BadRequest("Cannot set the maximum vdisk capacity to a value that "
                                            "is less than the current consumed vdisk capacity %s "
                                            "GB." % consumedvdiskcapacity)
            else:
                cloudspace.resourceLimits['CU_D'] = maxVDiskCapacity

        if maxCPUCapacity is not None:
            consumedcpucapacity = self.getConsumedCPUCores(machines)
            if maxCPUCapacity != -1 and maxCPUCapacity < consumedcpucapacity:
                raise exceptions.BadRequest("Cannot set the maximum cpu cores to a value that "
                                            "is less than the current consumed cores %s ." %
                                            consumedcpucapacity)
            else:
                cloudspace.resourceLimits['CU_C'] = maxCPUCapacity

        if maxNetworkPeerTransfer is not None:
            transferednewtpeer = self.getConsumedNetworkPeerTransfer(cloudspaceId)
            if maxNetworkPeerTransfer != -1 and maxNetworkPeerTransfer < transferednewtpeer:
                raise exceptions.BadRequest("Cannot set the maximum network transfer peering "
                                            "to a value that is less than the current  "
                                            "sent/received %s GB." % transferednewtpeer)
            else:
                cloudspace.resourceLimits['CU_NP'] = maxNetworkPeerTransfer

        if maxNumPublicIP is not None:
            assingedpublicip = self.getConsumedPublicIPs(cloudspace)
            if maxNumPublicIP != -1 and maxNumPublicIP < 1:
                raise exceptions.BadRequest("Cloudspace must have reserve at least 1 Public IP "
                                            "address for its VFW")
            elif maxNumPublicIP != -1 and maxNumPublicIP < assingedpublicip:
                raise exceptions.BadRequest("Cannot set the maximum number of public IPs "
                                            "to a value that is less than the current "
                                            "assigned %s." % assingedpublicip)
            else:
                cloudspace.resourceLimits['CU_I'] = maxNumPublicIP
        cloudspace.updateTime = int(time.time())
        self.models.cloudspace.set(cloudspace)
        return True

    # Unexposed actor
    def getConsumedCloudUnits(self, cloudspace, **kwargs):
        """
        Calculate the currently consumed cloud units for resources in a cloudspace.
        Calculated cloud units are returned in a dict which includes:
        - CU_M: consumed memory in GB
        - CU_C: number of virtual cpu cores
        - CU_D: consumed virtual disk storage in GB
        - CU_I: number of public IPs

        :param cloudspaceId: id of the cloudspace consumption should be calculated for
        :return: dict with the consumed cloud units
        """
        consumedcudict = dict()
        machines = self.models.VMachine.objects(status__nin=['DESTROYED', 'ERROR'], cloudspace=cloudspace).only('id', 'size', 'disks')
        consumedcudict['CU_M'] = self.getConsumedMemoryCapacity(machines)
        consumedcudict['CU_C'] = self.getConsumedCPUCores(machines)
        consumedcudict['CU_D'] = self.getConsumedVDiskCapacity(machines)
        consumedcudict['CU_I'] = self.getConsumedPublicIPs(cloudspace)

        return consumedcudict

    @authenticator.auth(acl={'cloudspace': set('X')})
    def getDefenseShield(self, cloudspaceId, **kwargs):
        """
        Get information about the defense shield

        param:cloudspaceId id of the cloudspace
        :return dict with defense shield details
        """
        cloudspaceId = int(cloudspaceId)
        cloudspace = self.models.cloudspace.get(cloudspaceId)
        fwid = "%s_%s" % (cloudspace.gid, cloudspace.networkId)
        fw = self.netmgr._getVFWObject(fwid)

        pwd = str(uuid.uuid4())
        self.netmgr.fw_set_password(fwid, 'admin', pwd)
        urllocation = self.hrd.get('instance.openvcloud.cloudbroker.defense_proxy')
        location = self.models.location.search({'gid': cloudspace.gid})[1]

        url = '%s/ovcinit/%s/%s' % (urllocation, getIP(fw.host), location['locationCode'])
        result = {'user': 'admin', 'password': pwd, 'url': url}
        return result

    # Unexposed actor
    def checkAvailablePublicIPs(self, cloudspace, numips=1):
        """
        Check that the required number of ip addresses are available in the given cloudspace

        :param cloudspaceId: id of the cloudspace to check
        :param numips: the required number of public IP addresses that need to be free
        :return: True if check succeeds, otherwise raise a 400 BadRequest error
        """
        # Validate that there still remains enough public IP addresses to assign in account
        j.apps.cloudapi.accounts.checkAvailablePublicIPs(cloudspace.account, numips)

        # Validate that there still remains enough public IP addresses to assign in cloudspace
        resourcelimits = cloudspace.resourceLimits
        if 'CU_I' in resourcelimits:
            reservedcus = cloudspace.resourceLimits['CU_I']

            if reservedcus != -1:
                consumedcus = self.getConsumedPublicIPs(cloudspace)
                availablecus = reservedcus - consumedcus
                if availablecus < numips:
                    raise exceptions.BadRequest("Required actions will consume an extra %s public "
                                                "IP(s), owning cloudspace only has %s free IP(s)." %
                                                (numips, availablecus))

        return True

    # Unexposed actor
    def checkAvailableMachineResources(self, cloudspace, numcpus=0, memorysize=0, vdisksize=0, checkaccount=True):
        """
        Check that the required machine resources are available in the given cloudspace

        :param cloudspaceId: id of the cloudspace to check
        :param numcpus: the required number of cpu cores that need to be free
        :param memorysize: the required memory size in GB that need to be free
        :param vdisksize: the required vdisk size in GB that need to be free
        :param checkaccount: check account for available resources
        :return: True if check succeeds, otherwise raise a 400 BadRequest error
        """
        # Validate that there still remains enough public IP addresses to assign in cloudspace
        machines = self.models.VMachine.objects(status__nin=['DESTROYED', 'ERROR'], cloudspace=cloudspace).only('id', 'memory', 'vcpus', 'disks')
        resourcelimits = cloudspace.resourceLimits
        if checkaccount:
            j.apps.cloudapi.accounts.checkAvailableMachineResources(cloudspace.account, numcpus,
                                                                    memorysize, vdisksize)

        # Validate that there still remains enough cpu cores to assign in cloudspace
        if numcpus > 0 and 'CU_C' in resourcelimits:
            reservedcus = cloudspace.resourceLimits['CU_C']

            if reservedcus != -1:
                consumedcus = self.getConsumedCPUCores(machines)
                availablecus = reservedcus - consumedcus
                if availablecus < numcpus:
                    raise exceptions.BadRequest("Required actions will consume an extra %s core(s),"
                                                " owning cloudspace only has %s free core(s)." %
                                                (numcpus, availablecus))

        # Validate that there still remains enough memory capacity to assign in cloudspace
        if memorysize > 0 and 'CU_M' in resourcelimits:
            reservedcus = cloudspace.resourceLimits['CU_M']

            if reservedcus != -1:
                consumedcus = self.getConsumedMemoryCapacity(machines)
                availablecus = reservedcus - consumedcus
                if availablecus < memorysize:
                    raise exceptions.BadRequest("Required actions will consume an extra %s GB of "
                                                "memory, owning cloudspace only has %s GB of free "
                                                "memory space." % (memorysize, availablecus))

        # Validate that there still remains enough vdisk capacity to assign in cloudspace
        if vdisksize > 0 and 'CU_D' in resourcelimits:
            reservedcus = cloudspace.resourceLimits['CU_D']

            if reservedcus != -1:
                consumedcus = self.getConsumedVDiskCapacity(machines)
                availablecus = reservedcus - consumedcus
                if availablecus < vdisksize:
                    raise exceptions.BadRequest("Required actions will consume an extra %s GB of "
                                                "vdisk space, owning cloudspace only has %s GB of "
                                                "free vdisk space." % (vdisksize, availablecus))

        return True

    # Unexposed actor
    def getConsumedCloudUnitsInCloudspaces(self, cloudspaces, deployedcloudspaces, **kwargs):
        """
        Calculate the currently consumed cloud units for resources in a cloudspace.
        Calculated cloud units are returned in a dict which includes:
        - CU_M: consumed memory in GB
        - CU_C: number of virtual cpu cores
        - CU_D: consumed virtual disk storage in GB
        - CU_I: number of public IPs

        :param cloudspaceId: id of the cloudspace consumption should be calculated for
        :return: dict with the consumed cloud units
        """
        machines = self.models.VMachine.objects(status__nin=['DESTROYED', 'ERROR'], cloudspace__in=cloudspaces).only('id', 'size')
        consumedcudict = dict()
        consumedcudict['CU_M'] = self.getConsumedMemoryInCloudspaces(machines)
        consumedcudict['CU_C'] = self.getConsumedCPUCoresInCloudspaces(machines)
        consumedcudict['CU_D'] = 0
        # for calculating consumed ips we should consider only deployed cloudspaces
        consumedcudict['CU_I'] = self.getConsumedPublicIPsInCloudspaces(deployedcloudspaces)

        return consumedcudict

    # unexposed actor
    def getConsumedMemoryInCloudspaces(self, machines):
        """
        Calculate the total number of consumed memory by the machines in a given cloudspaces list

        :param cloudspacesIds: list of ids of the cloudspaces that should be checked
        :return: the total number of consumed memory
        """

        consumedmemcapacity = 0
        consumedmemcapacity = sum(m.size.memory for m in machines)
        return consumedmemcapacity / 1024.0

    # unexposed actor
    def getConsumedCPUCoresInCloudspaces(self, machines):
        """
        Calculate the total number of consumed cpu cores by the machines in a given cloudspaces list

        :param cloudspacesIds: list of ids of the cloudspaces that should be checked
        :return: the total number of consumed cpu cores
        """
        numcpus = 0
        numcpus = sum(m.size.vcpus for m in machines)
        return numcpus

    # unexposed actor
    def getConsumedPublicIPsInCloudspaces(self, cloudspaces):
        """
        Calculate the total number of consumed public IPs by the machines in a given cloudspaces list

        :param cloudspacesIds: list of ids of the cloudspaces that should be checked
        :return: the total number of consumed public IPs
        """
        numpublicips = 0
        # Add the public IP directly attached to the cloudspace
        for cloudspace in cloudspaces:
            if cloudspace.get('externalnetworkip'):
                numpublicips += 1

        # Add the number of machines in cloudspace that have public IPs attached to them
        cloudspaceids = [cs.id for cs in cloudspaces]
        numpublicips += self.models.vmachine.count({'cloudspaceId': {'$in': cloudspaceids},
                                                    'nics.type': 'PUBLIC',
                                                    'status': {'$nin': ['DESTROYED', 'ERROR']}})
        return numpublicips

    @authenticator.auth(acl={'cloudspace': set('X')})
    def getOpenvpnConfig(self, cloudspaceId, **kwargs):
        import zipfile
        from cStringIO import StringIO
        ctx = kwargs['ctx']
        cloudspace = self.models.cloudspace.get(cloudspaceId)
        if cloudspace.status != 'DEPLOYED':
            raise exceptions.NotFound('Can not get openvpn config for a cloudspace which is not deployed')
        fwid = "%s_%s" % (cloudspace.gid, cloudspace.networkId)
        config = self.cb.netmgr.fw_get_openvpn_config(fwid)
        ctx.start_response('200 OK', [('content-type', 'application/octet-stream'),
                                      ('content-disposition', "inline; filename = openvpn.zip")])
        fp = StringIO()
        zip = zipfile.ZipFile(fp, 'w')
        for filename, filecontent in config.items():
            zip.writestr(filename, filecontent)
        zip.close()
        return fp.getvalue()
