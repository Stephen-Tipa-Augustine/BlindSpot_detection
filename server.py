"""
Author:     Stephen Tipa Augustine
Date:       29th/May/2020
License:    Unidentified
Purpose:    This module acts as a low level socket server implemented
            in python programming language
"""

# Importing necessary modules
import struct
import threading
import socket
import time
from utility import Logging


class Main(object):
    def __init__(self, *args, **kwargs):
        self.log = Logging()  # Initializes the logger class
        server_address = ("localhost", 9000)
        self.log.info("Starting server ...")
        time.sleep(2)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.log.info("TCP Socket successfully created")
        time.sleep(2)
        self.socket.bind(server_address)  # Binds to localhost
        self.log.info("Server socket bind to address: {:} and port: {:}".format(server_address[0], server_address[1]))
        time.sleep(1.5)
        self.socket.listen(5)
        self.clients = []

    def run(self, *args):
        '''
        Starts the server application
        :param args: extra args
        :return: None
        '''
        self.log.info("Server listening, and waiting for client connections")
        while True:
            client_socket, client_address = self.socket.accept()
            self.send("Connected at: {:}".format(client_address), client_socket)
            self.log.info(
                "Connection to the client: {:} at address: {:} has been established".format(client_socket.getsockname(),
                                                                                            client_address))
            try:
                threading.Thread(target=self.client_handler, args=(client_socket, client_address)).start()
                self.log.info('client thread for:{:} started'.format(client_address))
            except:
                client_socket.close()
                self.log.error('client thread for:{:} failed to start'.format(client_address))

    def client_handler(self, client_socket, client_address):
        """
        Handles client requests
        :param client_socket: client socket object
        :param client_address: client address, a Python tuple object
        :return: False
        """
        while True:
            received_message = self.receive(client_socket)
            if received_message is None:
                continue
            else:
                self.log.info("Server received text: " + received_message + ' from: {:}'.format(client_address))
                if received_message == 'quit':
                    self.log.info('client at {:} is closing socket connection'.format(client_address))
                    self.send('1000', client_socket)
                    client_socket.close()
                    return False
                received_message = received_message.upper()
                self.send(received_message, client_socket)
                self.log.info("Server processed text and sent: " + received_message + ' to: {:}'.format(client_address))
        client_socket.close()

    @staticmethod
    def send(msg, client_socket):
        """
        Sends messages to client through client socket
        :param client_socket:
        :param msg: its either str or bytes type
        :return: None
        """
        # Prefix each message with a 4-byte length (network byte order)
        if type(msg) is not bytes:
            msg = msg.encode('utf-8')
        msg = struct.pack('>I', len(msg)) + msg
        client_socket.sendall(msg)

    def receive(self, client_socket):
        """
        receives messages from clients
        :param client_socket: client socket object
        :return: str object
        """
        # Read message length and unpack it into an integer
        raw_msglen = self.recvall(client_socket, 4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        # Read the message data
        return self.recvall(client_socket, msglen).decode('utf-8')

    def recvall(self, sock, n):
        """
        A helper function for receive()
        :param sock: Client socket object
        :param n: number of bytes to be received, its int type
        :return: bytes array object
        """
        # Helper function to recv n bytes or return None if EOF is hit
        data = bytearray()
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                self.log.critical("Socket connection to client Broken")
                return None
            data.extend(packet)
        return data


if __name__ == "__main__":
    server = Main()
    server.run()
