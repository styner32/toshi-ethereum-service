if __name__ == "__main__":
    import asyncio
    from toshieth.app import extra_service_config
    extra_service_config()
    from toshieth.collectibles import punks
    from toshieth.collectibles import erc721
    from toshieth.collectibles import worker

    m1 = erc721.ERC721TaskManager()
    m2 = punks.CryptoPunksTaskManager()

    w = worker.CollectiblesWorker()
    w.add_instance(m1)
    w.add_instance(m2)
    w.work()
    asyncio.get_event_loop().run_forever()
