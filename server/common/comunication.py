import socket


def write_in_socket(socket: socket.socket, msg: str):
    """
    Write a message to a socket

    :param socket: socket to write to
    :param msg: message to write
    """
    socket.sendall(len(msg).to_bytes(4, 'big') + msg.encode('utf-8'))

def read_from_socket(socket: socket.socket) -> str:
    """
    Read a message from a socket

    :param socket: socket to read from
    :return: message read
    """
    msg_len = int.from_bytes(socket.recv(4), 'big')
    data_recv = b""
    while len(data_recv) < msg_len:
        data_recv += socket.recv(msg_len - len(data_recv))
    return data_recv.decode('utf-8')
