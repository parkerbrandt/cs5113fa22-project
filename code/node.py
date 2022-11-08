# Imports
import re
import socket
import time

import grpc
import pokemonOU_pb2
import pokemonOU_pb2_grpc


class PokemonOUGame(pokemonOU_pb2_grpc.PokemonOUServicer):
    def __init__(self):
        return


"""
The Server Class

Handles input from both Trainers and Pokemon clients, and manages the grid
"""
class Server:
    def serve(self, gridsize):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        game = PokemonOUGame()
        pokemonOU_pb2_grpc.add_PokemonOUGameServicer_to_server(game, server)
        server.add_insecure_port('[::]:50051')
        server.start()
        
        print('Server started')
        try:
            while True:
                if game.is_done:
                    server.stop(0)
                time.sleep(1)
        except KeyboardInterrupt:
            server.stop(0)
        return


"""
The Pokemon Class
"""
class Pokemon:
    def __init__(self):
        return

    def run(self):
        return


"""
The Trainer Class
"""
class Trainer:
    def __init__(self):
        # Check in with the server, and receive an emoji designation

        return

    # Run the gameplay loop for the trainer
    def run(self):
        return



"""
Start of Program Logic

Decides which class the machine belongs to, and runs that code
"""

if __name__ == '__main__':
    
    # Parse any command-line arguments

    # Determine which class the program is
    hostname=re.sub(r'[0-9]', '', socket.gethostname())

    if hostname == 'server':
        server = Server()
        server.serve()
    elif hostname == 'trainer':
        trainer = Trainer()
        trainer.run()
    elif hostname == 'pokemon':
        pokemon = Pokemon()
        pokemon.run()
    