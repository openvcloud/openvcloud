from js9 import j

class cloudapi_users(j.code.classGetBase()):
    """
    User management
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="users"
        self.appname="cloudapi"
        #cloudapi_users_osis.__init__(self)


    def authenticate(self, username, password, **kwargs):
        """
        The function evaluates the provided username and password and returns a session key.
        The session key can be used for doing api requests. E.g this is the authkey parameter in every actor request.
        A session key is only vallid for a limited time.
        param:username username to validate
        param:password password to validate
        result str,,session
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method authenticate")

    def get(self, username, **kwargs):
        """
        Get information of a existing username based on username id
        param:username username of the user
        result dict,,user
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method get")

    def getMatchingUsernames(self, usernameregex, limit=5, **kwargs):
        """
        Get a list of the matching usernames for a given string
        param:usernameregex regex of the usernames to searched for
        param:limit the number of usernames to return default=5
        result list,,list
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getMatchingUsernames")

    def getResetPasswordInformation(self, resettoken, **kwargs):
        """
        Retrieve information about a password reset token (if still valid)
        param:resettoken password reset token
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getResetPasswordInformation")

    def isValidInviteUserToken(self, inviteusertoken, emailaddress, **kwargs):
        """
        Check if the inviteusertoken and emailaddress pair are valid and matching
        param:inviteusertoken the token that was previously sent to the invited user email
        param:emailaddress email address for the user
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method isValidInviteUserToken")

    def registerInvitedUser(self, inviteusertoken, emailaddress, username, password, confirmpassword, **kwargs):
        """
        Registers an invited user
        param:inviteusertoken user invitation token
        param:emailaddress email address
        param:username username to be assigned to user
        param:password password
        param:confirmpassword password confirmation
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method registerInvitedUser")

    def resetPassword(self, resettoken, newpassword, **kwargs):
        """
        Resets a password
        param:resettoken password reset token
        param:newpassword new password
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method resetPassword")

    def sendResetPasswordLink(self, emailaddress, **kwargs):
        """
        Sends a reset password link to the supplied email address
        param:emailaddress unique emailaddress for the account
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method sendResetPasswordLink")

    def setData(self, data, **kwargs):
        """
        Set extra user information
        param:data data to set on user
        result True
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method setData")

    def updatePassword(self, oldPassword, newPassword, **kwargs):
        """
        Change user password
        param:oldPassword oldPassword of the user
        param:newPassword newPassword of the user
        result dict,,user
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method updatePassword")

    def validate(self, validationtoken, password, **kwargs):
        """
        Validates user email and sets his password
        param:validationtoken Validation token
        param:password User password
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method validate")
