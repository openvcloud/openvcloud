from . import cloudbroker
from js9 import j


class BaseActor(object):
    def __init__(self):
        self.cb = cloudbroker.CloudBroker()
        self.models = cloudbroker.models
        self.systemodel = j.portal.tools.models.system
        self.config = j.application.instanceconfig.get('cloudbroker', {})
