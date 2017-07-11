from JumpScale9Portal.data.models.BaseModelFactory import NameSpaceLoader
from . import models


class Models(NameSpaceLoader):

    def __init__(self):
        self.__imports__ = "mongoengine"
        super().__init__(models)
        self.VMachine = models.VMachine
        self.Account = models.Account
        self.Location = models.Location
        self.Disk = models.Disk
        self.Stack = models.Stack
        self.Cloudspace = models.Cloudspace
        self.Image = models.Image
