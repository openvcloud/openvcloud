from js9 import j

class cloudbroker_grid(j.tools.code.classGetBase()):
    """
    Operator actions for handling interventions on a a grid
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="grid"
        self.appname="cloudbroker"
        #cloudbroker_grid_osis.__init__(self)


    def add(self, gid, name, apiUrl, locationcode, **kwargs):
        """
        Adds a location/grid
        param:gid id of the grid
        param:name Name of the location
        param:apiUrl Url of the location to add
        param:locationcode Location code typicly used in dns names
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method add")

    def checkVMs(self, gid, **kwargs):
        """
        Run checkvms jumpscript
        param:gid id of the grid
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method checkVMs")

    def purgeLogs(self, gid, age, **kwargs):
        """
        Remove logs & eco’s
        By default the logs en eco's older than than 1 week but this can be overriden
        param:gid id of the grid
        param:age by default 1 week (-1h, -1w TODO: check the options in the jsgrid purgelogs)
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method purgeLogs")

    def rename(self, gid, name, **kwargs):
        """
        Rename a grid/location
        param:gid id of the grid
        param:name New name of the location
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method rename")
