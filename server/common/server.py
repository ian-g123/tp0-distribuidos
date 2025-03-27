import signal
import socket
import logging

from multiprocessing import Barrier, Process, Lock
from common.comunication import read_from_socket, write_in_socket
from common.serializer import deserializeBets
from common.utils import has_won, load_bets, store_bets

FINISH_MESSAGE = "finish"


class Server:
    def __init__(self, port, listen_backlog, amount_of_clients):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)

        self._amount_of_clients = amount_of_clients
        self._agency_socket = None
        self._agency_id = None
        self._lock = Lock()
        self._barrier = Barrier(amount_of_clients)
        self._running = True
        self._shutting_down = False

        # Handle SIGINT (Ctrl+C) and SIGTERM (docker stop)
        signal.signal(signal.SIGTERM, self.__graceful_shutdown_handler)
        signal.signal(signal.SIGINT, self.__graceful_shutdown_handler)

    def run(self):
        processes = []
        try:
            for _ in range(self._amount_of_clients):
                process = Process(target=self.__run)
                process.start()
                processes.append(process)
            for process in processes:
                process.join()
        finally:
            if not self._shutting_down:
                self.__graceful_shutdown_handler()

    def __run(self):
        """
        Executes the main server operations in a controlled sequence.

        This method handles the reception of client connections for subprocesses, synchronizes
        operations using a barrier, processes bet results, and ensures proper
        shutdown in case of errors or completion.
        """
        try:
            self.__receive_client()
            self._barrier.wait()
            logging.info("action: sorteo | result: success")
            self.__handle_bet_results()
        except Exception as e:
            logging.error(f'action: server_error | result: fail | error: {e}')
        finally:
            if not self._shutting_down:
                self.__graceful_shutdown_handler()

    def __handle_bet_results(self):
        """
        Handles the processing of bet results by determining the winners and notifying
        the winners associated with the current agency.
        """
        received_bets = load_bets()
        winners_bets = [bet for bet in received_bets if has_won(bet)]
        my_agency_winners = [
            bet for bet in winners_bets if bet.agency == self._agency_id]
        self.__notify_winners(my_agency_winners)

    def __receive_client(self):
        """
        Handles the process of accepting a new client connection and receiving bets from the client.

        This method first accepts a new client connection. If a client socket is successfully
        established, it proceeds to receive bets from the connected client.
        """
        client_socket = self.__accept_new_connection()
        if client_socket:
            self.__receive_bets(client_socket)

    def __receive_bets(self, client_socket):
        """
        Handles the reception of bets from a client socket.

        This method continuously reads data from the client socket, deserializes
        the received bets, and stores them. It also keeps track of the total number
        of bets received and any errors encountered during the deserialization
        process. Once the client signals the end of transmission, the method logs
        the results and sends a summary back to the client.
        """
        data_received = ""
        amount_of_bets = 0
        errors_in_bets = 0

        while True:
            data_received = read_from_socket(client_socket)
            if data_received == FINISH_MESSAGE:
                break
            bets, errors = deserializeBets(data_received)
            if bets:
                agency_bets = bets[0].agency
                self._agency_socket = client_socket
                self._agency_id = agency_bets
            with self._lock:
                store_bets(bets)
            amount_of_bets += len(bets)
            errors_in_bets += errors
        result = "success" if errors_in_bets == 0 else "fail"
        logging.info(
            f"action: apuesta_recibida | result: {result} | cantidad: {amount_of_bets}")
        write_in_socket(
            client_socket, f"Se recibieron correctamente {amount_of_bets} de {amount_of_bets + errors_in_bets} apuestas")

    def __notify_winners(self, winners_bets):
        """
        Notify winners of the lottery contest

        Function sends a message to the winners of the lottery contest
        """
        winners_doc = [winner.document for winner in winners_bets]
        winners_doc = ",".join(winners_doc)
        try:
            write_in_socket(self._agency_socket, winners_doc)
            logging.info(
                f"action: notify_winners | result: success | agency: {self._agency_id} | winners: {winners_doc}")
        except Exception as e:
            logging.error(
                f"action: notify_winners | result: fail | agency: {self._agency_id} | error: {e}")

    def __graceful_shutdown_handler(self, signum=None, frame=None):
        """
        Function closes the server socket and all the client sockets
        """
        logging.debug(
            f'action: graceful_shutdown | result: in_progress')
        self._running = False
        self._shutting_down = True
        if self._server_socket:
            self._server_socket.close()
            logging.info("action: close_server_socket | result: success")
        if self._agency_socket:
            self._agency_socket.close()
            logging.info("action: close_agency_socket | result: success")
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
        logging.info(
            f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
