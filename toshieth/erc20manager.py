import asyncio
import logging

from tornado.httpclient import AsyncHTTPClient
from tornado.escape import json_encode

from toshi.log import configure_logger, log_unhandled_exceptions
from toshi.utils import parse_int
from toshi.config import config

from toshi.ethereum.mixin import EthereumMixin
from toshi.jsonrpc.client import JsonRPCClient

from toshieth.tasks import BaseEthServiceWorker, BaseTaskHandler, manager_dispatcher, erc20_dispatcher

log = logging.getLogger("toshieth.erc20manager")

class ERC20UpdateHandler(EthereumMixin, BaseTaskHandler):

    @log_unhandled_exceptions(logger=log)
    async def update_token_cache(self, contract_address, *eth_addresses):

        if len(eth_addresses) == 0:
            return

        is_wildcard = contract_address == "*"

        async with self.db:
            if is_wildcard:
                tokens = await self.db.fetch("SELECT contract_address FROM tokens")
            else:
                tokens = [{'contract_address': contract_address}]

        for address in eth_addresses:
            if is_wildcard:
                log.info("START update_token_cache(\"*\", {})".format(address))
                # NOTE: we don't remove this at the end on purpose
                # to avoid spamming of "*" refreshes
                should_run = await self.redis.set("bulk_token_update:{}".format(address), 1,
                                                  expire=60, exist=self.redis.SET_IF_NOT_EXIST)
                if not should_run:
                    log.info("ABORT update_token_cache(\"*\", {}): {}".format(address, should_run))
                    continue
                client = JsonRPCClient(config['ethereum']['url'])
                client._httpclient = AsyncHTTPClient(force_instance=True)
            else:
                client = self.eth
            for token in tokens:
                await self._update_token_cache(token['contract_address'], address, is_wildcard, client)
            if is_wildcard:
                log.info("DONE update_token_cache(\"*\", {})".format(address))

    async def _update_token_cache(self, contract_address, eth_address, should_send_update, client):
        try:
            data = "0x70a08231000000000000000000000000" + eth_address[2:]
            value = await client.eth_call(to_address=contract_address, data=data)
            # value of "0x" means something failed with the contract call
            if value == "0x0000000000000000000000000000000000000000000000000000000000000000" or value == "0x":
                if value == "0x":
                    log.warning("calling balanceOf for contract {} failed".format(contract_address))
                value = 0
            else:
                value = parse_int(value)  # remove hex padding of value
            async with self.db:
                if value > 0:
                    await self.db.execute(
                        "INSERT INTO token_balances (contract_address, eth_address, value) "
                        "VALUES ($1, $2, $3) "
                        "ON CONFLICT (contract_address, eth_address) "
                        "DO UPDATE set value = EXCLUDED.value",
                        contract_address, eth_address, hex(value))
                    send_update = True
                else:
                    rval = await self.db.execute(
                        "DELETE FROM token_balances WHERE contract_address = $1 AND eth_address = $2",
                        contract_address, eth_address)
                    if rval == "DELETE 1":
                        send_update = True
                    else:
                        send_update = False
                await self.db.commit()

            if should_send_update and send_update:
                data = {
                    "txHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
                    "fromAddress": "0x0000000000000000000000000000000000000000",
                    "toAddress": eth_address,
                    "status": "confirmed",
                    "value": hex(value),
                    "contractAddress": contract_address
                }
                message = "SOFA::TokenPayment: " + json_encode(data)
                manager_dispatcher.send_notification(eth_address, message)
        except:
            log.exception("WARNING: failed to update token cache of '{}' for address: {}".format(contract_address, eth_address))

class TaskManager(BaseEthServiceWorker):

    def __init__(self):
        super().__init__([(ERC20UpdateHandler,)], queue_name="erc20")
        configure_logger(log)

if __name__ == "__main__":
    from toshieth.app import extra_service_config
    extra_service_config()
    app = TaskManager()
    app.work()
    asyncio.get_event_loop().run_forever()
