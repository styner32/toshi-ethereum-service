import asyncio
import logging
from toshi.log import configure_logger, log_unhandled_exceptions
from toshi.database import prepare_database
from toshi.redis import prepare_redis
from toshi.config import config
from toshi.jsonrpc.client import JsonRPCClient
from toshi.utils import parse_int
from toshieth.tasks import erc20_dispatcher

log = logging.getLogger("toshieth.health_monitor")

INITIAL_WAIT_CALLBACK_TIME = 30
ERC20_CHECK_CALLBACK_TIME = 60 * 60

class HealthMonitor:

    def __init__(self):
        configure_logger(log)

        if 'monitor' in config:
            node_url = config['monitor']['url']
        else:
            log.warning("monitor using config['ethereum'] node")
            node_url = config['ethereum']['url']

        self.eth = JsonRPCClient(node_url, should_retry=True)

    def start(self):
        if not hasattr(self, '_startup_future'):
            self._startup_future = asyncio.get_event_loop().create_future()
            asyncio.get_event_loop().create_task(self._initialise())
            asyncio.get_event_loop().call_later(
                INITIAL_WAIT_CALLBACK_TIME,
                lambda: asyncio.get_event_loop().create_task(self.run_erc20_health_check()))
        return self._startup_future

    @log_unhandled_exceptions(logger=log)
    async def _initialise(self):
        # prepare databases
        self.pool = await prepare_database(handle_migration=False)
        await prepare_redis()

        self._startup_future.set_result(True)

    async def run_erc20_health_check(self):
        try:
            await self._run_erc20_health_check()
        except:
            log.exception("Error running health check")
        asyncio.get_event_loop().call_later(
            ERC20_CHECK_CALLBACK_TIME,
            lambda: asyncio.get_event_loop().create_task(self.run_erc20_health_check()))

    @log_unhandled_exceptions(logger=log)
    async def _run_erc20_health_check(self):

        log.info("running erc20 health check")
        async with self.pool.acquire() as con:
            token_balances = await con.fetch("SELECT * FROM token_balances")

        bad = 0
        requests = []
        last_execute = 0
        bulk = self.eth.bulk()

        for token in token_balances:
            contract_address = token['contract_address']
            data = "0x70a08231000000000000000000000000" + token['eth_address'][2:]

            f = bulk.eth_call(to_address=contract_address, data=data)
            requests.append((contract_address, token['eth_address'], f, token['value']))

            if len(requests) >= last_execute + 500:
                await bulk.execute()
                bulk = self.eth.bulk()
                last_execute = len(requests)

        if len(requests) > last_execute:
            await bulk.execute()

        bad_data = {}
        for contract_address, eth_address, f, db_value in requests:
            if not f.done():
                log.warning("future not done when checking erc20 cache")
                continue
            try:
                value = f.result()
            except:
                log.exception("error getting erc20 value {}:{}".format(contract_address, eth_address))
                continue
            if parse_int(value) != parse_int(db_value):
                bad += 1
                bad_data.setdefault(eth_address, set()).add(contract_address)

        if bad > 0:
            log.warning("Found {}/{} bad ERC20 caches over {} addresses".format(bad, len(token_balances), len(bad_data)))

            for eth_address in bad_data:
                erc20_dispatcher.update_token_cache("*", eth_address)
                await asyncio.sleep(15) # don't overload things

if __name__ == '__main__':
    from toshieth.app import extra_service_config
    extra_service_config()
    monitor = HealthMonitor()
    monitor.start()
    asyncio.get_event_loop().run_forever()
