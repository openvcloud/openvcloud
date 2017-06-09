from js9 import j

class cloudbroker_health(j.code.classGetBase()):
    """
    API Check status of grid
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="health"
        self.appname="cloudbroker"
        #cloudbroker_health_osis.__init__(self)


    def status(self, **kwargs):
        """
        check status of grid
        result dict
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method status")
