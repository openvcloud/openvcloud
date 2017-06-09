from js9 import j

class cloudapi_machines(j.code.classGetBase()):
    """
    API Actor api, this actor is the final api a enduser uses to manage his resources
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="machines"
        self.appname="cloudapi"
        #cloudapi_machines_osis.__init__(self)


    def addDisk(self, machineId, diskName, description, iops, size=10, type='B', ssdSize=0, **kwargs):
        """
        Create and attach a disk to the machine
        param:machineId id of the machine
        param:diskName name of disk
        param:description optional description
        param:size size in GByte default=10
        param:type (B;D;T) B=Boot;D=Data;T=Temp default=B
        param:ssdSize size in GBytes default is 0 default=0
        param:iops max number of IOPS default is 2000
        result int,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method addDisk")

    def addUser(self, machineId, userId, accesstype, **kwargs):
        """
        Give a registered user access rights
        param:machineId id of the machine
        param:userId username or emailaddress of the user to grant access
        param:accesstype 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        result bool,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method addUser")

    def attachDisk(self, machineId, diskId, **kwargs):
        """
        Attach a disk to the machine
        param:machineId id of the machine
        param:diskId id of disk to attach
        result bool,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method attachDisk")

    def attachExternalNetwork(self, machineId, **kwargs):
        """
        Attach a public network to the machine
        param:machineId id of the machine
        result bool,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method attachExternalNetwork")

    def clone(self, machineId, name, cloudspaceId, snapshotTimestamp, **kwargs):
        """
        Clone the machine
        param:machineId id of the machine to clone
        param:name name of the cloned machine
        param:cloudspaceId optional id of the cloudspace in which the machine should be put
        param:snapshotTimestamp optional snapshot to base the clone upon
        result int,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method clone")

    def convertToTemplate(self, machineId, templatename, **kwargs):
        """
        Convert a machine to a template
        param:machineId id of the machine
        param:templatename name of the template
        result bool,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method convertToTemplate")

    def create(self, cloudspaceId, name, description, sizeId, imageId, disksize, datadisks, **kwargs):
        """
        Create a machine based on the available sizes, in a certain cloud space
        The user needs write access rights on the cloud space
        param:cloudspaceId id of cloud space in which we want to create a machine
        param:name name of machine
        param:description optional description
        param:sizeId id of the specific size
        param:imageId id of the specific image
        param:disksize size of base volume
        param:datadisks list of extra data disks in gigabytes
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method create")

    def delete(self, machineId, **kwargs):
        """
        Delete a machine
        param:machineId id of the machine
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method delete")

    def deleteSnapshot(self, machineId, epoch, **kwargs):
        """
        Delete a snapshot of the machine
        param:machineId id of the machine
        param:epoch epoch time of snapshot
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method deleteSnapshot")

    def deleteUser(self, machineId, userId, **kwargs):
        """
        Revoke user access from the vmachine
        param:machineId id of the machine
        param:userId id or emailaddress of the user to remove
        result bool,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method deleteUser")

    def detachDisk(self, machineId, diskId, **kwargs):
        """
        Detach a disk from the machine
        param:machineId id of the machine
        param:diskId id of disk to detach
        result bool,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method detachDisk")

    def detachExternalNetwork(self, machineId, **kwargs):
        """
        Detach the public network from the machine
        param:machineId id of the machine
        result bool,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method detachExternalNetwork")

    def exportOVF(self, link, username, passwd, path, machineId, callbackUrl, **kwargs):
        """
        Export a machine with it's disks to owncloud(ovf)
        param:link WebDav link to owncloud
        param:username WebDav Username
        param:passwd WebDav Password
        param:path Path to ovf file in WebDav share
        param:machineId id of the machine to export
        param:callbackUrl callback url so that the API caller can be notified. If this is specified the G8 will not send an email itself upon completion.
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method exportOVF")

    def get(self, machineId, **kwargs):
        """
        Get information from a certain object.
        This contains all information about the machine.
        param:machineId id of machine
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method get")

    def getConsoleUrl(self, machineId, **kwargs):
        """
        Get url to connect to console
        param:machineId id of the machine to connect to the console
        result str,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getConsoleUrl")

    def getHistory(self, machineId, size, **kwargs):
        """
        Get machine history
        param:machineId id of the machine
        param:size number of entries to return
        result list,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getHistory")

    def importOVF(self, link, username, passwd, path, cloudspaceId, name, description, sizeId, callbackUrl, **kwargs):
        """
        Import a machine from owncloud(ovf)
        param:link WebDav link to owncloud
        param:username WebDav Username
        param:passwd WebDav Password
        param:path Path to ovf file in WebDav share
        param:cloudspaceId id of the cloudspace in which the vm should be created
        param:name name of machine
        param:description optional description
        param:sizeId the size id of the machine
        param:callbackUrl callback url so that the API caller can be notified. If this is specified the G8 will not send an email itself upon completion.
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method importOVF")

    def list(self, cloudspaceId, **kwargs):
        """
        List the deployed machines in a space. Filtering based on status is possible
        param:cloudspaceId id of cloud space in which machine exists
        result list
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method list")

    def listSnapshots(self, machineId, **kwargs):
        """
        List the snapshots of the machine
        param:machineId id of the machine
        result list,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method listSnapshots")

    def pause(self, machineId, **kwargs):
        """
        Pause the machine
        param:machineId id of the machine
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method pause")

    def reboot(self, machineId, **kwargs):
        """
        Reboot the machine
        param:machineId id of the machine
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method reboot")

    def reset(self, machineId, **kwargs):
        """
        Reset the machine, force reboot
        param:machineId id of the machine
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method reset")

    def resize(self, machineId, sizeId, **kwargs):
        """
        Change the size of a machine
        param:machineId id of machine to resize
        param:sizeId new sizeId
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method resize")

    def resume(self, machineId, **kwargs):
        """
        Resume the machine
        param:machineId id of the machine
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method resume")

    def rollbackSnapshot(self, machineId, epoch, **kwargs):
        """
        Rollback a snapshot of the machine
        param:machineId id of the machine
        param:epoch epoch time of snapshot
        result str
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method rollbackSnapshot")

    def snapshot(self, machineId, name, **kwargs):
        """
        Take a snapshot of the machine
        param:machineId id of machine to snapshot
        param:name name to give snapshot
        result str
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method snapshot")

    def start(self, machineId, **kwargs):
        """
        Start the machine
        param:machineId id of the machine
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method start")

    def stop(self, machineId, force=False, **kwargs):
        """
        Stop the machine
        param:machineId id of the machine
        param:force force machine shutdown default=False
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method stop")

    def update(self, machineId, name, description, **kwargs):
        """
        Change basic properties of a machine
        Name, description can be changed with this action.
        param:machineId id of the machine
        param:name name of the machine
        param:description description of the machine
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method update")

    def updateUser(self, machineId, userId, accesstype, **kwargs):
        """
        Update user access rights. Returns True only if an actual update has happened.
        param:machineId id of the machineId
        param:userId userid/email for registered users or emailaddress for unregistered users
        param:accesstype 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        result bool,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method updateUser")
