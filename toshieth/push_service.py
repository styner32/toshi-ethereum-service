import asyncio
import logging

from toshieth.tasks import BaseEthServiceWorker, BaseTaskHandler
from toshi.config import config
from toshi.log import configure_logger
from toshi.push import PushServerClient, GCMHttpPushClient

log = logging.getLogger("toshieth.push_service")

class PushNotificationHandler(BaseTaskHandler):

    def initialize(self, pushclient):
        self.pushclient = pushclient

    async def send_notification(self, eth_address, message):

        async with self.db:
            rows = await self.db.fetch("SELECT * FROM notification_registrations WHERE eth_address = $1",
                                       eth_address)

        for row in rows:
            service = row['service']
            if service in ['gcm', 'apn']:
                log.debug("Sending {} PN to: {} ({})".format(service, eth_address, row['registration_id']))
                await self.pushclient.send(row['toshi_id'], service, row['registration_id'], {"message": message})

class PushNotificationService(BaseEthServiceWorker):

    def __init__(self, *, pushclient=None):

        super().__init__([], queue_name="pushservice")

        if pushclient is not None:
            self.pushclient = pushclient
        elif 'gcm' in config and 'server_key' in config['gcm'] and config['gcm']['server_key'] is not None:
            self.pushclient = GCMHttpPushClient(config['gcm']['server_key'])
        elif 'pushserver' in config and 'url' in config['pushserver'] and config['pushserver']['url'] is not None:
            self.pushclient = PushServerClient(url=config['pushserver']['url'],
                                               username=config['pushserver'].get('username'),
                                               password=config['pushserver'].get('password'))
        else:
            raise Exception("Unable to find appropriate push notification client config")

        self.add_task_handler(PushNotificationHandler, kwargs={'pushclient': self.pushclient})

        configure_logger(log)

if __name__ == "__main__":
    from toshieth.app import extra_service_config
    extra_service_config()
    app = PushNotificationService()
    app.work()
    asyncio.get_event_loop().run_forever()
