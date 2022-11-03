# Imports
import socket

import grpc
import pokemonOU_pb2
import pokemonOU_pb2_grpc


class PokemonOUGame(pokemonOU_pb2_grpc.PokemonOUServicer):
    def funct():
        return

class Server:
    def serve(self):
        return

class Pokemon:
    def __init__(self):
        return

    def run(self):
        return

class Trainer:
    def __init__(self):
        return

    def run(self):
        return



"""
Start of Program Logic

Decides which class the program belongs to, and runs that code
"""

if __name__ == '__main__':
    
    # Parse any command-line arguments

    # Determine which class the program is
    if socket.gethostname() == 'server':
        print('Server')
    elif socket.gethostname() == 'trainer':
        print('Trainer')
    elif socket.gethostname() == 'pokemon':
        print('Pokemon')
    