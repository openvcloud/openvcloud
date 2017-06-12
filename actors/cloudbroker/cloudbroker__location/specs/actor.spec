[actor] @dbtype:mem,fs
    """
    Operator actions for handling interventions on a a grid
    """

    method:purgeLogs
        """
        Remove logs & eco’s
        By default the logs en eco's older than than 1 week but this can be overriden
        """
        var:locationId str,, id of the grid
        var:age str,, by default 1 week (-1h, -1w TODO: check the options in the jsgrid purgelogs)
        result: bool

    method:checkVMs
        """
        Run checkvms jumpscript
        """
        var:locationId str,, id of the grid
        result: bool

    method:update
        """
        Rename a grid/location
        """
        var:loacationId str,, id of the location
        var:name str,, New name of the location @validator:name
        var:apiUrl str,,New API URL
        result: bool

    method:add
        """
        Adds a location/grid
        """
        var:name str,, Name of the location @validator:name
        var:apiUrl str,, Url of the location to add
        result: str
