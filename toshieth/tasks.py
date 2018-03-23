import asyncio

from toshi.database import prepare_database, DatabaseMixin
from toshi.redis import prepare_redis, get_redis_connection, RedisMixin
from trq.worker import Worker
from trq.dispatch import Dispatcher as _Dispatcher

class BaseTaskHandler(DatabaseMixin, RedisMixin):
    def __init__(self, task_id, *args, **kwargs):
        self.task_id = task_id
        self.initialize(*args, **kwargs)

    def initialize(*args, **kwargs):
        pass

class BaseEthServiceWorker:
    def __init__(self, handlers, *, queue_name):
        self._handlers = handlers or []
        self._queue_name = queue_name
        self.worker = None

    def work(self):
        return asyncio.get_event_loop().create_task(self._work())

    async def _work(self):
        await prepare_database(handle_migration=False)
        redis = await prepare_redis()
        self.worker = Worker(self._handlers, queue_name=self._queue_name, connection=redis)
        self.worker.work()

    def shutdown(self):
        return self.worker.shutdown()

    def add_task_handler(self, cls, args=None, kwargs=None):
        if self.worker is None:
            self._handlers.append((cls, args or [], kwargs or {}))
        else:
            self.worker.add_task_handler(cls, args=args, kwargs=kwargs)

class Dispatcher(_Dispatcher):
    def __init__(self, *, queue_name):
        super().__init__(queue_name=queue_name)

    @property
    def connection(self):
        return get_redis_connection()

manager_dispatcher = Dispatcher(queue_name="manager")
push_dispatcher = Dispatcher(queue_name="pushservice")
eth_dispatcher = Dispatcher(queue_name="ethservice")
erc20_dispatcher = Dispatcher(queue_name="erc20")
collectibles_dispatcher = Dispatcher(queue_name="collectibles")
