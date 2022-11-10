# Imports
from concurrent import futures

import logging
import random
import re
import socket
import time

import grpc
import pokemonOU_pb2
import pokemonOU_pb2_grpc


"""
The Pokemon OU Game class

The class that implements the functions defined in the pokemonou.proto file
Most functions will be used for communicating between clients and server
"""
class PokemonOUGame(pokemonOU_pb2_grpc.PokemonOUServicer):
    
    clients = []
    people_emojis = []      # https://emojipedia.org/people/
    isused_people_emojis = []

    animal_emojis = []      # https://emojipedia.org/nature/
    isused_animal_emojis = []

    def __init__(self):
        # Initialize people and animal emoji lists
        

        return

    """
    Trainer & Pokemon Functions
    """

    # Called by a client whenever they are first built
    # Will register the client with the server and designate a random emoji to the client based on their type
    def Initialize(self, client_type):
        emoji = 0
        if client_type == "trainer":
            # Choose a random emoji from the people emoji list
            emoji_idx = random.randint(0, len(self.people_emojis) - 1)
            
            # Check that the emoji hasn't been used yet
            while self.isused_people_emoji[emoji_idx] is True:
                emoji_idx = random.randint(0, len(self.people_emojis) - 1)
            
            self.isused_people_emojis[emoji_idx] = True
            emoji = self.people_emojis[emoji_idx]

        elif client_type == "pokemon":
            # Choose a random emoji from the animal emoji list
            emoji_idx = random.randint(0, len(self.animal_emojis) - 1)
            
            # Check that the emoji hasn't been used yet
            while self.isused_animal_emoji[emoji_idx] is True:
                emoji_idx = random.randint(0, len(self.animal_emojis) - 1)
            
            self.isused_animal_emojis[emoji_idx] = True
            emoji = self.animal_emojis[emoji_idx]

        else:
            # Return -1 to denote an invalid input
            emoji = -1

        return emoji


"""
The Server Class

Handles input from both Trainers and Pokemon clients, and manages the grid
"""
class Server:

    # Handles input and output from the Trainer & Pokemon clients
    def serve(self, gridsize):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        game = PokemonOUGame()
        pokemonOU_pb2_grpc.add_PokemonOUServicer_to_server(game, server)
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
    port = "50051"
    icon = 0

    def __init__(self):
        # Check in with the server, and receive an emoji designation

        return

    def run(self):
        return


"""
The Trainer Class
"""
class Trainer:
    port = "50051"
    icon = 0

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
    # Begin logging
    logging.basicConfig()

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
    