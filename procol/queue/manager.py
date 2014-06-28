from multiprocessing.managers import SyncManager


class QueueManager(SyncManager):
        pass


def queue_manager(queue, address=None):
    QueueManager.register('get_queue', callable=lambda: queue)

    return QueueManager(address=address, authkey='123456')


def queue_manager_process(queue):
    manager = queue_manager(queue)

    queue.start()
    manager.start()

    manager_queue = manager.get_queue()
    return manager_queue


def queue_server(queue, port=50000, serve_locally=True):
    host = '127.0.0.1' if serve_locally else '0.0.0.0'

    manager = queue_manager(queue, address=(host, port))
    queue.start()
    server = manager.get_server()

    print 'Serving on port: ', port
    server.serve_forever()


def queue_client(server_address=None):
    QueueManager.register('get_queue')

    queue = QueueManager(address=server_address, authkey='123456')
    queue.connect()

    pool = queue.get_queue()

    return pool