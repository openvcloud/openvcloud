from mongoengine import fields
from mongoengine import EmbeddedDocument
from js9 import j
import json
from JumpScale9Portal.data.models.Models import Base, Errorcondition

DB = 'openvcloud'

default_meta = {'abstract': True, "db_alias": DB}


def list_dereference(listobj):
    for idx, value in enumerate(listobj):
        if isinstance(value, dict):
            if '$oid' in value:
                listobj[idx] = value['$oid']
            else:
                dict_derefence(value)
        elif isinstance(value, list):
            list_dereference(value)


def dict_derefence(obj):
    for key, value in obj.items():
        if isinstance(value, dict):
            if '$oid' in value:
                obj['{}Id'.format(key)] = value['$oid']
                obj.pop(key)
            else:
                dict_derefence(value)
        elif isinstance(value, list):
            list_dereference(value)


def to_dict(document):
    d = j.data.serializer.json.loads(document.to_json())
    d.pop("_cls", None)
    objid = d.pop("_id", None)
    if objid:
        d['id'] = str(document.id)
    dict_derefence(d)
    return d


def to_python(obj):
    if isinstance(obj, list):
        results = []
        for item in obj:
            results.append(to_dict(item))
        return results
    else:
        return to_dict(obj)


class ModelBase(Base):
    meta = default_meta

    def to_dict(self):
        return to_dict(self)


class ACE(EmbeddedDocument):
    userGroupId = fields.StringField(required=True)
    type = fields.StringField(choices=['U', 'G'])
    right = fields.StringField()
    status = fields.StringField()

    def to_dict(self):
        data = json.loads(self.to_json())
        data.pop('_cls', None)
        return data


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
    disks = fields.ListField(fields.IntField())
    username = fields.StringField()
    password = fields.StringField()


class Location(ModelBase):
    name = fields.StringField(required=True)
    apiUrl = fields.StringField()
    apiToken = fields.StringField()


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
    location = fields.ReferenceField(Location)
    acl = fields.EmbeddedDocumentListField(ACE)
    type = fields.StringField(choices=['BOOT', 'DB', 'CACHE'])
    diskPath = fields.StringField()
    snapshots = fields.EmbeddedDocumentListField(Snapshot)


class Macaddress(ModelBase):
    count = fields.IntField(default=0)
    location = fields.ReferenceField(Location, required=True)


class VMachine(ModelBase):
    name = fields.StringField(required=True)
    description = fields.StringField()
    size = fields.ReferenceField(Size)
    image = fields.ReferenceField(Image)
    disks = fields.ListField(fields.ReferenceField(Disk))
    nics = fields.EmbeddedDocumentListField(Nic)
    referenceId = fields.StringField()
    accounts = fields.EmbeddedDocumentListField(VMAccount)
    status = fields.StringField(choices=['HALTED', 'INIT', 'RUNNING', 'STARTING', 'PAUSED', 'DESTROYED'])
    type = fields.StringField()
    hostName = fields.StringField()
    cpus = fields.IntField()
    stack = fields.ReferenceField(Stack)
    acl = fields.EmbeddedDocumentListField(ACE)
    cloudspace = fields.ReferenceField(Cloudspace)
    creationTime = fields.IntField(default=j.data.time.getTimeEpoch)
    updateTime = fields.IntField(default=j.data.time.getTimeEpoch)
    deletionTime = fields.IntField()
    tags = fields.StringField()


del Base
del ModelBase
del EmbeddedDocument
