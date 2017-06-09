from js9 import j

class cloudapi_sizes(j.code.classGetBase()):
    """
    Lists all the configured flavors available.
    A flavor is a combination of amount of compute capacity(CU) and disk capacity(GB).
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="sizes"
        self.appname="cloudapi"
        #cloudapi_sizes_osis.__init__(self)


    def list(self, cloudspaceId, **kwargs):
        """
        List the available flavors, filtering can be based on the user which is doing the request
        param:cloudspaceId id of the cloudspace
        result list,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method list")
