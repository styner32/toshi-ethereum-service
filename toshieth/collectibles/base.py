import asyncio
import os
from toshi.database import prepare_database
from toshi.redis import prepare_redis
from toshi.jsonrpc.client import JsonRPCClient

from toshi.config import config

def extra_service_config():
    if 'COLLECTIBLE_IMAGE_FORMAT_STRING' in os.environ:
        config.set_from_os_environ('collectibles', 'image_format', 'COLLECTIBLE_IMAGE_FORMAT_STRING')
    else:
        # avoid throwing an exception when running tests
        import inspect
        caller = inspect.currentframe()
        while caller.f_back is not None:
            caller = caller.f_back
            if caller.f_globals['__name__'] == 'unittest.main':
                break
        else:
            raise Exception("Missing $COLLECTIBLE_IMAGE_FORMAT_STRING")

class CollectiblesTaskManager:

    def __init__(self):
        extra_service_config()
        self.eth = JsonRPCClient(config['ethereum']['url'], should_retry=False)
        asyncio.get_event_loop().create_task(self._initialize())

    async def _initialize(self):
        self.pool = await prepare_database(handle_migration=False)
        await prepare_redis()
        asyncio.get_event_loop().create_task(self.process_block())

    async def shutdown(self):
        pass

    async def process_block(self):
        raise NotImplementedError()
