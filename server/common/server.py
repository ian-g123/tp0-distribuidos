import signal
import socket
import logging

from common.comunication import read_from_socket, write_in_socket
from common.serializer import deserializeBet
from common.utils import store_bets

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
                self.__graceful_shutdown_handler()

    def __handle_client_connection(self):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        bet = self.__receive_bet()
        if not bet:
            return
        store_bets([bet])
        write_in_socket(self._client_socket, "Bet received")
        self._client_socket.close()
        logging.info(
            f"action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}")

    def __receive_bet(self):
        json_data = read_from_socket(self._client_socket)
        if not json_data:
            logging.error("action: receive_bet | result: fail | error: no data received")
            write_in_socket(self._client_socket, "Invalid bet")
            self._client_socket.close()
            return
        logging.debug(f"action: receive_bet | result: in_progress | msg: {json_data}")
        try:
            return deserializeBet(json_data)
        except Exception as e:
            logging.error(f"action: deserialize_bet | result: fail | error: {e}")
            write_in_socket(self._client_socket, "Invalid bet")
            self._client_socket.close()

    def __graceful_shutdown_handler(self):
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
            logging.info("action: close_server_socket | result: success")
        if self._client_socket:
            self._client_socket.close()
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
