from js9 import j

class cloudbroker_machine(j.tools.code.classGetBase()):
    """
    machine manager
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="machine"
        self.appname="cloudbroker"
        #cloudbroker_machine_osis.__init__(self)


    def addDisk(self, machineId, diskName, description, size, iops, **kwargs):
        """
        Adds a disk to a deployed machine
        param:machineId ID of machine
        param:diskName Name of the disk
        param:description Description
        param:size size in GByte default=10
        param:iops max number of IOPS default=2000
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method addDisk")

    def addUser(self, machineId, username, accesstype, **kwargs):
        """
        Give a user access rights.
        param:machineId Id of the machine
        param:username name of the user to be given rights
        param:accesstype 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method addUser")

    def attachExternalNetwork(self, machineId, **kwargs):
        """
        Connect VM to external network of the cloudspace
        param:machineId ID of machine
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method attachExternalNetwork")

    def clone(self, machineId, cloneName, reason, **kwargs):
        """
        Clones a machine
        param:machineId Machine id
        param:cloneName Clone name
        param:reason Reason
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method clone")

    def convertToTemplate(self, machineId, templateName, reason, **kwargs):
        """
        Convert a machien to template
        param:machineId ID of machine
        param:templateName Name of the template
        param:reason Reason
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method convertToTemplate")

    def createOnStack(self, cloudspaceId, name, description, sizeId, imageId, disksize, stackId, datadisks, **kwargs):
        """
        Create a machine on a specific stackid
        param:cloudspaceId id of space in which we want to create a machine
        param:name name of machine
        param:description optional description
        param:sizeId id of the specific size
        param:imageId id of the specific image
        param:disksize size of base volume
        param:stackId id of the stack
        param:datadisks list of data disk sizes in gigabytes
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method createOnStack")

    def createPortForward(self, machineId, localPort, destPort, proto, **kwargs):
        """
        Creates a port forwarding rule for a machine
        param:machineId ID of machine
        param:localPort Source port
        param:destPort Destination port
        param:proto Protocol
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method createPortForward")

    def deleteDisk(self, machineId, diskId, **kwargs):
        """
        Deletes a disk from a deployed machine
        param:machineId ID of machine
        param:diskId ID of disk
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method deleteDisk")

    def deletePortForward(self, machineId, publicIp, publicPort, proto, **kwargs):
        """
        Deletes a port forwarding rule for a machine
        param:machineId ID of machine
        param:publicIp Portforwarding public ip
        param:publicPort Portforwarding public port
        param:proto Portforwarding protocol
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method deletePortForward")

    def deleteSnapshot(self, machineId, epoch, reason, **kwargs):
        """
        Deletes a machine snapshot
        param:machineId Machine id
        param:epoch Snapshot timestamp
        param:reason Reason
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method deleteSnapshot")

    def deleteUser(self, machineId, username, **kwargs):
        """
        Delete user from account.
        param:machineId Id of the machine
        param:username name of the user to be removed
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method deleteUser")

    def destroy(self, machineId, reason, **kwargs):
        """
        Destroys a machine
        param:machineId Machine id
        param:reason Reason
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method destroy")

    def destroyMachines(self, machineIds, reason, **kwargs):
        """
        Destroys machines
        param:machineIds Machine ids
        param:reason Reason
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method destroyMachines")

    def detachExternalNetwork(self, machineId, **kwargs):
        """
        Detach VM from external network of the cloudspace
        param:machineId ID of machine
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method detachExternalNetwork")

    def get(self, machineId, **kwargs):
        """
        gets machine json object.
        param:machineId ID of machine
        result json
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method get")

    def getConsoleInfo(self, token, **kwargs):
        """
        Get Console info for machine
        param:token token to get consoleinfo for
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getConsoleInfo")

    def getHistory(self, machineId, **kwargs):
        """
        get history of a machine
        param:machineId ID of machine
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getHistory")

    def list(self, tag, computeNode, cloudspaceId, **kwargs):
        """
        List the undestroyed machines based on specific criteria
        At least one of the criteria needs to be passed
        param:tag a specific tag
        param:computeNode name of a specific computenode
        param:cloudspaceId specific cloudspace
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method list")

    def listPortForwards(self, machineId, result, **kwargs):
        """
        portforwarding of a machine
        param:machineId ID of machine
        param:result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method listPortForwards")

    def listSnapshots(self, machineId, **kwargs):
        """
        list snapshots of a machine
        param:machineId ID of machine
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method listSnapshots")

    def moveToDifferentComputeNode(self, machineId, reason, targetstackId, force, **kwargs):
        """
        Live-migrates a machine to a different CPU node.
        If no targetnode is given, the normal capacity scheduling is used to determine a targetnode
        param:machineId Machine id
        param:reason Reason
        param:targetstackId Name of the compute node the machine has to be moved to
        param:force force move of machine even if storage is busy
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method moveToDifferentComputeNode")

    def pause(self, machineId, reason, **kwargs):
        """
        Pauses a deployed machine
        param:machineId Machine id
        param:reason Reason
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method pause")

    def reboot(self, machineId, reason, **kwargs):
        """
        Reboots a deployed machine
        param:machineId Machine id
        param:reason Reason
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method reboot")

    def rebootMachines(self, machineIds, reason, **kwargs):
        """
        Reboots running machines
        param:machineIds Machine ids
        param:reason Reason
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method rebootMachines")

    def resize(self, machineId, sizeId, **kwargs):
        """
        Change memory and vcpu from machine
        param:machineId ID of machine
        param:sizeId new sizeId
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method resize")

    def resume(self, machineId, reason, **kwargs):
        """
        Resumes a deployed paused machine
        param:machineId Machine id
        param:reason Reason
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method resume")

    def rollbackSnapshot(self, machineId, epoch, reason, **kwargs):
        """
        Rolls back a machine snapshot
        param:machineId Machine id
        param:epoch Snapshot timestamp
        param:reason Reason
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method rollbackSnapshot")

    def snapshot(self, machineId, snapshotName, reason, **kwargs):
        """
        Takes a snapshot of a deployed machine
        param:machineId Machine id
        param:snapshotName Snapshot name
        param:reason Reason
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method snapshot")

    def start(self, machineId, reason, **kwargs):
        """
        Starts a deployed machine
        param:machineId Machine id
        param:reason Reason
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method start")

    def startMachines(self, machineIds, reason, **kwargs):
        """
        Starts a deployed machines
        param:machineIds Machine ids
        param:reason Reason
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method startMachines")

    def stop(self, machineId, reason, **kwargs):
        """
        Stops a machine
        param:machineId Machine id
        param:reason Reason
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method stop")

    def stopMachines(self, machineIds, reason, **kwargs):
        """
        Stops the running machines
        param:machineIds Machine ids
        param:reason Reason
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method stopMachines")

    def tag(self, machineId, tagName, **kwargs):
        """
        Adds a tag to a machine, useful for indexing and following a (set of) machines
        param:machineId id of the machine to tag
        param:tagName tag
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method tag")

    def untag(self, machineId, tagName, **kwargs):
        """
        Removes a specific tag from a machine
        param:machineId id of the machine to untag
        param:tagName tag
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method untag")

    def updateMachine(self, machineId, name, description, reason, **kwargs):
        """
        Updates machine description
        param:machineId ID of machine
        param:name new name
        param:description new description
        param:reason Reason
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method updateMachine")
