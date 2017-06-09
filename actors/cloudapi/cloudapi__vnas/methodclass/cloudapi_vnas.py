from js9 import j
import random
import string


class cloudapi_vnas(j.code.classGetBase()):

    """
    API Actor api for managing VNAS
    """

    def __init__(self):
        pass

        self._te = {}
        self.actorname = "vnas"
        self.appname = "cloudapi"
        # Should be configurable!!
        con = j.ssh.connect('10.101.104.128', port=1501, keypath='/root/.ssh/id_rsa')
        self.sambacl = j.ssh.samba.get(con)
        # cloudapi_vnas_osis.__init__(self)

    def addApplication(self, appname, sharename, cloudspace, readonly, **kwargs):
        """
        Give an application access to a share.
        Access rights can be 'R' or 'W'
        param:appname name of the app
        param:share name of the share to give access on
        param:readonly True for read only access
        result bool
        """
        appsecret = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(12))
        appname = '%s[%s]' % (cloudspace, appname)
        self.sambacl.addUser(appname, appsecret)
        return self.sambacl.grantaccess(appname, sharename, cloudspace, readonly)

    def createShare(self, sharename, cloudspace, **kwargs):
        """
        Create a share
        param:sharename name of share to create
        param:cloudspace name of cloudpsace
        result boolean
        """
        return self.sambacl.addSubShare(sharename, cloudspace)

    def deleteShare(self, sharename, cloudspace, **kwargs):
        """
        Delete a share
        param:name name of the share
        param:path path of share
        result bool,
        """
        return self.sambacl.removeSubShare(sharename, cloudspace)

    def listShares(self, cloudspace, **kwargs):
        """
        List shares.
        result [],
        """
        return self.sambacl.listSubShares(cloudspace)

    def removeApplication(self, appname, sharename, cloudspace, readonly, **kwargs):
        """
        Revoke a user's access to the share
        param:share name of share
        param:appname name of the application to revoke
        result 
        """
        appname = '%s[%s]' % (cloudspace, appname)
        return revokeaccess(appname, sharename, cloudspace, readonly)
