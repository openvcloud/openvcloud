from JumpScale9Portal.data.models.BaseModelFactory import NameSpaceLoader
from . import models


class Models(NameSpaceLoader):

    def __init__(self):
        self.__imports__ = "mongoengine"
        super().__init__(models)
