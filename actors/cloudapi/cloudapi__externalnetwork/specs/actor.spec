[actor] @dbtype:mem,redis,fs
    """
    List Existing extenal networks
    """
    method:list
        """
        """
        var:accountId str,, optional account id to include account specific externalnetwork @tags: optional
        result:[externalnetwork]
