from js9 import j

class cloudbroker_user(j.code.classGetBase()):
    """
    Operator actions for interventions specific to a user
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="user"
        self.appname="cloudbroker"
        #cloudbroker_user_osis.__init__(self)


    def create(self, username, emailaddress, password, groups, **kwargs):
        """
        Create a user
        param:username id of user
        param:emailaddress emailaddresses of the user
        param:password password of user
        param:groups list of groups this user belongs to
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method create")

    def delete(self, username, **kwargs):
        """
        Delete a user
        param:username id of user
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method delete")

    def deleteByGuid(self, userguid, **kwargs):
        """
        Delete a user using the user guid
        Note: This actor can also be called using username instead of guid to workaround CBGrid
        allowing userguid or username
        param:userguid guid of user
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method deleteByGuid")

    def deleteUsers(self, userIds, **kwargs):
        """
        Bulk delete a list of users
        param:userIds List of user ids
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method deleteUsers")

    def generateAuthorizationKey(self, username, **kwargs):
        """
        Generates a valid authorizationkey in the context of a specific user.
        This key can be used in a webbrowser to browse the cloud portal from the perspective of that specific user or to use the api in his/her authorization context
        param:username name of the user an authorization key is required for
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method generateAuthorizationKey")

    def sendResetPasswordLink(self, username, **kwargs):
        """
        send reset password of user to their email address
        param:username id of user
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method sendResetPasswordLink")

    def updatePassword(self, username, password, **kwargs):
        """
        Update user's password
        param:username id of user to reset password for
        param:password new password
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method updatePassword")
