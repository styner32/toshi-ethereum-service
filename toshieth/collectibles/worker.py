import asyncio
from trq.worker import Worker
from toshi.redis import get_redis_connection

class CollectiblesHandler:
    def __init__(self, task_id, worker):
        self.worker = worker

    def notify_new_block(self, blocknumber):
        for instance in self.worker.get_instances():
            if hasattr(instance, 'process_block'):
                asyncio.get_event_loop().create_task(instance.process_block(blocknumber))

class CollectiblesWorker(Worker):
    def __init__(self):
        super().__init__([(CollectiblesHandler, (self,))], queue_name="collectibles")
        self._instances = []

    def add_instance(self, instance):
        self._instances.append(instance)

    def get_instances(self):
        return self._instances

    @property
    def connection(self):
        return get_redis_connection()
