from .base import BaseManager
from requests import exceptions


class GraphManager(BaseManager):
    def getGraphUrl(self, graph):
        return self.client.graphs.GetGraph(graph).json()['url']

    def setGraphUrl(self, graph, url):
        return self.client.graphs.UpdateGraph({'url': url}, graph)

    def getDashboardUrl(self, graph, dashboard):
        return self.client.graphs.GetDashboard(graph, dashboard).json()['url']
