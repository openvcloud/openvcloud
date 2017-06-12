[actor] @dbtype:mem,osis
	"""
	User management
	"""

	method:authenticate @noauth
	    """
	    The function evaluates the provided username and password and returns a session key.
	    The session key can be used for doing api requests. E.g this is the authkey parameter in every actor request.
	    A session key is only vallid for a limited time.
	    """

	    var:username str,,username to validate
	    var:password str,,password to validate
	    result:str,,session key.

	method:get
	    """
	    Get information of a existing username based on username id
	    """
        var:username str,,username of the user
        result:dict,,user information.

	method:setData
	    """
	    Set extra user information
	    """
        var:data obj,,data to set on user
        result:True

	method:updatePassword
	    """
	    Change user password
	    """
        var:oldPassword str,,oldPassword of the user
        var:newPassword str,,newPassword of the user
        result:dict,,user information.

    method:sendResetPasswordLink @noauth
	    """
	    Sends a reset password link to the supplied email address
	    """
	    var:emailaddress str,,unique emailaddress for the account
	    result:bool

    method:getResetPasswordInformation @noauth
        """
        Retrieve information about a password reset token (if still valid)
        """
        var:resettoken str,, password reset token
        result:bool

    method:resetPassword @noauth
        """
        Resets a password
        """
        var:resettoken str,, password reset token
        var:newpassword str,, new password
        result:bool

    method:validate @noauth
        """
        Validates user email and sets his password
        """
        var:validationtoken str,, Validation token
        var:password str,, User password
        result:bool

    method:getMatchingUsernames
        """
        Get a list of the matching usernames for a given string
        """
        var:usernameregex str,,regex of the usernames to searched for
        var:limit int,5,the number of usernames to return
        result:list,,list of dicts with the username and url of the gravatar of the user

    method:isValidInviteUserToken @noauth
        """
        Check if the inviteusertoken and emailaddress pair are valid and matching
        """
        var:inviteusertoken str,,the token that was previously sent to the invited user email
        var:emailaddress str,,email address for the user
        result:bool

    method:registerInvitedUser @noauth
        """
        Registers an invited user
        """
        var:inviteusertoken str,, user invitation token
        var:emailaddress str,, email address
        var:username str,, username to be assigned to user
        var:password str,, password
        var:confirmpassword str,, password confirmation
        result:bool
