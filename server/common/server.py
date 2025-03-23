import signal
import socket
import logging

from common.comunication import read_from_socket, write_in_socket
from common.serializer import deserializeBets
from common.utils import has_won, load_bets, store_bets

FINISH_MESSAGE = "finish"


class Server:
    def __init__(self, port, listen_backlog, amount_of_clients):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._amount_of_clients = amount_of_clients
        self._agency_sockets = {}
        self._running = True
        self._shutting_down = False

        # Handle SIGINT (Ctrl+C) and SIGTERM (docker stop)
        signal.signal(signal.SIGINT, signal.signal(
            signal.SIGTERM, self.__graceful_shutdown_handler))

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """
        try:
            for _ in range(self._amount_of_clients):
                client_socket = self.__accept_new_connection()
                if client_socket:
                    self.__receive_bets(client_socket)
            # consultar ganadores
            logging.info("action: sorteo | result: success")
            received_bets = load_bets()
            winners_bets = [bet for bet in received_bets if has_won(bet)]
            self.__notify_winners(winners_bets)
        except Exception as e:
            logging.error(f'action: server_error | result: fail | error: {e}')
        finally:
            if not self._shutting_down:
                self.__graceful_shutdown_handler()

    def __receive_bets(self, client_socket):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
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
                self._agency_sockets[agency_bets] = client_socket
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
        agency_winners = {agency: [] for agency in self._agency_sockets.keys()}

        # Sort winners by agency
        while winners_bets:
            winner_bet = winners_bets.pop()
            agency_winners[winner_bet.agency].append(winner_bet.document)

        # Notify each agency
        for agency, winners in agency_winners.items():
            winners_docs = ",".join(winners)
            agency_socket = self._agency_sockets.get(agency)
            if agency_socket:
                try:
                    write_in_socket(agency_socket, winners_docs)
                    logging.info(
                        f"action: notify_winners | result: success | agency: {agency} | winners: {winners_docs}")
                except Exception as e:
                    logging.error(
                        f"action: notify_winners | result: fail | agency: {agency} | error: {e}")

        logging.info("action: notify_winners | result: success")

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
        for client_socket in self._agency_sockets.values():
            client_socket.close()
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
        logging.info(
            f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
