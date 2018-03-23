import asyncio
import os
import toshi.web

from toshieth import handlers
from toshieth import websocket

from toshi.handlers import GenerateTimestamp

from toshi.config import config
from toshi.log import configure_logger
from toshi.log import log as services_log
from toshi.jsonrpc.client import JsonRPCClient

def extra_service_config():
    config.set_from_os_environ('ethereum', 'url', 'ETHEREUM_NODE_URL')
    config.set_from_os_environ('monitor', 'url', 'MONITOR_ETHEREUM_NODE_URL')
    if 'ethereum' in config:
        if 'ETHEREUM_NETWORK_ID' in os.environ:
            config['ethereum']['network_id'] = os.environ['ETHEREUM_NETWORK_ID']
        else:
            config['ethereum']['network_id'] = asyncio.get_event_loop().run_until_complete(
                JsonRPCClient(config['ethereum']['url']).net_version())

    # push service config
    config.set_from_os_environ('pushserver', 'url', 'PUSH_URL')
    config.set_from_os_environ('pushserver', 'username', 'PUSH_USERNAME')
    config.set_from_os_environ('pushserver', 'password', 'PUSH_PASSWORD')
    config.set_from_os_environ('gcm', 'server_key', 'GCM_SERVER_KEY')

urls = [
    (r"^/v1/tx/skel/?$", handlers.TransactionSkeletonHandler),
    (r"^/v1/tx/?$", handlers.SendTransactionHandler),
    (r"^/v1/tx/cancel/?$", handlers.CancelTransactionHandler),
    (r"^/v1/tx/(0x[0-9a-fA-F]{64})/?$", handlers.TransactionHandler),
    (r"^/v1/balance/(0x[0-9a-fA-F]{40})/?$", handlers.BalanceHandler),
    (r"^/v1/address/(0x[0-9a-fA-F]{40})/?$", handlers.AddressHandler),
    (r"^/v1/timestamp/?$", GenerateTimestamp),
    (r"^/v1/(apn|gcm)/register/?$", handlers.PNRegistrationHandler),
    (r"^/v1/(apn|gcm)/deregister/?$", handlers.PNDeregistrationHandler),
    (r"^/v1/ws/?$", websocket.WebsocketHandler),
    (r"^/v1/tokens/(0x[0-9a-fA-F]{40})/?$", handlers.TokenHandler),
    (r"^/v1/tokens/(0x[0-9a-fA-F]{40})/(0x[0-9a-fA-F]{40})/?$", handlers.TokenHandler),
    (r"^/v1/tokens/?$", handlers.TokenListHandler),
    (r"^/v1/collectibles/(0x[0-9a-fA-F]{40})/?$", handlers.CollectiblesHandler),
    (r"^/v1/collectibles/(0x[0-9a-fA-F]{40})/(0x[0-9a-fA-F]{40})/?$", handlers.CollectiblesHandler),

    (r"^/v1/gasprice/?$", handlers.GasPriceHandler),

    # legacy
    (r"^/v1/register/?$", handlers.LegacyRegistrationHandler),
    (r"^/v1/deregister/?$", handlers.LegacyDeregistrationHandler),

    # (essentially) static file access
    (r"^/token/(?P<address>.+)\.(?P<format>.+)$", handlers.TokenIconHandler),

    # status
    (r"^/v1/status/?$", handlers.StatusHandler)
]

class Application(toshi.web.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        configure_logger(services_log)
        extra_service_config()

    async def _start(self):
        await super()._start()
        self.worker = websocket.EthServiceWorker()
        self.worker.work()

def main():
    app = Application(urls)
    app.start()
