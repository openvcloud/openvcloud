from js9 import j

class cloudbroker_image(j.code.classGetBase()):
    """
    image manager
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="image"
        self.appname="cloudbroker"
        #cloudbroker_image_osis.__init__(self)


    def delete(self, imageId, **kwargs):
        """
        delete image
        param:imageId id of image to be deleted
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method delete")

    def disable(self, imageId, **kwargs):
        """
        disable image
        param:imageId id of image to be disabled
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method disable")

    def enable(self, imageId, **kwargs):
        """
        enable image
        param:imageId id of image to be enabled
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method enable")

    def rename(self, imageId, name, **kwargs):
        """
        rename image
        param:imageId id of image to be enabled
        param:name new name of image
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method rename")

    def updateNodes(self, imageId, enabledStacks, **kwargs):
        """
        Update which nodes have this image available
        param:imageId id of image
        param:enabledStacks list of enabled stacks
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method updateNodes")
