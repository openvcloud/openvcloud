[actor] @dbtype:mem,osis
    """
    API Actor api, this actor is the final api a enduser uses to manage his resources
    """

    method:list
        """
        List the created disks belonging to an account
        """
        var:accountId str,,id of accountId the disks belongs to
        var:type str,,type of the disks @tags: optional
        result:list, list with every element containing details of a disk as a dict

    method:get
        """
        Get disk details
        """
        var:diskId str,, id of the disk
        result:dict, dict with the disk details


    method:limitIO
        """
        Limit IO done on a certain disk
        """
        var:diskId str,, Id of the disk to limit
        var:iops int,, Max IO per second, 0 means unlimited
        result:bool

    method:delete
        """
        Delete a disk
        """
        var:diskId str,, id of disk to delete
        var:detach bool,,detach disk from machine first @optional
        result: bool, True if disk was deleted successfully

    method:create
        """
        Create a disk
        """
        var:accountId str,,id of the account
        var:locationId str,,id of the grid
        var:name str,,name of disk
        var:description str,,description of disk
        var:size int,10,size in GBytes, default is 0
        var:type str,B, (B;D;T)  B=Boot;D=Data;T=Temp
        var:ssdSize int,0,size in GBytes default is 0 @optional
        var:iops int,,max number of IOPS default is 2000 @optional
        result:int, the id of the created disk
