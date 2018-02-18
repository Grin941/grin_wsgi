import logging
import socket
import threading
import multiprocessing


class SimpleHTTPServer:
    """ TCP IPv4 socket
    binded to passed hostname and port.
    """

    CONNECTION_QUEUE_LIMIT = 1
    SOCKET_FAMILY = socket.AF_INET
    SOCKET_TYPE = socket.SOCK_STREAM
    MULTITHREAD = False
    MULTIPROCESS = False

    def __init__(self, host, port):
        self._serversock = None
        self._create_serversocket(host, port)

    def _create_serversocket(self, host, port):
        self._serversock = socket.socket(self.SOCKET_FAMILY, self.SOCKET_TYPE)
        self._serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._serversock.bind((host, port))

    def process_request(self, request_handler):
        self._serversock.listen(self.CONNECTION_QUEUE_LIMIT)
        while True:
            self._accept(request_handler)

    def _accept(self, request_handler):
        clientsock, address = self._serversock.accept()
        try:
            request = clientsock.recv(1024).decode('utf-8')
            logging.debug('Request: {}'.format(request))
            if not request: raise
            response = request_handler(request)
            logging.debug('Response: {}'.format(response))
            clientsock.sendall(response)
        except Exception:
            clientsock.close()
            return False


class ThreadedHTTPServer(SimpleHTTPServer):
    """ TCP IPv4 socket listening connection
    in a multiple threads and
    binded to passed hostname and port.
    """

    CONNECTION_QUEUE_LIMIT = 5
    MULTITHREAD = True

    def _accept(self, request_handler):
        clientsock, address = self._serversock.accept()
        clientsock.settimeout(60)
        threading.Thread(target=request_handler,
                         args=(clientsock, address))


class MultiprocessingHTTPServer(SimpleHTTPServer):
    """ TCP IPv4 socket listenning connections in
    a multiple processess and
    binded to passed hostname and port.
    """

    CONNECTION_QUEUE_LIMIT = 1
    MULTIPROCESS = True

    def _accept(self, request_handler):
        clientsock, address = self._serversock.accept()
        process = multiprocessing.Process(target=request_handler,
                                          args=(clientsock, address))
        process.daemon = True
        process.start()
