from cloudbroker.actorlib.baseactor import BaseActor


class cloudapi_locations(BaseActor):

    def list(self, **kwargs):
        """
        List all locations

        :return list with every element containing details of a location as a dict
        """
        results = []
        for location in self.models.Location.objects:
            results.append(location.to_dict())
        return results

    def getUrl(self, **kwargs):
        """
        Get the portal url

        :return protal url
        """
        return self.config['portalurl']
