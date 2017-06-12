[actor] @dbtype:mem,fs
    """
    Operator actions for interventions on accounts
    """
    method:disable
        """
        disable an account.
        """
        var:accountId str,,ID of account
        var:reason str,,reason of disabling the account

    method:enable
        """
        enable an account.
        """
        var:accountId str,,ID of account to enable
        var:reason str,,reason of enabling the account

    method:delete
        """
        Complete delete an account from the system
        """"
        var:accountId str,,ID of account to delete
        var:reason str,,reason for deleting the account


    method:deleteAccounts
        """
        Complete delete accounts from the system
        """"
        var:accountIds list(int),, list of account ids to delete
        var:reason str,,reason for deleting the account

    method:addUser
        """
        Give a user access rights.
        """"
        var:accountId str,,ID of account to add to
        var:username str,,name of the user to be given rights
        var:accesstype str,, 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin

    method:deleteUser
        """
        Delete user from account.
        """"
        var:accountId str,,ID of account to remove from
        var:username str,,name of the user to be removed
        var:recursivedelete bool,, recursively delete access rights from owned cloudspaces and vmachines


    method:create
        """
        Create Account.
        Setting a cloud unit maximum to -1 or empty will not put any restrictions on the resource
        """"
        var:name str,, Display name @tags validator:name
        var:username str,, name of the account @tags validator:username
        var:emailaddress str,,email @optional
        var:maxMemoryCapacity float,-1, max size of memory in GB @optional
        var:maxVDiskCapacity int,-1, max size of aggregated vdisks in GB @optional
        var:maxCPUCapacity int,-1, max number of cpu cores @optional
        var:maxNetworkPeerTransfer int,-1, max sent/received network transfer peering @optional
        var:maxNumPublicIP int,-1, max number of assigned public IPs @optional
        var:sendAccessEmails bool,True, if true send emails when a user is granted access to resources @optional

    method:update
        """
        Update Account.
        Setting a cloud unit maximum to -1 ore empty will not put any restrictions on the resource
        """"
        var:accountId str,,ID of account
        var:name str,, Display name @tags validator:name
        var:maxMemoryCapacity float,, max size of memory in GB @optional
        var:maxVDiskCapacity int,, max size of aggregated vdisks in GB @optional
        var:maxCPUCapacity int,, max number of cpu cores @optional
        var:maxNetworkPeerTransfer int,, max sent/received network transfer peering @optional
        var:maxNumPublicIP int,, max number of assigned public IPs @optional
        var:sendAccessEmails bool,True, if true send emails when a user is granted access to resources @optional
