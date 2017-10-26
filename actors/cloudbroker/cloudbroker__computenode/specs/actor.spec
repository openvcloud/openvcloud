[actor] @dbtype:mem,fs
    """
    Operator actions for handling interventsions on a computenode
    """

    method:setStatus
        """
        Set the computenode status, options are 'ENABLED(creation and actions on machines is possible)','DISABLED(Only existing machines are started)', 'HALTED(Machine is not available'
        """
        var:id str,, id of the computenode
        var:locationId str,, the grid this computenode belongs to
        var:status str,, status (ENABLED, MAINTENANCE, DECOMMISSIONED).
        result: str

    method:btrfs_rebalance
        """
        Rebalances the btrfs filesystem
        """
        var:name str,, name of the computenode
        var:locationId str,, the grid this computenode belongs to
        var:mountpoint str,,the mountpoint of the btrfs
        var:uuid str,,if no mountpoint given, uuid is mandatory
        result: bool

    method:enable
        """
        Enable a stack
        """
        var:id str,,id of the computenode
        var:message str,,message. Must be less than 30 characters
        result: str

    method:enableStacks
        """
        Enable stacks
        """
        var:ids list(str),,ids of stacks to enable
        result:bool

    method:list
        """
        List stacks
        """
        var:locationId str,,filter on gid @optional
        result:list

    method:sync
        """
        Sync stacks
        """
        var:locationId str,,the grid id to sync
        result:bool

    method:maintenance
        """
        Migrates or stop all vms
        Set the status to 'MAINTENANCE'
        """
        var:id str,, id of the computenode
        var:vmaction str,, what to do with running vms move or stop
        var:force bool,, force to Stop VM if Life migration fails
        var:message str,,message. Must be less than 30 characters
        result: str


    method:decommission
        """
        Migrates all machines to different computes
        Set the status to 'DECOMMISSIONED'
        """
        var:id str,, id of the computenode
        var:locationId str,, the grid this computenode belongs to
        var:message str,,message. Must be less than 30 characters
        result: str


    method:upgrade
        """
        upgrade node to new version
        Set the status to 'ENABLED'
        """
        var:id str,, id of the computenode
        var:message str,,message. Must be less than 30 characters
        var:force bool,,force. force upgrade
        result: str
