from mongoengine import fields
from mongoengine import EmbeddedDocument, Document
from js9 import j
from JumpScale9Portal.data.models.Models import Base, Errorcondition

DB = 'openvcloud'

default_meta = {'abstract': True, "db_alias": DB}


class ModelBase(Base):
    meta = default_meta

    def to_dict(self):
        d = j.data.serializer.json.loads(Document.to_json(self))
        d.pop("_cls", None)
        d.pop("_id", None)
        d['id'] = str(self.id)
        return d


class ACE(EmbeddedDocument):
    userGroupId = fields.StringField(required=True)
    type = fields.StringField(choices=['U', 'G'])
    right = fields.StringField()
    status = fields.StringField()


class Account(ModelBase):
    name = fields.StringField(required=True)
    acl = fields.EmbeddedDocumentListField(ACE)
    status = fields.StringField(choices=['CONFIRMED', 'UNCONFIRMED', 'DISABLED'], rquired=True)
    updateTime = fields.IntField()
    resourceLimits = fields.DictField()
    sendAccessEmails = fields.BooleanField(default=True)
    creationTime = fields.IntField(default=j.data.time.getTimeEpoch)


class VMAccount(EmbeddedDocument):
    login = fields.StringField()
    password = fields.StringField()


class Image(ModelBase):
    name = fields.StringField(required=True)
    description = fields.StringField()
    size = fields.IntField(required=True)
    type = fields.StringField(required=True)
    referenceId = fields.StringField(required=True)
    status = fields.StringField(choices=['DISABLED', 'ENABLED', 'CREATING', 'DELETING'])
    account = fields.ReferenceField(Account)
    acl = fields.EmbeddedDocumentListField(ACE)
    username = fields.StringField()
    password = fields.StringField()


class Location(ModelBase):
    name = fields.StringField(required=True)
    apiUrl = fields.StringField()


class Stack(ModelBase):
    name = fields.StringField(required=True)
    description = fields.StringField()
    type = fields.StringField()
    images = fields.ListField(fields.ReferenceField(Image))
    referenceId = fields.StringField(rquired=True)
    error = fields.IntField()
    eco = fields.ReferenceField(Errorcondition)
    status = fields.StringField(choices=['DISABLED', 'ENABLED', 'ERROR', 'MAINTENANCE'])
    location = fields.ReferenceField(Location)


class Snapshot(EmbeddedDocument):
    label = fields.StringField(required=True)
    timestamp = fields.IntField()


class ExternalNetwork(ModelBase):
    name = fields.StringField(required=True)
    network = fields.StringField(required=True)
    subnetmask = fields.StringField()
    gateway = fields.StringField(required=True)
    vlan = fields.IntField(required=True)
    account = fields.ReferenceField(Account)
    ips = fields.ListField(fields.StringField())
    location = fields.ReferenceField(Location)


class Size(ModelBase):
    name = fields.StringField()
    memory = fields.IntField()
    vcpus = fields.IntField()
    description = fields.StringField()
    locations = fields.ListField(fields.ReferenceField(Location))
    disks = fields.ListField(fields.IntField())


class VNC(ModelBase):
    url = fields.StringField()


class ForwardRule(EmbeddedDocument):
    fromAddr = fields.StringField()
    fromPort = fields.IntField()
    toAddr = fields.StringField()
    toPort = fields.IntField()
    protocol = fields.StringField(choices=['tcp', 'udp'])


class NetworkIds(ModelBase):
    freeNetworkIds = fields.ListField(fields.IntField())
    usedNetworkIds = fields.ListField(fields.IntField())
    location = fields.ReferenceField(Location)


class Cloudspace(ModelBase):
    name = fields.StringField(required=True)
    description = fields.StringField()
    acl = fields.EmbeddedDocumentListField(ACE)
    account = fields.ReferenceField(Account)
    resourceLimits = fields.DictField()
    networkId = fields.IntField()
    networkcidr = fields.StringField()
    externalnetworkip = fields.StringField()
    externalnetwork = fields.ReferenceField(ExternalNetwork)
    forwardRules = fields.EmbeddedDocumentListField(ForwardRule)
    allowedVMSizes = fields.ListField(fields.IntField())
    status = fields.StringField(choices=['VIRTUAL', 'DEPLOYED', 'DESTROYED'])
    location = fields.ReferenceField(Location)
    creationTime = fields.IntField(default=j.data.time.getTimeEpoch)
    updateTime = fields.IntField(default=j.data.time.getTimeEpoch)
    deletionTime = fields.IntField()
    stack = fields.ReferenceField(Stack)


class Nic(EmbeddedDocument):
    networkId = fields.IntField()
    status = fields.StringField(choices=['ACTIVE', 'INIT', 'DOWN'])
    deviceName = fields.StringField()
    macAddress = fields.StringField()
    ipAddress = fields.StringField()
    type = fields.StringField()
    param = fields.StringField()


class Disk(ModelBase):
    name = fields.StringField()
    description = fields.StringField()
    size = fields.IntField()
    referenceId = fields.StringField()
    iops = fields.IntField()
    account = fields.ReferenceField(Account)
    acl = fields.EmbeddedDocumentListField(ACE)
    role = fields.StringField(choices=['BOOT', 'DB', 'CACHE'])
    diskPath = fields.StringField()
    snapshots = fields.EmbeddedDocumentListField(Snapshot)


class VMachine(ModelBase):
    name = fields.StringField(required=True)
    description = fields.StringField()
    size = fields.ReferenceField(Size)
    image = fields.ReferenceField(Image)
    disks = fields.ListField(fields.ReferenceField(Disk))
    nics = fields.EmbeddedDocumentListField(Nic)
    referenceId = fields.StringField()
    accounts = fields.EmbeddedDocumentListField(VMAccount)
    status = fields.StringField(choices=['HALTED', 'INIT', 'RUNNING', 'PAUSED', 'DESTROYED'])
    hostName = fields.StringField()
    cpus = fields.IntField()
    stack = fields.ReferenceField(Stack)
    acl = fields.EmbeddedDocumentListField(ACE)
    cloudspace = fields.ReferenceField(Cloudspace)
    updateTime = fields.IntField()
    deletionTime = fields.IntField()
    tags = fields.StringField()


del Base
del ModelBase
del EmbeddedDocument
