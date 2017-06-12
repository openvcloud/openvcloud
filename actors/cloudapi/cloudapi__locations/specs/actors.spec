[actor] @dbtype:mem,osis
    """
    API Actor api for managing locations
    """    

    method:list @noauth
        """
        List all locations
        """
        result:[], list with every element containing details of a location as a dict

    method:getUrl @noauth
        """
        Get the portal url
        """
        result:str, portal url
