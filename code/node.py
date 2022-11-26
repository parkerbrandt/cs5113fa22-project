# Imports
from concurrent import futures
from threading import Thread, Lock

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

    def __init__(self, board_sz):
        # Initialize variables and the initial game_board
        self.board_size = board_sz
        self.game_board = [[':seedling:' for i in range(self.board_size)] for j in range(self.board_size)]

        self.trainers = {}                  # A dictionary of trainer's names and their current location
        self.trainer_pokedexes = {}         # A dictionary of trainer's names and their current pokemon
        self.trainer_paths = {}             # All the locations that each trainer has visited
        self.people_emojis = []             # https://emojipedia.org/people/
        self.used_people_emojis = []        # A boolean array corresponding if each person emoji is used or not

        self.pokemon = {}                   # A dictionary of the pokemon and its current location
        self.pokemon_paths = {}             # A dictionary of the pokemon and all of its past locations                 
        self.animal_emojis = []             # https://emojipedia.org/nature/
        self.used_animal_emojis = []        # A boolean array corresponding if each animal emoji is used or not

        self.action_list = {}

        self.client_status = {}

        # Initialize people and animal emoji lists
        # Will read people_emoji_list.txt and animal_emoji_list.txt to get all used emojis
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
    def is_over(self):
        return

    def check_end(self):
        # Check if all pokemon had been captured
        return

    def captured(self, request, context):
        return pokemonou_pb2.Pokemon()

    # Prints out the list of actions that have occurred by every trainer/pokemon
    def actions(self, request, context):

        for k, v in self.action_list.items():
            print()

        return pokemonou_pb2.MoveList()

    # Prints the current board with pokemon and trainers
    def print_board(self):
        
        # Clear any previous boards that may exist (8 lines)
        # sys.stdout.write("\033[10F")

        # Print borders for the board
        for i in range(12):
            print(' -', end='')
        print()

        # Print the actual board
        for i in range(self.board_size):
            for j in range(self.board_size):    
                print('|' + emoji.emojize(self.game_board[i][j].strip()) + ' ', end='')

                if j == 7:
                    print('|', end='')

            # Newline
            print()


        for i in range(12):
            print(' -', end='')
        print()

        return

    # Wrapper for print_board() for clients to access
    def show_board(self, request, context):
        
        # Print the action that the client just did
        print(request.message)
        
        # Print the entire board
        self.print_board()

        return pokemonou_pb2.Board()


    """
    Trainer & Pokemon Functions
    """
    # Called by a client whenever they are first built
    # Will register the client with the server and designate a random emoji to the client based on their type
    
    # TODO: LOCK
    def initialize_client(self, request, context):
        emoji = ':skull:'
        
        if request.type == "trainer":
            if self.trainers.count(request.name) == 0:
                # Add the trainer to the server's list if they have not been added already
                # Choose a random emoji from the people emoji list
                emoji_idx = random.randint(0, len(self.people_emojis) - 1)
                
                # Check that the emoji hasn't been used yet
                while self.used_people_emojis[emoji_idx] is True:
                    emoji_idx = random.randint(0, len(self.people_emojis) - 1)
                
                self.used_people_emojis[emoji_idx] = True
                emoji = self.people_emojis[emoji_idx]
            else:
                return pokemonou_pb2.ClientInfo(name=request.name, emojiID=emoji, xLocation=-1, yLocation=-1)

        elif request.type == "pokemon":
            if self.pokemon.count(request.name) == 0:
                # Add the pokemon to the server's list if not added
                self.pokemon.append(request.name)

                # Choose a random emoji from the animal emoji list
                emoji_idx = random.randint(0, len(self.animal_emojis) - 1)
                
                # Check that the emoji hasn't been used yet
                while self.used_animal_emojis[emoji_idx] is True:
                    emoji_idx = random.randint(0, len(self.animal_emojis) - 1)
                
                self.used_animal_emojis[emoji_idx] = True
                emoji = self.animal_emojis[emoji_idx]
            else:
                return pokemonou_pb2.ClientInfo(name=request.name, emojiID=emoji, xLocation=-1, yLocation=-1)

        # Assign location as well on an unoccupied spot on the board
        # Unoccupied spots are denoted by a 0
        x = random.randint(0, self.board_size);
        y = random.randint(0, self.board_size);

        while self.game_board[x][y] == 0:
            x = random.randint(0, self.board_size);
            y = random.randint(0, self.board_size);

        # Adjust the board to have the trainer/pokemon's emoji
        self.game_board[x][y] = emoji

        # Add the location to the trainer and pokemon dictionaries, and the paths dictionaries
        if request.type == "trainer":
            self.trainer[request.name] = (x, y)
            self.trainer_paths[request.name] = [(x, y)]
        elif request.type == "pokemon":
            self.pokemon[request.name] = (x, y)
            self.pokemon_paths[request.name] = [(x, y)]

        return pokemonou_pb2.ClientInfo(name=request.name, emojiID=emoji, xLocation=x, yLocation=y)

    
    # TODO: LOCK
    def check_board(self, request, context):
        # Initial bare logic
        # TODO: Check for Pokemon and go to them
        valid_locations = []

        current_x = int(request.x)
        current_y = int(request.y)

        if current_x == self.board_size - 1:
            valid_locations.append()

        valid_locations = [(current_x  + 1, current_y), (current_x - 1, current_y), (current_x, current_y + 1), (current_x, current_y - 1)]
        return pokemonou_pb2.LocationList()

    # TODO: LOCK
    def move(self, request, context):
        return pokemonou_pb2.Move()

    def show_path(self, request, context):
        return pokemonou_pb2.LocationList()


    """
    Trainer Services
    """
    # TODO: LOCK
    def capture(self, request, context):

        # Check if a pokemon is in the location specified
        is_poke_there = False
        for pokemon in self.pokemon:
            break

        return pokemonou_pb2.Pokemon()

    def show_pokedex(self, request, context):
        return pokemonou_pb2.Pokedex()


    """
    Pokemon Services
    """
    def show_trainer_info(self, request, context):
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
                time.sleep(1)
        except KeyboardInterrupt:
            server.stop(0)
        return




"""
The Pokemon Class
"""
class Pokemon:

    def __init__(self, my_name):
        # Initialize variables
        self.name = my_name
        self.icon = ''
        self.x_loc = -1
        self.y_loc = -1
        return

    def run(self):
        with grpc.insecure_channel('server:50051') as channel:
            stub = pokemonou_pb2_grpc.PokemonOUStub(channel)

            # Initialize this Pokemon with the server, and get an emoji designation and location
            response = stub.Initialize(pokemonou_pb2.Name(name=self.name, type='pokemon'))
            self.icon = response.emojiID
            self.x_loc = int(response.xLocation)
            self.y_loc = int(response.yLocation)

            # Move around the board and avoid trainers
            while(True):
                
                # Check if captured
                
                # Get status from the server on if can move

                break

        return


"""
The Trainer Class
"""
class Trainer:

    def __init__(self, my_name):
        # Initialize variables
        self.name = my_name
        self.icon = ''
        self.x_loc = -1
        self.y_loc = -1
        return

    # Run the gameplay loop for the trainer
    def run(self):
        with grpc.insecure_channel('server:50051') as channel:
            stub = pokemonou_pb2_grpc.PokemonOUStub(channel)

            # Initialize this trainer with the server, and get an emoji designation
            response = stub.initialize_client(pokemonou_pb2.Name(name=self.name, type='trainer'))
            self.icon = response.emojiID
            self.x_loc = response.xLocation
            self.y_loc = response.yLocation

            # Move and attempt to capture pokemon
            is_game_over = False
            while(not is_game_over):
                
                # Check if a pokemon is in this space - if so, catch it, otherwise move
                action_msg = ""
                capture_res = stub.capture(pokemonou_pb2.ClientInfo(name=self.name, emoji=self.icon, xLocation=self.x_loc, yLocation=self.y_loc))
                if capture_res.name != "failure":
                    action_msg = "Captured " + capture_res.name + "."
                else:
                    # Move by checking the board, then finding suitable location
                    check_res = stub.CheckBoard()
                    valid_locs = []
                    new_x = 0
                    new_y = 0

                    action_msg = "Moved to (" + str(new_x) + ", " + str(new_y) + ") from"

                    move_res = stub.move_client(pokemonou_pb2.Location(x=0, y=0))

                # Check the status of the game
                status_res = stub.game_status()

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
    