from js9 import j

class cloudapi_images(j.tools.code.classGetBase()):
    """
    Lists all the images. A image is a template which can be used to deploy machines.
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="images"
        self.appname="cloudapi"
        #cloudapi_images_osis.__init__(self)


    def delete(self, imageId, **kwargs):
        """
        Delete an image
        param:imageId id of the image to delete
        result bool,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method delete")

    def list(self, accountId, cloudspaceId, **kwargs):
        """
        List the availabe images, filtering can be based on the user which is doing the request
        param:accountId optional account id to include account images
        param:cloudspaceId optional cloudpsace id to filer
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method list")
