# Imports
from concurrent import futures
from termcolor import colored

import emoji
import logging
import random
import re
import socket
import sys
import threading
import time

import grpc
import pokemonou_pb2
import pokemonou_pb2_grpc


"""
The Pokemon OU Game class

The class that implements the functions defined in the pokemonou.proto file
Most functions will be used for communicating between clients and server
Some functions are called only by the server machine
"""
class PokemonOUGame(pokemonou_pb2_grpc.PokemonOUServicer):     

    def __init__(self, board_sz):
        # Initialize variables and the initial game_board
        self.status = "active"
        
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

        self.action_list = []               # A list of all the actions that have occurred in the game

        # Lock variables
        self._key_lock = threading.Lock()

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
    def game_status(self, request, context):
        # Iterate over all pokemon and check if all are captured
        return pokemonou_pb2.GameStatus(status=self.status)

    def captured(self, request, context):
        return pokemonou_pb2.Name(name=, type=)

    # Prints out the list of actions that have occurred by every trainer/pokemon
    def actions(self):
        for action in self.action_list:
            print(action)
        return

    # Prints the current board with pokemon and trainers
    def print_board(self):

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
        
        # Print the entire board
        self.print_board()

        # Print the actions that this client has performed in their turn
        for action in request.actions:
            print(colored(action, 'yellow'))

        return pokemonou_pb2.GameStatus(status=self.status)


    """
    Trainer & Pokemon Functions
    """
    # Called by a client whenever they are first built
    # Will register the client with the server and designate a random emoji to the client based on their type
    def initialize_client(self, request, context):
        emoji = ':skull:'
        
        with self._key_lock:
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


    def check_board(self, request, context):
        # Initial bare logic
        # TODO: Check for Pokemon and go to them
        # TODO: Branch off for trainer and pokemon logic
        with self._key_lock:
            valid_locations = []

            current_x = int(request.x)
            current_y = int(request.y)

            for i in range (-1, 2):
                for j in range(-1, 2):
                    if (current_x + i) >= 0 and (current_x + i) < self.board_size:
                        if (current_y + j) >= 0 and (current_y + j) < self.board_size:
                            valid_locations.append(pokemonou_pb2.Location(x=current_x + i, y=current_y + j)) 

            return pokemonou_pb2.LocationList(locs=valid_locations)


    def move(self, request, context):

        with self._key_lock:
            # Check that the move is valid
            x = request.xLocation
            y = request.yLocation

            if x < 0 or x >= self.board_size:
                return pokemonou_pb2.Location(x=-1, y=request.yLocation)
            
            if y < 0 or y >= self.board_size:
                return pokemonou_pb2.Location(x=request.xLocation, y=-1)

            # Adjust the client's location and add to the path dictionaries
            # Also add to the action list
            if request.type == "trainer":
                self.trainers[request.name] = (x, y)
                self.trainer_paths[request.name].append((x, y))
            elif request.type == "pokemon":
                self.pokemon[request.name] = (x, y)
                self.pokemon_paths[request.name].append((x, y))

            self.action_list.append(request.action_msg)

            return pokemonou_pb2.Location(x=request.xLocation, y=request.yLocation)

    def show_path(self, request, context):

        # Print out the requested client's path
        if request.type == "trainer":
            path = self.trainer_paths[request.name]
        elif request.type == "pokemon":
            path = self.pokemon_paths[request.name]

        loc_list = []
        for loc in path:
            print(str(loc[0]) + ", " + str(loc[1]))
            loc_list.append(loc)

        return pokemonou_pb2.LocationList()


    """
    Trainer Services
    """
    def capture(self, request, context):

        with self._key_lock:
            # Check if a pokemon is in the location specified
            x = request.xLocation
            y = request.yLocation

            for pkmn, loc in self.pokemon.items():
                if x == loc[0] and y == loc[1]:
                    # Found the pokemon

                    # Adjust status

                    # Return the pokemon's name
                    return pokemonou_pb2.Name(name=pkmn, type="pokemon")

            # Pokemon was not found - return failure to signify that
            return pokemonou_pb2.Name(name="failure", type="pokemon")

    def show_pokedex(self, request, context):
        # Displays all the pokemon captured by a trainer
        return pokemonou_pb2.Pokedex()


    """
    Pokemon Services
    """
    def show_trainer_info(self, request, context):
        # Displays the trainer's name and information for a pokemon if they are captured
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
                # Check if game is over
                if game.status == "over":
                    # Print a list of all the actions once all Pokemon are captured
                    game.actions()

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
            response = stub.initialize_client(pokemonou_pb2.Name(name=self.name, type='pokemon'))
            self.icon = response.emojiID
            self.x_loc = int(response.xLocation)
            self.y_loc = int(response.yLocation)

            # Move around the board and avoid trainers
            is_game_over = False
            while(not is_game_over):
                
                # Check if captured
                # If so, display trainer information
                
                # Get status from the server on if can move

                # Check if the game is over
                status_res = stub.game_status(pokemonou_pb2.Name(name=self.name, type="pokemon"))
                is_game_over = status_res.status == "over"

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
        self.pokedex = []
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
                action_msgs = []

                # Check if a pokemon is in this space - if so, catch it, otherwise move
                capture_res = stub.capture(pokemonou_pb2.ClientInfo(name=self.name, emojiID=self.icon, xLocation=self.x_loc, yLocation=self.y_loc))
                
                # Check if capture was a success
                if capture_res.name != "failure":
                    # Success -- add the pokemon's name to the pokedex
                    self.pokedex.append(capture_res.name)
                    action_msgs.append(f'{self.name} captured {capture_res.name}')
                else:    
                    # Failure -- did not capture a pokemon
                    # Move by checking the board, then finding suitable location
                    check_res = stub.CheckBoard()
                    valid_locs = check_res.locs

                    # Randomly choose a new location from the valid location list
                    idx = random.randint(len(valid_locs))

                    new_x = (valid_locs[idx])[0]
                    new_y = (valid_locs[idx])[1]

                    move_res = stub.move(pokemonou_pb2.MoveInfo(name=self.name, loc=pokemonou_pb2.Location(x=new_x, y=new_y)))

                    # A -1 returned for x or y will denote an invalid move
                    if move_res.x != -1 and move_res.y != -1:
                        # Add this action to the action messages list
                        action_msg = "Moved to (" + str(new_x) + ", " + str(new_y) + ") from (" + str(self.x_loc) + ", " + str(self.y_loc)
                        action_msgs.append(action_msg)

                        # Adjust x and y locations
                        self.x_loc = move_res.x
                        self.y_loc = move_res.y

                    # Attempt a capture again in the new space after moving
                    capture2_res = stub.capture(pokemonou_pb2.ClientInfo(name=self.name, emoji=self.icon))
                    if capture2_res.name != "failure":
                        self.pokedex.append(capture2_res.name)
                        action_msgs.append(f'{self.name} captured {capture2_res.name}')

                # Ask the server to print the board at the end of every turn
                print_res = stub.show_board(pokemonou_pb2.ActionMsgs(name=self.name, actions=action_msgs))

                # Check the status of the game
                status_res = stub.game_status(pokemonou_pb2.Name(name=self.name, type="trainer"))
                is_game_over = status_res.status == "over"

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
    