# Imports
from concurrent import futures

import logging
import random
import re
import socket
import sys
import time

import grpc
import pokemonou_pb2
import pokemonou_pb2_grpc


"""
The Pokemon OU Game class

The class that implements the functions defined in the pokemonou.proto file
Most functions will be used for communicating between clients and server
"""
class PokemonOUGame(pokemonou_pb2_grpc.PokemonOUServicer):
    game_board = []
    clients = []
    people_emojis = []          # https://emojipedia.org/people/
    used_people_emojis = []     # A boolean array corresponding if each person emoji is used or not
    
    animal_emojis = []          # https://emojipedia.org/nature/
    used_animal_emojis = []     # A boolean array corresponding if each animal emoji is used or not

    def __init__(self):
        # Initialize people and animal emoji lists
        

        return

    """
    Server Services
    """
    def Captured(self, request, context):
        return pokemonou_pb2.Pokemon()

    def Moves(self, request, context):
        return pokemonou_pb2.MoveList()

    def Show_Board(self, request, context):
        return pokemonou_pb2.Board()


    """
    Trainer & Pokemon Functions
    """
    # Called by a client whenever they are first built
    # Will register the client with the server and designate a random emoji to the client based on their type
    def Initialize(self, request, context):
        emoji = 0
        if request.type == "trainer":
            # Choose a random emoji from the people emoji list
            emoji_idx = random.randint(0, len(self.people_emojis) - 1)
            
            # Check that the emoji hasn't been used yet
            while self.isused_people_emoji[emoji_idx] is True:
                emoji_idx = random.randint(0, len(self.people_emojis) - 1)
            
            self.isused_people_emojis[emoji_idx] = True
            emoji = self.people_emojis[emoji_idx]

        elif request.type == "pokemon":
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

        # TODO: Assign location as well on an unoccupied spot on the board
        # Unoccupied spots are denoted by a 0
        x = -1;
        y = -1;

        return pokemonou_pb2.ClientInfo(emojiID=emoji, xLocation=x, yLocation=y)

    
    def CheckBoard(self, request, context):
        return pokemonou_pb2.LocationList()

    def Show_Move(self, request, context):
        return pokemonou_pb2.Move()

    def ShowPath(self, request, context):
        return pokemonou_pb2.LocationList()

    """
    Trainer Services
    """
    def Capture(self, request, context):
        return pokemonou_pb2.Pokemon()

    def ShowPokedex(self, request, context):
        return pokemonou_pb2.Pokedex()


    """
    Pokemon Services
    """
    def ShowTrainerInfo(self, request, context):
        return pokemonou_pb2.Trainer()


"""
The Server Class

Handles input from both Trainers and Pokemon clients, and manages the grid
"""
class Server:

    # Handles input and output from the Trainer & Pokemon clients
    def serve(self, boardsize):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        game = PokemonOUGame()
        pokemonou_pb2_grpc.add_PokemonOUServicer_to_server(game, server)
        server.add_insecure_port('[::]:50051')
        server.start()
        
        print('Server started')
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            server.stop(0)
        return




"""
The Pokemon Class
"""
class Pokemon:
    my_name = ''
    icon = 0
    x_loc = 0
    y_loc = 0

    def __init__(self, name):
        self.my_name=name
        return

    def run(self):
        with grpc.insecure_channel('server:50051') as channel:
            stub = pokemonou_pb2_grpc.GuessingGameStub(channel)

            # Initialize this Pokemon with the server, and get an emoji designation
            response = stub.Initialize(pokemonou_pb2.Name(name=self.my_name, type='pokemon'))
            icon = response.emojiID

        return


"""
The Trainer Class
"""
class Trainer:
    my_name=''
    icon = 0
    x_loc = 0
    y_loc = 0

    def __init__(self, name):
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

    # Parse command-line arguments for size of board
    boardsz = int(sys.argv[1])

    # Determine which class the program is
    hostname = re.sub(r'[0-9]', '', socket.gethostname())

    if hostname == 'server':
        server = Server(boardsize=boardsz)
        server.serve()
    elif hostname == 'trainer':
        trainer = Trainer()
        trainer.run()
    elif hostname == 'pokemon':
        pokemon = Pokemon()
        pokemon.run()
    