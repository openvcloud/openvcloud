[actor] @dbtype:mem,osis
    """
    Lists all the images. A image is a template which can be used to deploy machines.
    """
    method:list
        """
        List the availabe images, filtering can be based on the user which is doing the request
        """
        var:accountId str,, optional account id to include account images @tags: optional
        var:cloudspaceId str,, optional cloudpsace id to filer @tags: optional
        result: list


    method:delete
        """
        Delete an image
        """
        var:imageId str,, id of the image to delete
        result:bool, True if image was deleted successfully

