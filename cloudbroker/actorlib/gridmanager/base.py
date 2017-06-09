class BaseManager(object):
    def __init__(self, client, models):
        self.client = client
        self.models = models
