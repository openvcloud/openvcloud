from js9 import j

class cloudapi_externalnetwork(j.tools.code.classGetBase()):
    """
    List Existing extenal networks
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="externalnetwork"
        self.appname="cloudapi"
        #cloudapi_externalnetwork_osis.__init__(self)


    def list(self, accountId, **kwargs):
        """
        param:accountId optional account id to include account specific externalnetwork
        result [externalnetwork]
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method list")
