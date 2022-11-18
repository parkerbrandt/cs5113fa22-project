# Imports
from concurrent import futures

import emoji
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
    board_size = 0
    game_board = []
    trainers = []
    pokemon = []
    moves = {}

    people_emojis = []          # https://emojipedia.org/people/
    used_people_emojis = []     # A boolean array corresponding if each person emoji is used or not
    
    animal_emojis = []          # https://emojipedia.org/nature/
    used_animal_emojis = []     # A boolean array corresponding if each animal emoji is used or not

    def __init__(self, board_sz):        
             
        # Initialize the board
        # :grass: indicates that each space is empty, will be changed whenever a trainer or pokemon connects
        self.board_size = board_sz
        
        self.game_board = [[':seedling:' for i in range(self.board_size)] for j in range(self.board_size)]

        # Initialize people and animal emoji lists
        # Will read people_emoji_list.txt and animal_emoji_list.txt to get all necessary emojis
        with open('people_emoji_list.txt', 'r') as p:
            lines = p.readlines()

            for i in range(len(lines)):
                self.people_emojis.append(lines[i])
                self.used_people_emojis.append(False)

        with open('animal_emoji_list.txt', 'r') as a:
            lines = a.readlines()

            for i in range(len(lines)):
                self.animal_emojis.append(lines[i])
                self.used_animal_emojis.append(False)

        return

    """
    Server Services
    """
    def Captured(self, request, context):
        return pokemonou_pb2.Pokemon()

    def Moves(self, request, context):
        return pokemonou_pb2.MoveList()

    # Prints the current board with pokemon and trainers
    def print_board(self):
        
        # Clear any previous boards that may exist (8 lines)
        # for i in range(8):
        #     sys.stdout.write("\033[F")

        # Print borders for the board
        for i in range(15):
            print('-', end='')

        # Print the actual board
        for i in range(self.board_size):
            for j in range(self.board_size):    

                print('|' + emoji.emojize(self.game_board[i][j]) + ' ', end='')

                if j == 7:
                    print('|', end='')

            # Newline
            print()


        for i in range(15):
            print('-', end='')

        return

    # Wrapper for print_board() for clients to access
    def Show_Board(self, request, context):
        self.print_board()

        return pokemonou_pb2.Board()


    """
    Trainer & Pokemon Functions
    """
    # Called by a client whenever they are first built
    # Will register the client with the server and designate a random emoji to the client based on their type
    def Initialize(self, request, context):
        emoji = 'N'
        
        if request.type == "trainer":
            if self.trainers.count(request.name) == 0:
                # Add the trainer to the server's list if they have not been added already
                self.trainers.append(request.name)

                # Choose a random emoji from the people emoji list
                emoji_idx = random.randint(0, len(self.people_emojis) - 1)
                
                # Check that the emoji hasn't been used yet
                while self.used_people_emoji[emoji_idx] is True:
                    emoji_idx = random.randint(0, len(self.people_emojis) - 1)
                
                self.used_people_emojis[emoji_idx] = True
                emoji = self.people_emojis[emoji_idx]

        elif request.type == "pokemon":
            if self.pokemon.count(request.name) == 0:
                # Add the pokemon to the server's list if not added
                self.pokemon.append(request.name)

                # Choose a random emoji from the animal emoji list
                emoji_idx = random.randint(0, len(self.animal_emojis) - 1)
                
                # Check that the emoji hasn't been used yet
                while self.used_animal_emoji[emoji_idx] is True:
                    emoji_idx = random.randint(0, len(self.animal_emojis) - 1)
                
                self.used_animal_emojis[emoji_idx] = True
                emoji = self.animal_emojis[emoji_idx]

        # Assign location as well on an unoccupied spot on the board
        # Unoccupied spots are denoted by a 0
        x = random.randint(0, self.board_size);
        y = random.randint(0, self.board_size);

        while self.game_board[x][y] == 0:
            x = random.randint(0, self.board_size);
            y = random.randint(0, self.board_size);

        # Adjust the board to have the trainer/pokemon
        self.game_board[x][y] = emoji

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
        game = PokemonOUGame(board_sz = boardsize)
        pokemonou_pb2_grpc.add_PokemonOUServicer_to_server(game, server)
        server.add_insecure_port('[::]:50051')
        server.start()
        
        print('Server started')

        try:
            while True:
                # Show the board once every second
                game.print_board()

                time.sleep(1)
        except KeyboardInterrupt:
            server.stop(0)
        return




"""
The Pokemon Class
"""
class Pokemon:
    my_name = ''
    icon = ''
    x_loc = -1
    y_loc = -1

    def __init__(self, name):
        # Initialize variables
        self.my_name=name
        return

    def run(self):
        with grpc.insecure_channel('server:50051') as channel:
            stub = pokemonou_pb2_grpc.PokemonOUStub(channel)

            # Initialize this Pokemon with the server, and get an emoji designation
            response = stub.Initialize(pokemonou_pb2.Name(name=self.my_name, type='pokemon'))
            self.icon = response.emojiID
            self.x_loc = response.xLocation
            self.y_loc = response.yLocation

            # Print the board
            stub.Show_Board()

        return


"""
The Trainer Class
"""
class Trainer:
    my_name=''
    icon = ''
    x_loc = -1
    y_loc = -1

    def __init__(self, name):
        # Initialize variables
        self.my_name = name
        return

    # Run the gameplay loop for the trainer
    def run(self):
        with grpc.insecure_channel('server:50051') as channel:
            stub = pokemonou_pb2_grpc.PokemonOUStub(channel)

            # Initialize this trainer with the server, and get an emoji designation
            response = stub.Initialize(pokemonou_pb2.Name(name=self.my_name, type='trainer'))
            self.icon = response.emojiID
            self.x_loc = response.xLocation
            self.y_loc = response.yLocation

            # Print the board


            # Move and attempt to capture pokemon

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
        server = Server()
        server.serve(boardsize=boardsz)
    elif hostname == 'trainer':
        trainer = Trainer(name=socket.gethostname())
        trainer.run()
    elif hostname == 'pokemon':
        pokemon = Pokemon(name=socket.gethostname())
        pokemon.run()
    