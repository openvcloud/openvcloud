from js9 import j

class cloudapi_locations(j.tools.code.classGetBase()):
    """
    API Actor api for managing locations
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="locations"
        self.appname="cloudapi"
        #cloudapi_locations_osis.__init__(self)


    def getUrl(self, **kwargs):
        """
        Get the portal url
        result str,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getUrl")

    def list(self, **kwargs):
        """
        List all locations
        result [],
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method list")
