[actor] @dbtype:mem,osis
    """
    API Actor api for managing VNAS
    """    
    method:createShare
        """
        Create a share
        """
        var:name str,,name of share to create
        var:path str,,path of share
        result:boolean  # returns whether creation was successful

    method:deleteShare
        """
        Delete a share
        """
        var:sharename str,,name of share to create
        var:cloudspace str,,name of cloudpsace
        result:bool, True if deletion whas successfull

    method:listShares
        """
        List shares. 
        """
        var:cloudspace str,,name of cloudpsace
        result:[], A json list of the share names.

    method:addApplication
        """
        Give an application access to a share.
        Access rights can be 'R' or 'W'
        """
        var:appname str,, name of the app
        var:sharename str,, name of the share to give access on
        var:cloudspace str,, name of cloudspace
        var:readonly bool,, True for read only access
        result:bool

    method:removeApplication
        """
        Revoke an applications's access to the share
        """
        var:appname str,, name of the application to revoke
        var:sharename str,, name of share
        var:cloudspace str,, name of cloudspace
        var:readonly bool,, If revoking readonly access or read/write
        result: bool