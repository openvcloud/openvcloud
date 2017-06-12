
[rootmodel:VMachine] @dbtype:osis
    """
    """
    prop:id int,,
    prop:name str,,name as given by customer @index
    prop:descr str,,
    prop:sizeId int,,id of size used by machine, size is the cloudbroker size. @index
    prop:imageId str,,id of image used to create machine @index
    prop:dedicatedCU bool,False,if true the compute capacity will be dedicated
    prop:disks list(int),,List of id of Disk objects
    prop:nics list(Nic),,List of id Nic objects (network interfaces) attached to this vmachine
    prop:referenceId str,,name as used in hypervisor @index
    prop:accounts list(VMAccount),,list of machine accounts on the virtual machine
    prop:status str,,status of the vm (HALTED;INIT;RUNNING;TODELETE;SNAPSHOT;EXPORT;DESTROYED) @index
    prop:hostName str,,hostname of the machine as specified by OS; is name in case no hostname is provided @index
    prop:cpus int,1,number of cpu assigned to the vm
    prop:boot bool,True,indicates if the virtual machine must automatically start upon boot of host machine
    prop:hypervisorType str,VMWARE,hypervisor running this vmachine (VMWARE;HYPERV;KVM)
    prop:stackId str,,ID of the stack
    prop:acl list(ACE),,access control list @index
    prop:cloudspaceId str,,id of space which holds this vmachine @index
    prop:networkGatewayIPv4 str,,IP address of the gateway for this vmachine
    prop:referenceSizeId str,, reference to the size used on the stack
    prop:cloneReference int,, id to the machine on which this machine is based
    prop:clone int,, id of the clone
    prop:creationTime int,, epoch time of creation, in seconds @index
    prop:updateTime int,, epoch time of update, in seconds @index
    prop:deletionTime int,, epoch time of destruction, in seconds @index
    prop:type str,,Type of machine @index
    prop:tags str,, A tags string @index

[model:VMAccount] @dbtype:osis
    """
    Machine account on the virtual machine
    """
    prop:login str,,login name of the machine account
    prop:password str,,password of the machine account

[rootmodel:Disk] @dbtype:osis
    """
    """
    prop:id int,,
    prop:name str,,name as given by customer
    prop:descr str,,
    prop:sizeMax int,,provisioned size of disk in MB @index
    prop:sizeUsed int,,used capacity of disk in MB
    prop:referenceId str,,name as used in hypervisor @index
    prop:realityDeviceNumber int,, Number a device gets after connect
    prop:status str,,status of the vm (ACTIVE;INIT;IMAGE) @index
    prop:type str,,(RAW,ISCSI)
    prop:locationId str,,ID of the grid @index
    prop:iops int,,Limited IOPS
    prop:accountId str,,ID of the account @index
    prop:acl dict(ACE),,access control list
    prop:role str,,role of disk (BOOT; DATA; TEMP) @index
    prop:order int,,order of the disk (as will be shown in OS)
    prop:iqn str,,location of iscsi backend e.g. iqn.2009-11.com.aserver:b6d2aa75-d5ae-4e5a-a38a-12c64c787be6
    prop:diskPath str,, Holds the path of the disk
    prop:login str,,login of e.g. iqn connection
    prop:passwd str,,passwd of e.g. iqn connection
    prop:params str,,pylabs tags to define optional params
    prop:bootPartition int,,the partition to boot from if disk is a bootdisk
    prop:images list(int),,List of id of Image object
    prop:snapshots list(Snapshot),,List of snapshots for disk
