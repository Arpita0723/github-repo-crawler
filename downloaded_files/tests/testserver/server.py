import select
import socket
import ssl
import threading


def consume_socket_content(sock, timeout=0.5):
    chunks = 65536
    content = b""

    while True:
        more_to_read = select.select([sock], [], [], timeout)[0]
        if not more_to_read:
            break

        new_content = sock.recv(chunks)
        if not new_content:
            break

        content += new_content

    return content


class Server(threading.Thread):
    """Dummy server using for unit testing"""

    WAIT_EVENT_TIMEOUT = 5

    def __init__(
        self,
        handler=None,
        host="localhost",
        port=0,
        requests_to_handle=1,
        wait_to_close_event=None,
    ):
        super().__init__()

        self.handler = handler or consume_socket_content
        self.handler_results = []

        self.host = host
        self.port = port
        self.requests_to_handle = requests_to_handle

        self.wait_to_close_event = wait_to_close_event
        self.ready_event = threading.Event()
        self.stop_event = threading.Event()

    @classmethod
    def text_response_server(cls, text, request_timeout=0.5, **kwargs):
        def text_response_handler(sock):
            request_content = consume_socket_content(sock, timeout=request_timeout)
            sock.send(text.encode("utf-8"))

            return request_content

        return Server(text_response_handler, **kwargs)

    @classmethod
    def basic_response_server(cls, **kwargs):
        return cls.text_response_server(
            "HTTP/1.1 200 OK\r\n" + "Content-Length: 0\r\n\r\n", **kwargs
        )

    def run(self):
        try:
            self.server_sock = self._create_socket_and_bind()
            # in case self.port = 0
            self.port = self.server_sock.getsockname()[1]
            self.ready_event.set()
            self._handle_requests()

            if self.wait_to_close_event:
                self.wait_to_close_event.wait(self.WAIT_EVENT_TIMEOUT)
        finally:
            self.ready_event.set()  # just in case of exception
            self._close_server_sock_ignore_errors()
            self.stop_event.set()

    def _create_socket_and_bind(self):
        sock = socket.socket()
        sock.bind((self.host, self.port))
        sock.listen()
        return sock

    def _close_server_sock_ignore_errors(self):
        try:
            self.server_sock.close()
        except OSError:
            pass

    def _handle_requests(self):
        for _ in range(self.requests_to_handle):
            sock = self._accept_connection()
            if not sock:
                break

            handler_result = self.handler(sock)

            self.handler_results.append(handler_result)
            sock.close()

    def _accept_connection(self):
        try:
            ready, _, _ = select.select(
                [self.server_sock], [], [], self.WAIT_EVENT_TIMEOUT
            )
            if not ready:
                return None

            return self.server_sock.accept()[0]
        except OSError:
            return None

    def __enter__(self):
        self.start()
        if not self.ready_event.wait(self.WAIT_EVENT_TIMEOUT):
            raise RuntimeError("Timeout waiting for server to be ready.")
        return self.host, self.port

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.stop_event.wait(self.WAIT_EVENT_TIMEOUT)
        else:
            if self.wait_to_close_event:
                # avoid server from waiting for event timeouts
                # if an exception is found in the main thread
                self.wait_to_close_event.set()

        # ensure server thread doesn't get stuck waiting for connections
        self._close_server_sock_ignore_errors()
        self.join()
        return False  # allow exceptions to propagate


class TLSServer(Server):
    def __init__(
        self,
        *,
        handler=None,
        host="localhost",
        port=0,
        requests_to_handle=1,
        wait_to_close_event=None,
        cert_chain=None,
        keyfile=None,
        mutual_tls=False,
        cacert=None,
    ):
        super().__init__(
            handler=handler,
            host=host,
            port=port,
            requests_to_handle=requests_to_handle,
            wait_to_close_event=wait_to_close_event,
        )
        self.cert_chain = cert_chain
        self.keyfile = keyfile
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.ssl_context.load_cert_chain(self.cert_chain, keyfile=self.keyfile)
        self.mutual_tls = mutual_tls
        self.cacert = cacert
        if mutual_tls:
            # For simplicity, we're going to assume that the client cert is
            # issued by the same CA as our Server certificate
            self.ssl_context.verify_mode = ssl.CERT_OPTIONAL
            self.ssl_context.load_verify_locations(self.cacert)

    def _create_socket_and_bind(self):
        sock = socket.socket()
        sock = self.ssl_context.wrap_socket(sock, server_side=True)
        sock.bind((self.host, self.port))
        sock.listen()
        return sock
