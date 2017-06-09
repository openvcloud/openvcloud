from js9 import j
from cloudbrokerlib import authenticator
from cloudbrokerlib.baseactor import BaseActor

class cloudapi_s3storage(BaseActor):
    """
    API Actor api, this actor is the final api a enduser uses to manage storagebuckets
    """
    def __init__(self):
        super(cloudapi_s3storage, self).__init__()
        self.osis_logs = j.clients.osis.getCategory(j.core.portal.active.osis, "system", "log")

    def _get(self, cloudspaceId):
        cloudspace = self.models.cloudspace.get(int(cloudspaceId)) 
        s3storagebuckets = self.models.s3user.search({'cloudspaceId':int(cloudspaceId), 'location':cloudspace.location})[1:]
        if len(s3storagebuckets) == 0:
            return None
        return s3storagebuckets[0]

    @authenticator.auth(acl={'cloudspace': set('R')})
    def get(self, cloudspaceId, **kwargs):
        """
        Gets the S3 details for a specific cloudspace
        param:cloudspaceId id of the space
        result list
        """
        ctx = kwargs['ctx']
        connectiondetails = self._get(cloudspaceId)
        if connectiondetails is None:
            ctx.start_response('404 Not Found', [])
            return 'No S3 Credentials found for this CloudSpace.'
        return connectiondetails

    @authenticator.auth(acl={'cloudspace': set('R')})
    def listbuckets(self, cloudspaceId, **kwargs):
        """
        List the storage buckets in a space.
        param:cloudspaceId id of the space
        result list
        """
        import boto
        import boto.s3.connection

        connectiondetails = self._get(cloudspaceId)
        if connectiondetails is None:
            return []

        access_key = connectiondetails['accesskey']
        secret_key = connectiondetails['secretkey']
        s3server = connectiondetails['s3url']
        conn = boto.connect_s3(access_key,secret_key,is_secure=True,host=s3server,calling_format = boto.s3.connection.OrdinaryCallingFormat())
        result = conn.get_all_buckets()
        buckets = [{'name':bucket.name, 's3url':s3server} for bucket in result]
        return buckets

