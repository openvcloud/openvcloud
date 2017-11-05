from .base import BaseManager


class WebhookManager(BaseManager):
    def create(self, name, eventtypes, url):
        data = {
            'name': name,
            'eventtypes': eventtypes,
            'url': url,
        }
        self.client.webhooks.CreateWebhook(data)

    def delete(self, name):
        return self.client.webhooks.DeleteWebhook(name)
