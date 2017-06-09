from js9 import j

class cloudbroker_ovsnode(j.code.classGetBase()):
    """
    Operator actions for interventions on accounts
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="ovsnode"
        self.appname="cloudbroker"
        #cloudbroker_ovsnode_osis.__init__(self)


    def decommissionNode(self, nid, **kwargs):
        """
        put a storage driver in decommition node.
        param:nid nid of storage node down
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method decommissionNode")
