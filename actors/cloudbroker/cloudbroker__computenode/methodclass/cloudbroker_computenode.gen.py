from js9 import j

class cloudbroker_computenode(j.tools.code.classGetBase()):
    """
    Operator actions for handling interventsions on a computenode
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="computenode"
        self.appname="cloudbroker"
        #cloudbroker_computenode_osis.__init__(self)


    def btrfs_rebalance(self, name, gid, mountpoint, uuid, **kwargs):
        """
        Rebalances the btrfs filesystem
        param:name name of the computenode
        param:gid the grid this computenode belongs to
        param:mountpoint the mountpoint of the btrfs
        param:uuid if no mountpoint given, uuid is mandatory
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method btrfs_rebalance")

    def decommission(self, id, gid, message, **kwargs):
        """
        Migrates all machines to different computes
        Set the status to 'DECOMMISSIONED'
        param:id id of the computenode
        param:gid the grid this computenode belongs to
        param:message message. Must be less than 30 characters
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method decommission")

    def enable(self, id, gid, message, **kwargs):
        """
        Enable a stack
        param:id id of the computenode
        param:gid the grid this computenode belongs to
        param:message message. Must be less than 30 characters
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method enable")

    def enableStacks(self, ids, **kwargs):
        """
        Enable stacks
        param:ids ids of stacks to enable
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method enableStacks")

    def list(self, gid, **kwargs):
        """
        List stacks
        param:gid filter on gid
        result list
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method list")

    def maintenance(self, id, gid, vmaction, message, **kwargs):
        """
        Migrates or stop all vms
        Set the status to 'MAINTENANCE'
        param:id id of the computenode
        param:gid the grid this computenode belongs to
        param:vmaction what to do with running vms move or stop
        param:message message. Must be less than 30 characters
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method maintenance")

    def setStatus(self, id, gid, status, **kwargs):
        """
        Set the computenode status, options are 'ENABLED(creation and actions on machines is possible)','DISABLED(Only existing machines are started)', 'HALTED(Machine is not available'
        param:id id of the computenode
        param:gid the grid this computenode belongs to
        param:status status (ENABLED, MAINTENANCE, DECOMMISSIONED).
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method setStatus")

    def sync(self, gid, **kwargs):
        """
        Sync stacks
        param:gid the grid id to sync
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method sync")
