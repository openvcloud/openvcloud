from js9 import j

class cloudbroker_diagnostics(j.code.classGetBase()):
    """
    Operator actions to perform specific diagnostic checks on the platform
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="diagnostics"
        self.appname="cloudbroker"
        #cloudbroker_diagnostics_osis.__init__(self)


    def checkVms(self, **kwargs):
        """
        Starts the vms check jumpscipt to do a ping to every VM from their virtual firewalls
        result boolean
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method checkVms")
