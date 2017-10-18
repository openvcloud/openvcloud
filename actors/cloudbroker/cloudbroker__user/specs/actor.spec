[actor] @dbtype:mem,fs
    """
    Operator actions for interventions specific to a user
    """
    method:generateAuthorizationKey
        """
        Generates a valid authorizationkey in the context of a specific user.
        This key can be used in a webbrowser to browse the cloud portal from the perspective of that specific user or to use the api in his/her authorization context
        """
        var:username str,,name of the user an authorization key is required for

    method:sendResetPasswordLink
        """
        send reset password of user to their email address
        """
        var:username str,, id of user
        result:bool

    method:delete
        """
        Delete a user
        """
        var:username str,, id of user
        result:bool

    method:deleteUsers
        """
        Bulk delete a list of users
        """
        var:userIds list(id),, List of user ids
        result:bool

    method:deleteByGuid
        """
        Delete a user using the user guid
        Note: This actor can also be called using username instead of guid to workaround CBGrid
        allowing userguid or username
        """
        var:userguid str,, guid of user
        result:bool

    method:create
        """
        Create a user
        """
        var:username str,, id of user @tags validator:username
        var:emailaddress list,, emailaddresses of the user
        var:password str,, password of user
        var:groups list,,list of groups this user belongs to @optional default_is_none
        result:bool
