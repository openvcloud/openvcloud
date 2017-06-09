from js9 import j

class cloudbroker_account(j.code.classGetBase()):
    """
    Operator actions for interventions on accounts
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="account"
        self.appname="cloudbroker"
        #cloudbroker_account_osis.__init__(self)


    def addUser(self, accountId, username, accesstype, **kwargs):
        """
        Give a user access rights.
        param:accountId ID of account to add to
        param:username name of the user to be given rights
        param:accesstype 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method addUser")

    def create(self, name, username, emailaddress, maxMemoryCapacity=-1.0, maxVDiskCapacity=-1, maxCPUCapacity=-1, maxNetworkPeerTransfer=-1, maxNumPublicIP=-1, sendAccessEmails=True, **kwargs):
        """
        Create Account.
        Setting a cloud unit maximum to -1 or empty will not put any restrictions on the resource
        param:name Display name
        param:username name of the account
        param:emailaddress email
        param:maxMemoryCapacity max size of memory in GB default=-1.0
        param:maxVDiskCapacity max size of aggregated vdisks in GB default=-1
        param:maxCPUCapacity max number of cpu cores default=-1
        param:maxNetworkPeerTransfer max sent/received network transfer peering default=-1
        param:maxNumPublicIP max number of assigned public IPs default=-1
        param:sendAccessEmails if true send emails when a user is granted access to resources default=True
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method create")

    def delete(self, accountId, reason, **kwargs):
        """
        Complete delete an account from the system
        param:accountId ID of account to delete
        param:reason reason for deleting the account
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method delete")

    def deleteAccounts(self, accountIds, reason, **kwargs):
        """
        Complete delete accounts from the system
        param:accountIds list of account ids to delete
        param:reason reason for deleting the account
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method deleteAccounts")

    def deleteUser(self, accountId, username, recursivedelete, **kwargs):
        """
        Delete user from account.
        param:accountId ID of account to remove from
        param:username name of the user to be removed
        param:recursivedelete recursively delete access rights from owned cloudspaces and vmachines
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method deleteUser")

    def disable(self, accountId, reason, **kwargs):
        """
        disable an account.
        param:accountId ID of account
        param:reason reason of disabling the account
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method disable")

    def enable(self, accountId, reason, **kwargs):
        """
        enable an account.
        param:accountId ID of account to enable
        param:reason reason of enabling the account
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method enable")

    def update(self, accountId, name, maxMemoryCapacity, maxVDiskCapacity, maxCPUCapacity, maxNetworkPeerTransfer, maxNumPublicIP, sendAccessEmails=True, **kwargs):
        """
        Update Account.
        Setting a cloud unit maximum to -1 ore empty will not put any restrictions on the resource
        param:accountId ID of account
        param:name Display name
        param:maxMemoryCapacity max size of memory in GB
        param:maxVDiskCapacity max size of aggregated vdisks in GB
        param:maxCPUCapacity max number of cpu cores
        param:maxNetworkPeerTransfer max sent/received network transfer peering
        param:maxNumPublicIP max number of assigned public IPs
        param:sendAccessEmails if true send emails when a user is granted access to resources default=True
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method update")
