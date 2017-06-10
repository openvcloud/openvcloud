from js9 import j

class cloudapi_accounts(j.tools.code.classGetBase()):
    """
    API Actor api for managing account
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="accounts"
        self.appname="cloudapi"
        #cloudapi_accounts_osis.__init__(self)


    def addUser(self, accountId, userId, accesstype, **kwargs):
        """
        Give a registered user access rights
        param:accountId id of the account
        param:userId username or emailaddress of the user to grant access
        param:accesstype 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        result bool,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method addUser")

    def create(self, name, access, maxMemoryCapacity='-1', maxVDiskCapacity=-1, maxCPUCapacity=-1, maxNetworkPeerTransfer=-1, maxNumPublicIP=-1, **kwargs):
        """
        Create a extra an account (Method not implemented)
        param:name name of account to create
        param:access list of ids of users which have full access to this account
        param:maxMemoryCapacity max size of memory in GB default=-1
        param:maxVDiskCapacity max size of aggregated vdisks in GB default=-1
        param:maxCPUCapacity max number of cpu cores default=-1
        param:maxNetworkPeerTransfer max sent/received network transfer peering default=-1
        param:maxNumPublicIP max number of assigned public IPs default=-1
        result int,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method create")

    def delete(self, accountId, **kwargs):
        """
        Delete an account (Method not implemented)
        param:accountId id of the account
        result bool,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method delete")

    def deleteUser(self, accountId, userId, recursivedelete=False, **kwargs):
        """
        Revoke user access from the account
        param:accountId id of the account
        param:userId id or emailaddress of the user to remove
        param:recursivedelete recursively revoke access rights from owned cloudspaces and vmachines default=False
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method deleteUser")

    def get(self, accountId, **kwargs):
        """
        Get account details
        param:accountId id of the account
        result dict,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method get")

    def getConsumedCloudUnits(self, accountId, **kwargs):
        """
        Calculate the currently consumed cloud units for all cloudspaces in the account.
        Calculated cloud units are returned in a dict which includes:
        - CU_M: consumed memory in GB
        - CU_C: number of cpu cores
        - CU_D: consumed vdisk storage in GB
        - CU_I: number of public IPs
        param:accountId id of the account consumption should be calculated for
        result dict,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getConsumedCloudUnits")

    def getConsumedCloudUnitsByType(self, accountId, cutype, **kwargs):
        """
        Calculate the currently consumed cloud units of the specified type for all cloudspaces
        in the account.
        Possible types of cloud units are include:
        - CU_M: returns consumed memory in GB
        - CU_C: returns number of virtual cpu cores
        - CU_D: returns consumed virtual disk storage in GB
        - CU_S: returns consumed primary storage (NAS) in TB
        - CU_A: returns consumed secondary storage (Archive) in TB
        - CU_NO: returns sent/received network transfer in operator in GB
        - CU_NP: returns sent/received network transfer peering in GB
        - CU_I: returns number of public IPs
        param:accountId id of the account consumption should be calculated for
        param:cutype cloud unit resource type
        result float,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getConsumedCloudUnitsByType")

    def getConsumption(self, accountId, start, end, **kwargs):
        """
        download the resources traking files for an account within a given period
        param:accountId id of the account
        param:start epoch represents the start time
        param:end epoch represents the end time
        result str,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getConsumption")

    def list(self, **kwargs):
        """
        List all accounts the user has access to
        result [],
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method list")

    def listTemplates(self, accountId, **kwargs):
        """
        List templates which can be managed by this account
        param:accountId id of the account
        result dict,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method listTemplates")

    def update(self, accountId, name, maxMemoryCapacity, maxVDiskCapacity, maxCPUCapacity, maxNetworkPeerTransfer, maxNumPublicIP, sendAccessEmails, **kwargs):
        """
        Update an account name and resource limits
        param:accountId id of the account to change
        param:name name of the account
        param:maxMemoryCapacity max size of memory in GB
        param:maxVDiskCapacity max size of aggregated vdisks in GB
        param:maxCPUCapacity max number of cpu cores
        param:maxNetworkPeerTransfer max sent/received network transfer peering
        param:maxNumPublicIP max number of assigned public IPs
        param:sendAccessEmails if true send emails when a user is granted access to resources
        result bool,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method update")

    def updateUser(self, accountId, userId, accesstype, **kwargs):
        """
        Update user access rights
        param:accountId id of the account
        param:userId userid/email for registered users or emailaddress for unregistered users
        param:accesstype 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        result bool,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method updateUser")
