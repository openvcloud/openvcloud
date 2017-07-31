from js9 import j
from cloudbroker.actorlib import authenticator
from cloudbroker.actorlib.baseactor import BaseActor
from JumpScale9Portal.portal import exceptions


class cloudapi_accounts(BaseActor):
    """
    API Actor api for managing account

    """
    @authenticator.auth(acl={'account': set('U')})
    def addUser(self, accountId, userId, accesstype, **kwargs):
        """
        Give a registered user access rights

        :param accountId: id of the account
        :param userId: username or emailaddress of the user to grant access
        :param accesstype: 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        :return True if user was added successfully
        """
        account = self._get(accountId)
        user = self.cb.checkUser(userId, activeonly=False)
        if not user:
            raise exceptions.NotFound("User is not registered on the system")
        else:
            # Replace email address with name
            userId = user['name']

        self._addACE(account, userId, accesstype, userstatus='CONFIRMED')
        try:
            j.apps.cloudapi.users.sendShareResourceEmail(user, 'account', account, accesstype)
            return True
        except:
            self.deleteUser(accountId, userId, recursivedelete=False)
            raise

    def _get(self, accountId):
        account = self.models.Account.get(accountId)
        if not account:
            raise exceptions.NotFound('Account does not exist')
        return account

    def _addACE(self, account, userId, accesstype, userstatus='CONFIRMED'):
        """
        Add a new ACE to the ACL of the account

        :param account: account object
        :param userId: userid/email for registered users or emailaddress for unregistered users
        :param accesstype: 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        :param userstatus: status of the user (CONFIRMED or INVITED)
        :return True if ACE was added successfully
        """

        self.cb.isValidRole(accesstype)
        for ace in account.acl:
            if ace.userGroupId == userId:
                raise exceptions.BadRequest('User already has access rights to this account')

        ace = self.models.ACE(
            userGroupId=userId,
            type='U',
            right=accesstype,
            status=userstatus
        )
        account.update(add_to_set__acl=ace)
        return True

    @authenticator.auth(acl={'account': set('U')})
    def updateUser(self, accountId, userId, accesstype, **kwargs):
        """
        Update user access rights

        :param accountId: id of the account
        :param userId: userid/email for registered users or emailaddress for unregistered users
        :param accesstype: 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        :return True if user access was updated successfully
        """
        account = self._get(accountId)
        self.cb.isValidRole(accesstype)
        for ace in account.acl:
            if ace.userGroupId == userId:
                if not self.cb.isaccountuserdeletable(ace, account.acl):
                    raise exceptions.BadRequest('User is last admin on the account, cannot change '
                                                'user\'s access rights')
                break
        else:
            raise exceptions.NotFound('User does not have any access rights to update')

        self.models.account.updateSearch({'id': accountId, 'acl.userGroupId': userId},
                                         {'$set': {'acl.$.right': accesstype}})

        account.update(pull__acl=ace)
        ace.right = accesstype
        account.update(add_to_set__acl=ace)
        return True

    def create(self, name, access, maxMemoryCapacity=None, maxVDiskCapacity=None,
               maxCPUCapacity=None, maxNetworkPeerTransfer=None, maxNumPublicIP=None, **kwargs):
        """
        Create a extra an account (Method not implemented)

        :param name: name of account to create
        :param access: list of ids of users which have full access to this account
        :param maxMemoryCapacity: max size of memory in GB
        :param maxVDiskCapacity: max size of aggregated vdisks in GB
        :param maxCPUCapacity: max number of cpu cores
        :param maxNetworkPeerTransfer: max sent/received network transfer peering
        :param maxNumPublicIP: max number of assigned public IPs
        :return int
        """
        raise NotImplementedError("Not implemented method create")

    @authenticator.auth(acl={'account': set('R')})
    def get(self, accountId, **kwargs):
        """
        Get account details

        :param accountId: id of the account
        :return dict with the account details
        """
        account = self._get(accountId).to_dict()

        # Filter the acl (after removing the selected user) to only have admins
        admins = list(filter(lambda a: set(a['right']) == set('ARCXDU'), account['acl']))
        # Set canBeDeleted to True except for the last admin on the account (if more than 1 admin
        # on account then all can be deleted)
        for ace in account['acl']:
            if len(admins) <= 1 and ace in admins:
                ace['canBeDeleted'] = False
            else:
                ace['canBeDeleted'] = True
        return account

    @authenticator.auth(acl={'account': set('R')})
    def listTemplates(self, accountId, **kwargs):
        """
        List templates which can be managed by this account

        :param accountId: id of the account
        :return dict with the template images for the given account
        """
        fields = ['id', 'name', 'description', 'type', 'UNCPath', 'size', 'username', 'accountId', 'status']
        q = {'accountId': int(accountId)}
        query = {'$query': q, '$fields': fields}
        results = self.models.image.search(query)[1:]
        return results

    @authenticator.auth(acl={'account': set('U')})
    def deleteUser(self, accountId, userId, recursivedelete=False, **kwargs):
        """
        Revoke user access from the account

        :param acountId: id of the account
        :param userId: id or emailaddress of the user to remove
        :param recursivedelete: recursively revoke access permissions from owned cloudspaces
                                and machines
        :return True if user access was revoked from account
        """
        account = self._get(accountId)
        for ace in account.acl:
            if ace.userGroupId == userId:
                if not self.cb.isaccountuserdeletable(ace, account.acl):
                    raise exceptions.BadRequest("User '%s' is the last admin on the account '%s'" %
                                                (userId, account.name))
                break
        else:
            raise exceptions.NotFound('User "%s" does not have access on the account' % userId)

        ace = ace.to_dict()
        ace.pop('right')
        account.update(pull__acl=ace)

        if recursivedelete:
            # Delete user accessrights from owned cloudspaces
            cloudspaces = self.models.Cloudspace.objects(account=account).only('id')
            cloudspaces.update(pull__acl=ace)
            for cloudspace in cloudspaces:
                # Delete user accessrights from related machines (part of owned cloudspaces)
                self.models.VMachine.objects(cloudspace=cloudspace).update(pull__acl=ace)
        return True

    def list(self, **kwargs):
        """
        List all accounts the user has access to

        :return list with every element containing details of a account as a dict
        """
        ctx = kwargs['ctx']
        user = ctx.env['beaker.session']['user']
        fields = ['id', 'name', 'acl', 'creationTime', 'updateTime']
        q = {'acl.userGroupId': user, 'status': {'$in': ['DISABLED', 'CONFIRMED']}}
        accounts = []
        for account in self.models.Account.find(q).only(*fields):
            accountdict = account.to_dict()
            accounts.append({
                'id': str(account.id),
                'name': account.name,
                'acl': accountdict['acl'],
                'creationTime': account.creationTime,
                'updateTime': account.updateTime
            })

        return accounts

    @authenticator.auth(acl={'account': set('A')})
    def update(self, accountId, name=None, maxMemoryCapacity=None, maxVDiskCapacity=None,
               maxCPUCapacity=None, maxNetworkPeerTransfer=None, maxNumPublicIP=None, sendAccessEmails=None, **kwargs):
        """
        Update an account name or the maximum cloud units set on it
        Setting a cloud unit maximum to -1 will not put any restrictions on the resource

        :param accountId: id of the account to change
        :param name: name of the account
        :param maxMemoryCapacity: max size of memory in GB
        :param maxVDiskCapacity: max size of aggregated vdisks in GB
        :param maxCPUCapacity: max number of cpu cores
        :param maxNetworkPeerTransfer: max sent/received network transfer peering
        :param maxNumPublicIP: max number of assigned public IPs
        :return: True if update was successful
        """

        if sendAccessEmails == 1:
            sendAccessEmails = True
        elif sendAccessEmails == 0:
            sendAccessEmails = False

        accountobj = self.models.account.get(accountId)

        if name:
            accountobj.name = name

        if sendAccessEmails is not None:
            accountobj.sendAccessEmails = sendAccessEmails

        if maxMemoryCapacity or maxVDiskCapacity or maxCPUCapacity or maxNetworkPeerTransfer or maxNumPublicIP:
            reservedcloudunits = self.getReservedCloudUnits(accountId)

        if maxMemoryCapacity is not None:
            consumedmemcapacity = self._getConsumedCloudUnitsByType(accountobj, 'CU_M')
            if maxMemoryCapacity != -1 and maxMemoryCapacity < consumedmemcapacity:
                raise exceptions.BadRequest("Cannot set the maximum memory capacity to a value "
                                            "that is less than the current consumed memory "
                                            "capacity %s GB." % consumedmemcapacity)
            elif maxMemoryCapacity != -1 and maxMemoryCapacity < reservedcloudunits['CU_M']:
                raise exceptions.BadRequest("Cannot set the maximum memory capacity to a value "
                                            "that is less than the current reserved memory "
                                            "capacity %s GB by account's cloudspaces." %
                                            reservedcloudunits['CU_M'])
            else:
                accountobj.resourceLimits['CU_M'] = maxMemoryCapacity

        if maxVDiskCapacity is not None:
            consumedvdiskcapacity = self._getConsumedCloudUnitsByType(accountobj, 'CU_D')
            if maxVDiskCapacity != -1 and maxVDiskCapacity < consumedvdiskcapacity:
                raise exceptions.BadRequest("Cannot set the maximum vdisk capacity to a value that "
                                            "is less than the current consumed vdisk capacity %s "
                                            "GB." % consumedvdiskcapacity)
            elif maxVDiskCapacity != -1 and maxVDiskCapacity < reservedcloudunits['CU_D']:
                raise exceptions.BadRequest("Cannot set the maximum vdisk capacity to a value "
                                            "that is less than the current reserved vdisk "
                                            "capacity %s GB by account's cloudspaces." %
                                            reservedcloudunits['CU_D'])
            else:
                accountobj.resourceLimits['CU_D'] = maxVDiskCapacity

        if maxCPUCapacity is not None:
            consumedcpucapacity = self._getConsumedCloudUnitsByType(accountobj, 'CU_C')
            if maxCPUCapacity != -1 and maxCPUCapacity < consumedcpucapacity:
                raise exceptions.BadRequest("Cannot set the maximum cpu cores to a value that "
                                            "is less than the current consumed cores %s "
                                            "GB." % consumedcpucapacity)
            elif maxCPUCapacity != -1 and maxCPUCapacity < reservedcloudunits['CU_C']:
                raise exceptions.BadRequest("Cannot set the maximum cpu cores to a value "
                                            "that is less than the current reserved cpu cores "
                                            "%s by account's cloudspaces." %
                                            reservedcloudunits['CU_C'])
            else:
                accountobj.resourceLimits['CU_C'] = maxCPUCapacity

        if maxNetworkPeerTransfer is not None:
            transferednewtpeer = self._getConsumedCloudUnitsByType(accountobj, 'CU_NP')
            if maxNetworkPeerTransfer != -1 and maxNetworkPeerTransfer < transferednewtpeer:
                raise exceptions.BadRequest("Cannot set the maximum network transfer peering "
                                            "to a value that is less than the current  "
                                            "sent/received %s GB." % transferednewtpeer)
            elif maxNetworkPeerTransfer != -1 and maxNetworkPeerTransfer < reservedcloudunits['CU_NP']:
                raise exceptions.BadRequest("Cannot set the maximum  network transfer peering "
                                            "to a value that is less than the current reserved "
                                            "transfer %s GB by account's cloudspaces." %
                                            reservedcloudunits['CU_NP'])
            else:
                accountobj.resourceLimits['CU_NP'] = maxNetworkPeerTransfer

        if maxNumPublicIP is not None:
            assingedpublicip = self._getConsumedCloudUnitsByType(accountobj, 'CU_I')
            if maxNumPublicIP != -1 and maxNumPublicIP < assingedpublicip:
                raise exceptions.BadRequest("Cannot set the maximum number of public IPs "
                                            "to a value that is less than the current "
                                            "assigned %s." % assingedpublicip)
            elif maxNumPublicIP != -1 and maxNumPublicIP < reservedcloudunits['CU_I']:
                raise exceptions.BadRequest("Cannot set the maximum number of public IPs to a "
                                            "value that is less than the current reserved "
                                            "%s by account's cloudspaces."
                                            % reservedcloudunits['CU_I'])
            else:
                accountobj.resourceLimits['CU_I'] = maxNumPublicIP

        self.models.account.set(accountobj)
        return True

    # Unexposed actor
    def getConsumedVDiskCapacity(self, account):
        """
        Calculate the total consumed disk storage in the account in GB

        :param accountId: id of the accountId that should be checked
        :return: the total consumed disk storage
        """
        disks = self.models.Disk.objects(account=account.id).only('size')
        consumeddiskcapacity = sum([d['size'] for d in disks])
        return consumeddiskcapacity

    @authenticator.auth(acl={'account': set('R')})
    def getConsumedCloudUnits(self, accountId, **kwargs):
        """
        Calculate the currently consumed cloud units for all cloudspaces in the account.

        Calculated cloud units are returned in a dict which includes:
        - CU_M: consumed memory in GB
        - CU_C: number of virtual cpu cores
        - CU_D: consumed virtual disk storage in GB
        - CU_S: consumed primary storage (NAS) in TB
        - CU_A: consumed secondary storage (Archive) in TB
        - CU_NO: sent/received network transfer in operator in GB
        - CU_NP: sent/received network transfer peering in GB
        - CU_I: number of public IPs

        :param accountId: id of the account consumption should be calculated for
        :return: dict with the consumed cloud units
        """
        consumedcudict = {'CU_M': 0, 'CU_C': 0, 'CU_D': 0, 'CU_I': 0}
        # The following keys are unimplemented cloud unit consumptions, will set to 0 until
        # consumption is properly calculated
        unimplementedcu = {'CU_S': 0, 'CU_A': 0, 'CU_NO': 0, 'CU_NP': 0}

        cloudspaces = self.models.Cloudspace.objects(account=accountId).only('id', 'status')
        deployedcloudspaces = list(filter(lambda sp: sp.status == 'DEPLOYED', cloudspaces))
        consumedcudict = j.apps.cloudapi.cloudspaces.getConsumedCloudUnitsInCloudspaces(
            cloudspaces, deployedcloudspaces)

        consumedcudict.update(unimplementedcu)
        # Calculate disks on account level so as not to miss unattached disks
        consumedcudict['CU_D'] = self.getConsumedVDiskCapacity(accountId)
        return consumedcudict

    @authenticator.auth(acl={'account': set('R')})
    def getConsumedCloudUnitsByType(self, accountId, cutype, **kwargs):
        account = self.models.Account.get(accountId)
        if not account:
            raise exceptions.NotFound("Account with id %s does not exists".format(accountId))
        return self._getConsumedCloudUnitsByType(account, cutype, **kwargs)

    def _getConsumedCloudUnitsByType(self, account, cutype, **kwargs):
        """
        Calculate the currently consumed cloud units of the specified type for all cloudspaces
        in the account.

        Possible types of cloud units are include:
        - CU_M: returns consumed memory in GB
        - CU_C: returns number of virtual cpu cores
        - CU_D: returns consumed virtual disk storage in GB
        - CU_A: returns consumed secondary storage (Archive) in TB
        - CU_NP: returns sent/received network transfer peering in GB
        - CU_I: returns number of public IPs

        :param accountId: id of the account consumption should be calculated for
        :param cutype: cloud unit resource type
        :return: float/int for the consumed cloud unit of the specified type
        """
        consumedamount = 0
        # get all cloudspaces in this account
        cloudspaces = self.models.Cloudspace.objects(account=account.id).only('id')
        machines = self.models.VMachine.objects(status__nin=['DESTROYED', 'ERROR'], cloudspace__in=cloudspaces).only('id', 'size')

        # For the following cloud unit types 'CU_S', 'CU_A', 'CU_NO', 'CU_NP', 0 will be returned
        # until proper consumption calculation is implemented
        if cutype == 'CU_M':
            consumedamount = j.apps.cloudapi.cloudspaces.getConsumedMemoryInCloudspaces(machines)
        elif cutype == 'CU_C':
            consumedamount = j.apps.cloudapi.cloudspaces.getConsumedCPUCoresInCloudspaces(machines)
        elif cutype == 'CU_D':
            consumedamount = self.getConsumedVDiskCapacity(account)
        elif cutype == 'CU_NP':
            return 0
        elif cutype == 'CU_I':
            # for calculating consumed ips we should consider only deployed cloudspaces
            deployedcloudspaces = self.models.Cloudspace.objects(account=account.id, status='DEPLOYED').only('id')
            consumedamount = j.apps.cloudapi.cloudspaces.getConsumedPublicIPsInCloudspaces(deployedcloudspaces)
        else:
            raise exceptions.BadRequest('Invalid cloud unit type: %s' % cutype)

        return consumedamount

    # Unexposed actor
    def getReservedCloudUnits(self, account, excludecloudspaceid=None, **kwargs):
        """
        Calculate the currently reserved cloud units by all cloudspaces under an account

        Reserved cloud units will be calculated by summing up all cloud unit limits set on the
        cloudspaces in the account (cloudspaces with unlimited CUs, set to -1, will not be counted
        as they do not reserve any resources)

        Reserved cloud units are returned in a dict which includes:
        - CU_M: consumed memory in GB
        - CU_C: number of virtual cpu cores
        - CU_D: consumed virtual disk storage in GB
        - CU_NP: sent/received network transfer peering in GB
        - CU_I: number of public IPs

        :param accountId: id of the account reserved CUs should be calculated for
        :param excludecloudspaceid: exclude the cloudspace with the specified id when performing the
            calculations
        :return: dict with the reserved cloud units
        """
        reservedcudict = {'CU_M': 0, 'CU_C': 0, 'CU_D': 0, 'CU_I': 0, 'CU_NP': 0}

        # Aggregate the total consumed cloud units for all cloudspaces in the account
        for cloudspace in self.models.Cloudspace.objects(account=account, status__ne='DESTROYED'):
            if excludecloudspaceid is not None and cloudspace.id == excludecloudspaceid:
                continue

            for cukey, cuvalue in cloudspace.resourceLimits.items():
                # Ignore cu limit if -1 as it indicates that no limit is set
                if cukey in reservedcudict and cuvalue != -1:
                    reservedcudict[cukey] += cuvalue

        return reservedcudict

    # Unexposed actor
    def checkAvailablePublicIPs(self, account, numips=1):
        """
        Check that the required number of ip addresses are available in the given account

        :param accountId: id of the account to check
        :param numips: the required number of public IP addresses that need to be free
        :return: True if check succeeds, otherwise raise a 400 BadRequest error
        """
        # Validate that there still remains enough public IP addresses to assign in account
        resourcelimits = account.resourceLimits
        if 'CU_I' in resourcelimits:
            reservedcus = resourcelimits['CU_I']

            if reservedcus != -1:
                consumedcus = self._getConsumedCloudUnitsByType(account, 'CU_I')
                availablecus = reservedcus - consumedcus
                if availablecus < numips:
                    raise exceptions.BadRequest("Required actions will consume an extra %s public IP(s),"
                                                " owning account only has %s free IP(s)." % (numips,
                                                                                             availablecus))
        return True

    # Unexposed actor
    def checkAvailableMachineResources(self, account, numcpus=0, memorysize=0, vdisksize=0):
        """
        Check that the required machine resources are available in the given account

        :param accountId: id of the accountId to check
        :param numcpus: the required number of cpu cores that need to be free
        :param memorysize: the required memory size in GB that need to be free
        :param vdisksize: the required vdisk size in GB that need to be free
        :return: True if check succeeds, otherwise raise a 400 BadRequest error
        """
        resourcelimits = account.resourceLimits

        # Validate that there still remains enough cpu cores to assign in account
        if numcpus > 0 and 'CU_C' in resourcelimits:
            reservedcus = account.resourceLimits['CU_C']

            if reservedcus != -1:
                consumedcus = self._getConsumedCloudUnitsByType(account, 'CU_C')
                availablecus = reservedcus - consumedcus
                if availablecus < numcpus:
                    raise exceptions.BadRequest("Required actions will consume an extra %s core(s),"
                                                " owning account only has %s free core(s)." %
                                                (numcpus, availablecus))

        # Validate that there still remains enough memory capacity to assign in account
        if memorysize > 0 and 'CU_M' in resourcelimits:
            reservedcus = account.resourceLimits['CU_M']

            if reservedcus != -1:
                consumedcus = self._getConsumedCloudUnitsByType(account, 'CU_M')
                availablecus = reservedcus - consumedcus
                if availablecus < memorysize:
                    raise exceptions.BadRequest("Required actions will consume an extra %s GB of "
                                                "memory, owning account only has %s GB of free "
                                                "memory space." % (memorysize, availablecus))

        # Validate that there still remains enough vdisk capacity to assign in account
        if vdisksize > 0 and 'CU_D' in resourcelimits:
            reservedcus = account.resourceLimits['CU_D']

            if reservedcus != -1:
                consumedcus = self._getConsumedCloudUnitsByType(account, 'CU_D')
                availablecus = reservedcus - consumedcus
                if availablecus < vdisksize:
                    raise exceptions.BadRequest("Required actions will consume an extra %s GB of "
                                                "vdisk space, owning account only has %s GB of "
                                                "free vdisk space." % (vdisksize, availablecus))

        return True

    @authenticator.auth(acl={'account': set('R')})
    def getConsumption(self, accountId, start, end, **kwargs):
        import datetime
        import zipfile
        from cStringIO import StringIO
        import os
        import glob

        ctx = kwargs['ctx']
        start_time = datetime.datetime.utcfromtimestamp(start)
        end_time = datetime.datetime.utcfromtimestamp(end)
        root_path = "/opt/jumpscale7/var/resourcetracking/"
        account_path = os.path.join(root_path, str(accountId))
        pathes = glob.glob(os.path.join(account_path, '*/*/*/*'))
        pathes_in_range = list()
        for path in pathes:
            path_list = path.split("/")
            path_date = datetime.datetime(int(path_list[-4]), int(path_list[-3]),
                                          int(path_list[-2]), int(path_list[-1]))
            if path_date >= start_time and path_date <= end_time:
                pathes_in_range.append(path)
        ctx.start_response('200 OK', [('content-type', 'application/octet-stream'),
                                      ('content-disposition', "inline; filename = account.zip")])
        fp = StringIO()
        zip = zipfile.ZipFile(fp, 'w', zipfile.ZIP_DEFLATED)
        for path in pathes_in_range:
            file_path = os.path.join(path, 'account_capnp.bin')
            zip.write(file_path, file_path.replace(root_path, ''))
        zip.close()
        return fp.getvalue()
