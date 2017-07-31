from js9 import j

class cloudbroker_location(j.tools.code.classGetBase()):
    """
    Operator actions for handling interventions on a a grid
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="location"
        self.appname="cloudbroker"
        #cloudbroker_location_osis.__init__(self)


    def add(self, name, apiUrl, apiToken, **kwargs):
        """
        Adds a location/grid
        param:name Name of the location
        param:apiUrl Url of the location to add
        param:apiToken Token to authenticate with api
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method add")

    def checkVMs(self, locationId, **kwargs):
        """
        Run checkvms jumpscript
        param:locationId id of the grid
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method checkVMs")

    def delete(self, locationId, **kwargs):
        """
        Delete location
        param:locationId id of the location
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method delete")

    def purgeLogs(self, locationId, age, **kwargs):
        """
        Remove logs & eco’s
        By default the logs en eco's older than than 1 week but this can be overriden
        param:locationId id of the grid
        param:age by default 1 week (-1h, -1w TODO: check the options in the jsgrid purgelogs)
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method purgeLogs")

    def update(self, locationId, name, apiUrl, apiToken, **kwargs):
        """
        Rename a grid/location
        param:locationId id of the location
        param:name New name of the location
        param:apiUrl New API URL
        param:apiToken Token to authenticate with api
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method update")
