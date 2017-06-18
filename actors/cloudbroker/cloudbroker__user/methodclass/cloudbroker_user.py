from js9 import j
from JumpScale9Portal.portal.auth import auth
from cloudbroker.actorlib.baseactor import BaseActor
from JumpScale9Portal.portal import exceptions
import hashlib
import time


class cloudbroker_user(BaseActor):
    """
    Operator actions for interventions specific to a user
    """
    def generateAuthorizationKey(self, username, **kwargs):
        """
        Generates a valid authorizationkey in the context of a specific user.
        This key can be used in a webbrowser to browse the cloud portal from the perspective of that specific user or to use the api in his/her authorization context
        param:username name of the user an authorization key is required for
        """
        user = self.cb.checkUser(username)
        if not user:
            raise exceptions.NotFound("User with name %s does not exists" % username)
        return self.cb.actors.cloudapi.users.authenticate(username=username, password=user['passwd'])

    @auth(['level1', 'level2', 'level3'])
    def updatePassword(self, username, password, **kwargs):
        user = self.cb.checkUser(username)
        if not user:
            raise exceptions.NotFound("User with name %s does not exists" % username)
        user['passwd'] = hashlib.md5(password).hexdigest()
        self.syscl.user.set(user)
        return True

    @auth(['level1', 'level2', 'level3'])
    def create(self, username, emailaddress, password, groups, **kwargs):
        groups = groups or []
        created = j.portal.tools.server.active.auth.createUser(
            username, password, emailaddress, groups, None)
        if created:
            primaryemailaddress = emailaddress[0]
            self.cb.updateResourceInvitations(username, primaryemailaddress)

        return True

    @auth(['level1', 'level2', 'level3'])
    def sendResetPasswordLink(self, username, **kwargs):
        user = self.cb.checkUser(username)
        if not user:
            raise exceptions.NotFound("User with name %s does not exists" % username)
        email = user['emails']
        return self.cb.actors.cloudapi.users.sendResetPasswordLink(emailaddress=email)

    @auth(['level1', 'level2', 'level3'])
    def deleteUsers(self, userIds, **kwargs):
        ctx = kwargs['ctx']
        ctx.events.runAsync(self._deleteUsers,
                            args=(userIds, ctx),
                            kwargs={},
                            title='Deleting Users',
                            success='Users deleted successfully',
                            error='Failed to delete users')

    def _deleteUsers(self, userIds, ctx):
        for idx, username in enumerate(userIds):
            ctx.events.sendMessage("Deleting Users", 'Deleting User %s/%s' %
                                   (idx + 1, len(userIds)))
            try:  # BULK ACTION
                self.delete(username)
            except exceptions.BadRequest:
                pass

    @auth(['level1', 'level2', 'level3'])
    def delete(self, username, **kwargs):
        """
        Delete the user from all ACLs and set user status to inactive

        :param username: username of the user to delete
        :return: True if deletion was successful
        """
        user = self.cb.checkUser(username)
        if not user:
            raise exceptions.NotFound("User with name %s does not exists" % username)
        else:
            userobj = self.syscl.user.get(user['id'])

        query = {'acl.userGroupId': username, 'acl.type': 'U'}
        # Delete user from all accounts, if account status is Destoryed then delete without
        # further validation
        accountswiththisuser = self.models.account.search(query)[1:]
        for account in accountswiththisuser:
            if account['status'] in ['DESTROYED', 'DESTROYING']:
                # Delete immediately without further checks
                accountobj = self.models.account.get(account['guid'])
                accountobj.acl = filter(lambda a: a.userGroupId != username, accountobj.acl)
                self.models.account.set(accountobj)
            else:
                j.apps.cloudbroker.account.deleteUser(accountId=account['id'], username=username,
                                                      recursivedelete=True)

        # Delete user from cloudspaces
        cloudspaceswiththisuser = self.models.cloudspace.search(query)[1:]
        for cloudspace in cloudspaceswiththisuser:
            j.apps.cloudbroker.cloudspace.deleteUser(cloudspaceId=cloudspace['id'],
                                                     username=username, recursivedelete=True)
        # Delete user from vmachines
        machineswiththisuser = self.models.vmachine.search(query)[1:]
        for machine in machineswiththisuser:
            j.apps.cloudbroker.machine.deleteUser(machineId=machine['id'], username=username)

        # Set the user to inactive
        userobj.active = False
        gid = userobj.gid
        uid = userobj.id
        userobj.id = 'DELETED_%i_%s' % (time.time(), uid)
        userobj.guid = '%s_DELETED_%i_%s' % (gid, time.time(), uid)
        userobj.protected = False
        self.syscl.user.delete(uid)
        self.syscl.user.set(userobj)
        self.syscl.sessioncache.deleteSearch({'user': uid})

        return True

    @auth(['level1', 'level2', 'level3'])
    def deleteByGuid(self, userguid, **kwargs):
        """
        Delete the user from all ACLs and set user status to inactive
        Note: This actor can also be called using username instead of guid to workaround CBGrid
        allowing userguid or username

        :param userguid: guid of the user to delete
        :return: True if deletion was successful
        """
        if userguid.count("_"):
            users = self.syscl.user.search({'guid': userguid})[1:]
            username = users[0]['id']
        else:
            username = userguid
        return self.delete(username)
