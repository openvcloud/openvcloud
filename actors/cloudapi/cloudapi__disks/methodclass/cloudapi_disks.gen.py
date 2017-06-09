from js9 import j

class cloudapi_disks(j.code.classGetBase()):
    """
    API Actor api, this actor is the final api a enduser uses to manage his resources
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="disks"
        self.appname="cloudapi"
        #cloudapi_disks_osis.__init__(self)


    def create(self, accountId, gid, name, description, iops, size=10, type='B', ssdSize=0, **kwargs):
        """
        Create a disk
        param:accountId id of the account
        param:gid id of the grid
        param:name name of disk
        param:description description of disk
        param:size size in GBytes, default is 0 default=10
        param:type (B;D;T)  B=Boot;D=Data;T=Temp default=B
        param:ssdSize size in GBytes default is 0 default=0
        param:iops max number of IOPS default is 2000
        result int,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method create")

    def delete(self, diskId, detach, **kwargs):
        """
        Delete a disk
        param:diskId id of disk to delete
        param:detach detach disk from machine first
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method delete")

    def get(self, diskId, **kwargs):
        """
        Get disk details
        param:diskId id of the disk
        result dict,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method get")

    def limitIO(self, diskId, iops, **kwargs):
        """
        Limit IO done on a certain disk
        param:diskId Id of the disk to limit
        param:iops Max IO per second, 0 means unlimited
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method limitIO")

    def list(self, accountId, type, **kwargs):
        """
        List the created disks belonging to an account
        param:accountId id of accountId the disks belongs to
        param:type type of the disks
        result list,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method list")
