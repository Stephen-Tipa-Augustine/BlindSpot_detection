"""
Author:     Stephen Tipa Augustine
Date:       29th/May/2020
License:    Unidentified
Purpose:    This module acts as a low level socket client implemented
            in python programming language
"""

# Importing required modules
import socket
import struct
import sys

from utility import Logging
import time


class Main(object):
    def __init__(self, address=('localhost', 9000), *args, **kwargs):
        self.log = Logging()
        self.log.info("Creating client socket")
        time.sleep(1.5)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.log.info("TCP Socket successfully created, and initiating connection")
        time.sleep(1)
        self.socket.connect(address)
        message = self.receive()
        self.log.info(message)

    def run(self):
        """
        starts the client main loop
        :return:
        """
        print("Enter a text below for processing or enter 'quit' to exit or 'loop' to measure throughput")
        while True:
            msg = input('-->: ')
            if msg != '':
                start_time = time.time()
                self.send(msg)
                if msg == 'quit':
                    print('Client requested server for connection break ...')
                    time.sleep(2)
                    receive_message = self.receive()
                    if receive_message == '1000':
                        print('Server acknowledged exit command')
                        print('Closing client socket ...')
                        time.sleep(2)
                        self.socket.close()
                        sys.exit(0)
                elif msg == "loop":
                    msg = input("Your message ?: ")
                    if msg:
                        latencies = []
                        for i in range(1000):
                            start_time = time.time()
                            self.send(msg)
                            receive_message = self.receive()
                            latency = time.time() - start_time
                            print("Server Reply: ", receive_message)
                            latencies.append(latency)
                        average_duration = sum(latencies) / len(latencies)
                        print('System throughput: ', (len(msg) * 8) / (average_duration * 1024), ' kbps')
                        continue
                receive_message = self.receive()
                latency = time.time() - start_time
                print("Server Reply: ", receive_message)
                print('Round Trip Latency: %f seconds' % latency)

    def send(self, msg):
        """
        Sends messages to server through client socket
        :param msg: its either str or bytes type
        :return: None
        """
        # Prefix each message with a 4-byte length (network byte order)
        if type(msg) is not bytes:
            msg = msg.encode('utf-8')
        msg = struct.pack('>I', len(msg)) + msg
        self.socket.sendall(msg)

    def receive(self):
        """
        Receives messages from server
        :return: str object
        """
        # Read message length and unpack it into an integer
        raw_msglen = self.recvall(self.socket, 4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        # Read the message data
        return self.recvall(self.socket, msglen).decode('utf-8')

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
                self.log.critical("Socket connection to server Broken")
                return None
            data.extend(packet)
        return data


if __name__ == '__main__':
    client = Main()
    client.run()
