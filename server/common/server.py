import signal
import socket
import logging

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._client_socket = None
        self._running = True
        self._shutting_down = False
        
        # Handle SIGINT (Ctrl+C) and SIGTERM (docker stop)
        signal.signal(signal.SIGINT, signal.signal(signal.SIGTERM, self.__graceful_shutdown_handler))

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """        
        try:
            while self._running:
                self._client_socket = self.__accept_new_connection()
                if self._client_socket:
                    self.__handle_client_connection()
        except Exception as e:
            logging.error(f'action: server_error | result: fail | error: {e}')
        finally:
            if not self._shutting_down:
                self.__graceful_shutdown_handler(None, None)

    def __handle_client_connection(self):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            # TODO: Modify the receive to avoid short-reads
            msg = self._client_socket.recv(1024).rstrip().decode('utf-8')
            addr = self._client_socket.getpeername()
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
            # TODO: Modify the send to avoid short-writes
            self._client_socket.send("{}\n".format(msg).encode('utf-8'))
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
        finally:
            self._client_socket.close()

    def __graceful_shutdown_handler(self, signum, frame):
        """
        Function closes the server socket and all the client sockets
        and then exits the program
        """
        logging.debug(
            f'action: graceful_shutdown | result: in_progress')
        self._running = False
        self._shutting_down = True
        if self._server_socket:
            self._server_socket.close()
            self._server_socket = None
            logging.info("action: close_server_socket | result: success")
        if self._client_socket:
            self._client_socket.close()
            self._server_socket = None
            logging.info("action: close_client_socket | result: success")
        logging.info("action: graceful_shutdown | result: success")

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
