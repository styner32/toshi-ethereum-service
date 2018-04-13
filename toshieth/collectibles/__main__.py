if __name__ == "__main__":
    import asyncio
    from toshieth.app import extra_service_config

    from toshi.database import prepare_database
    from toshi.redis import prepare_redis

    from toshieth.collectibles import punks
    from toshieth.collectibles import erc721
    from toshieth.collectibles import worker

    extra_service_config()

    # prepare databases
    asyncio.get_event_loop().run_until_complete(prepare_database(handle_migration=False))
    asyncio.get_event_loop().run_until_complete(prepare_redis())

    m1 = erc721.ERC721TaskManager()
    m2 = punks.CryptoPunksTaskManager()

    w = worker.CollectiblesWorker()
    w.add_instance(m1)
    w.add_instance(m2)

    # this is to catch errors in the worker, otherwise the
    # logs get swallowed
    def done_callback(f):
        print(f.result())
    w.work().add_done_callback(done_callback)

    asyncio.get_event_loop().run_forever()
