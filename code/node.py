from concurrent import futures

import emoji
import logging
import math
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

    def __init__(self, board_size, total_pkmn):

        # Initialize variables
        self.status = "active"

        self.board_size = board_size
        self.game_board = [[":seedling:" for i in range(self.board_size)] for j in range(self.board_size)]

        self.trainers = {}                  # Dict: key = trainer's name (string), value = current location ((int, int) tuple)
        self.trainer_pokedexes = {}         # Dict: key = trainer's name (string), value = list of pokemon ([string])
        self.trainer_paths = {}             # Dict: key = trainer's name (string), value = list of locations visited ([(int, int)])
        self.people_emojis = []             # List of emojis for trainers to use ([string]) - https://emojipedia.org/people/ 
        self.used_people_emojis = []        # List of booleans corresponding to people_emojis that has True if that emoji has been used

        self.num_pkmn = total_pkmn          # The int number of total pokemon that will be added
                                            # Used so game cannot end prematurely before all Pokemon are added
        self.pokemon = {}                   # Dict: key = pokemon's name (string), value = current location ((int, int) tuple)
        self.pokemon_paths = {}             # Dict: key = pokemon's name (string), value = list of locations visited ([(int, int)])
        self.animal_emojis = []             # List of emojis for pokemon to use ([string]) - https://emojipedia.org/nature/
        self.used_animal_emojis = []        # List of booleans telling which animal emojis have been used

        self.action_list = []               # A list of all the actions that clients have taken in the game so far
        self.current_actions = []           # A list of the current actions that have not been output yet

        self.last_output_len = 0

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
    Server Functions
    """

    # Prints all of the actions that every client has taken so far
    def actions(self):
        for action in self.action_list:
            print(action)
        return

    # Prints the current state of the board, and all the actions that have been taken in this turn
    def print_board(self):

        # Clear the screen
        LINE_UP = '\033[1A'
        LINE_CLEAR = '\x1b[2K'
        for i in range(self.last_output_len):
            print(LINE_UP, end=LINE_CLEAR)

        # Print the actual board
        for i in range(self.board_size):
            for j in range(self.board_size):    
                print('|' + emoji.emojize(self.game_board[i][j].strip()) + ' ', end='')

                if j == self.board_size-1:
                    print('|', end='')

            # Newline
            print()

        # Print all of the action messages for this turn
        for msg in self.current_actions:
            print(msg)

        self.last_output_len = self.board_size + 4 * len(self.current_actions) + 3

        self.current_actions = []

        return



    """
    Client Functions
    """

    # Checks if the game is over by checking if all the pokemon are captured
    def game_status(self, request, context):
        # Iterate over all pokemon and check if all are captured
        catch_count = 0
        for pkmn, _ in self.pokemon.items():
            for trainer, dex in self.trainer_pokedexes.items():
                if pkmn in dex:
                    catch_count += 1

        if catch_count == len(self.pokemon) and catch_count == self.num_pkmn:
            self.game_status = "over"
        else:
            self.game_status = "active"

        return pokemonou_pb2.GameStatus(status=self.status)


    # Registers a client with the server, and allocates them an emoji for their icon, and a location on the board
    def initialize_client(self, request, context):

        _emoji = ":skull:"

        with self._key_lock:
            if request.type == "trainer":
                # Add the trainer to the server if they are not already registered as a key in self.trainers dict
                if request.name not in self.trainers:

                    # Choose a random emoji from the people emoji list, and check if it has been used
                    emoji_idx = random.randint(0, len(self.people_emojis) - 1)
                    while self.used_people_emojis[emoji_idx] == True:
                        emoji_idx = random.randint(0, len(self.people_emojis) - 1)

                    # Found an emoji - update the used people emoji list and send to the client
                    self.used_people_emojis[emoji_idx] = True
                    _emoji = self.people_emojis[emoji_idx]

                    self.current_actions.append(request.name + " connected to the server as " + emoji.emojize(_emoji.strip()))
                else:
                    # If client has already connected, return skull emoji to denote that
                    return pokemonou_pb2.ClientInfo(name=request.name, emojiID=_emoji, xLocation=-1, yLocation=-1)

            elif request.type == "pokemon":
                # Add the pokemon to the server if they are not already registered as a key in self.pokemon dict
                if request.name not in self.pokemon:

                    # Choose a random emoji from animal emoji list, and check if it has been used
                    emoji_idx = random.randint(0, len(self.animal_emojis) - 1)
                    while self.used_animal_emojis[emoji_idx] == True:
                        emoji_idx = random.randint(0, len(self.animal_emojis) - 1)
                    
                    # Found an emoji - update the used animal list
                    self.used_animal_emojis[emoji_idx] = True
                    _emoji = self.animal_emojis[emoji_idx]

                    self.current_actions.append(request.name + " connected to the server as " + emoji.emojize(_emoji.strip()))
                else:
                    return pokemonou_pb2.ClientInfo(name=request.name, emojiID=_emoji, xLocation=-1, yLocation=-1)

            # Assign the client a spot on the board as well
            # Unoccupied spots are denoted by ":seedling:"
            x = random.randint(0, self.board_size - 1)
            y = random.randint(0, self.board_size - 1)

            # If the spot is preoccupied, keep trying
            while self.game_board[x][y] != ":seedling:":
                x = random.randint(0, self.board_size - 1)
                y = random.randint(0, self.board_size - 1)  

            # Put the emoji in the spot
            self.game_board[x][y] = _emoji

            # Add the client and their location to the server's dictionaries and paths
            if request.type == "trainer":
                self.trainers[request.name] = (x, y)
                self.trainer_paths[request.name] = [(x, y)]
                self.trainer_pokedexes[request.name] = []
            elif request.type == "pokemon":
                self.pokemon[request.name] = (x, y)
                self.pokemon_paths[request.name] = [(x, y)]

        return pokemonou_pb2.ClientInfo(name=request.name, emojiID=_emoji, xLocation=x, yLocation=y)


    # Returns the location of the nearest client of the opposite type to the client
    def check_board(self, request, context):

        with self._key_lock:
            current_x = request.xLocation
            current_y = request.yLocation

            type = re.sub(r'[0-9]', '', request.name)
            nx = -1
            ny = -1
            nearest_dist = self.board_size * 2

            if type == "trainer":

                # Check for the case where no pokemon are around
                if len(self.pokemon) < 1:
                    return pokemonou_pb2.Location(x=current_x, y=current_y)

                for pokemon, p_loc in self.pokemon.items():
                    dist = math.sqrt((current_x - p_loc[0])**2 + (current_y - p_loc[1])**2)
                    if dist < nearest_dist:
                        nearest_dist = dist
                        nx = p_loc[0]
                        ny = p_loc[1]

            elif type == "pokemon":

                # Check for the case where no trainers are around
                if len(self.trainers) < 1:
                    return pokemonou_pb2.Location(x=current_x, y=current_y)

                for trainer, t_loc in self.trainers.items():
                    dist = math.sqrt((current_x - t_loc[0])**2 + (current_y - t_loc[1])**2)
                    if dist < nearest_dist:
                        nearest_dist = dist
                        nx = t_loc[0]
                        ny = t_loc[1]

            return pokemonou_pb2.Location(x=nx, y=ny)


    # Checks that a move is legal, then moves the client to the specified spot
    def move(self, request, context):
        
        with self._key_lock:

            # Check that the move is valid
            nx = request.newloc.x
            ny = request.newloc.y

            if nx < 0:
                nx = 0
            if nx > self.board_size - 1:
                nx = self.board_size - 1

            if ny < 0:
                ny = 0
            if ny > self.board_size - 1:
                ny = self.board_size - 1

            # Adjust the client's location and add to the path directories
            if request.name.type == "trainer":
                # Make sure there are no other trainers in this spot
                if self.game_board[nx][ny] not in self.people_emojis:
                    self.trainers[request.name.name] = (nx, ny)
                    self.trainer_paths[request.name.name].append((nx, ny))
                else:
                    return pokemonou_pb2.Location(x=request.oldloc.x, y=request.oldloc.y)

            elif request.name.type == "pokemon":
                # Make sure there are no other pokemon in this spot
                if self.game_board[nx][ny] not in self.animal_emojis:
                    self.pokemon[request.name.name] = (nx, ny)
                    self.pokemon_paths[request.name.name].append((nx, ny))
                else:
                    return pokemonou_pb2.Location(x=request.oldloc.x, y=request.oldloc.y)

            # Update the game_board to reflect the changes
            self.game_board[request.oldloc.x][request.oldloc.y] = ":seedling:"
            self.game_board[nx][ny] = request.emojiID

            # Add the action message to the lists
            action_msg = f"{request.name.name} ({emoji.emojize(request.emojiID.strip())}) moved to ({nx}, {ny}) from ({request.oldloc.x}, {request.oldloc.y})"
            self.action_list.append(action_msg)
            self.current_actions.append(action_msg)

            return pokemonou_pb2.Location(x=nx, y=ny)
    
    # Will display the entire path that a client has taken throughout the game
    def show_path(self, request, context):

        type = re.sub(r'[0-9]', '', request.name)

        path_str = f"{request.name}'s path: "
        if type == "trainer":
            
            for location in self.trainer_paths[request.name]:
                path_str += f"({location[0]}, {location[1]}) -> "
            path_str += "end"

        elif type == "pokemon":
            for location in self.pokemon_paths[request.name]:
                path_str += f"({location[0]}, {location[1]}) -> "
            path_str += "end"

        # Add the path string to the current actions to be performed
        self.current_actions.append(path_str)

        return pokemonou_pb2.Name(name=request.name, type=type)


    """
    Trainer Functions
    """
    
    # If a pokemon is in the space the trainer is in, then the trainer has captured it and it will be removed from the board
    def capture(self, request, context):
        with self._key_lock:
            x = request.xLocation
            y = request.yLocation

            for pokemon, loc in self.pokemon.items():
                if x == loc[0] and y == loc[1]:
                    # Found a pokemon - add it to the pokedex, and remove from pokemon dict
                    self.trainer_pokedexes[request.name].append(pokemon)
                    del self.pokemon[pokemon]

                    # Add to the output list
                    self.current_actions.append(f"{request.name} ({emoji.emojize(request.emojiID.strip())}) has captured {pokemon}")

                    # Return the name of the pokemon
                    return pokemonou_pb2.Name(name=pokemon, type="pokemon")

            return pokemonou_pb2.Name(name="failure", type="pokemon")

    # Displays the entire pokedex of a trainer with all the pokemon they have caught
    def show_pokedex(self, request, context):

        # Check if the Trainer's dex is empty, if not append each pokemon to a list to be output
        pkdx_str = f"{request.name}'s Pokedex: "
        if len(self.trainer_pokedexes[request.name]) == 0:
            pkdx_str += "Empty"
        else:
            for pkmn in self.trainer_pokedexes[request.name]:
                pkdx_str += f"{pkmn} - "

        self.current_actions.append(pkdx_str)

        return pokemonou_pb2.Name(name=request.name, type="trainer")


    """
    Pokemon Functions
    """

    # If a pokemon is captured, this will let them know
    def captured(self, request, context):
        # Check if this pokemon exists in any of the trainers pokedexes
        for trainer, pokedex in self.trainer_pokedexes.items():
            if request.name in pokedex:
                return pokemonou_pb2.Name(name=trainer, type="trainer")

        # Return the name as "free" if it is not captured
        return pokemonou_pb2.Name(name="free", type="")


    # Displays the trainer's name and emoji of the pokemon
    def show_trainer_info(self, request, context):

        for trainer, _ in self.trainers.items():
            pokedex = self.trainer_pokedexes[trainer]
            if request.name in pokedex:
                self.current_actions.append(f"{trainer} owns {request.name}")
                return pokemonou_pb2.Name(name=trainer, type="trainer")



"""
The Server Class

Handles input from both Trainers and Pokemon clients, and manages the grid
"""
class Server():
    
    def serve(self, boardsize, totalpkmn):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=boardsize**2))
        game = PokemonOUGame(board_size=boardsize, total_pkmn=totalpkmn)
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

                    # Stop the server
                    return

                # Print the board every second, with the list of actions that have occurred
                game.print_board()

                time.sleep(1)

        except KeyboardInterrupt:
            server.stop(0)

        return



"""
The Pokemon Class
    - A Pokemon will attempt to evade capture by running away from the nearest trainer
"""
class Pokemon():

    def __init__(self, my_name):
        # Initialize variables
        self.name = my_name
        self.icon = ''
        self.x_loc = -1
        self.y_loc = -1
        return

    # The Pokemon's gameplay loop:
    #   If not captured, then run directly away from the nearest trainer until reaching a border
    def run(self):
        with grpc.insecure_channel("server:50051") as channel:
            stub = pokemonou_pb2_grpc.PokemonOUStub(channel)

            # Initialize this Pokemon with the server, and get an emoji designation and location
            response = stub.initialize_client(pokemonou_pb2.Name(name=self.name, type="pokemon"))
            self.icon = response.emojiID
            self.x_loc = int(response.xLocation)
            self.y_loc = int(response.yLocation)

            # Run away from Trainers and evade capture
            is_game_over = False
            while(not is_game_over):

                # Check if this pokemon was captured
                # Server returning the name 'free' denotes that the pokemon is free
                captured_res = stub.captured(pokemonou_pb2.Name(name=self.name, type="pokemon"))
                if captured_res.name != "free":

                    # The pokemon is captured - show its trainer info and its path, then exit
                    trainer_res = stub.show_trainer_info(pokemonou_pb2.Name(name=self.name, type="trainer"))
                    path_res = stub.show_path(pokemonou_pb2.Name(name=self.name, type="pokemon"))
                    return
                
                # Check where the nearest trainer is and move 1 spot in the opposite direction
                check_res = stub.check_board(pokemonou_pb2.ClientInfo(name=self.name, emojiID=self.icon, xLocation=self.x_loc, yLocation=self.y_loc))

                dx = 0
                dy = 0
                nx = check_res.x
                ny = check_res.y

                if nx < self.x_loc:
                    dx = 1
                elif nx > self.x_loc:
                    dx = -1

                if ny < self.y_loc:
                    dy = 1
                elif ny > self.y_loc:
                    dy = -1

                move_res = stub.move(pokemonou_pb2.MoveInfo(name=pokemonou_pb2.Name(name=self.name, type="pokemon"), 
                                                            emojiID=self.icon, 
                                                            oldloc=pokemonou_pb2.Location(x=self.x_loc, y=self.y_loc), 
                                                            newloc=pokemonou_pb2.Location(x=self.x_loc+dx, y=self.y_loc+dy)))

                # Update the x and y coords
                self.x_loc = move_res.x
                self.y_loc = move_res.y

                # Check the status of the game
                status_res = stub.game_status(pokemonou_pb2.Name(name=self.name, type="trainer"))
                is_game_over = status_res.status == "over"

                time.sleep(1)

        return


"""
The Trainer Class
    - A Trainer will attempt to capture the nearest pokemon
"""
class Trainer():

    def __init__(self, my_name):
        # Initialize variables
        self.name = my_name
        self.icon = ''
        self.x_loc = -1
        self.y_loc = -1
        self.pokedex = []
        return

    # The Trainer gameplay loop:
    #   If a pokemon is at the current spot, capture it, if not move towards the nearest one and attempt one more capture
    def run(self):
        with grpc.insecure_channel("server:50051") as channel:
            stub = pokemonou_pb2_grpc.PokemonOUStub(channel)

            # Initialize this Pokemon with the server, and get an emoji designation and location
            response = stub.initialize_client(pokemonou_pb2.Name(name=self.name, type="trainer"))
            self.icon = response.emojiID
            self.x_loc = int(response.xLocation)
            self.y_loc = int(response.yLocation)

            # Move and attempt to capture Pokemon
            is_game_over = False
            while(not is_game_over):

                # Check if there is a Pokemon in this spot
                capture_res = stub.capture(pokemonou_pb2.ClientInfo(name=self.name, emojiID=self.icon, xLocation=self.x_loc, yLocation=self.y_loc))
                if capture_res.name == "failure":
                    # No Pokemon was caught - move towards the nearest pokemon and attempt a capture again
                    check_res = stub.check_board(pokemonou_pb2.ClientInfo(name=self.name, emojiID=self.icon, xLocation=self.x_loc, yLocation=self.y_loc))

                    dx = 0
                    dy = 0

                    nx = check_res.x
                    ny = check_res.y

                    if nx < self.x_loc:
                        dx = -1
                    elif nx > self.x_loc:
                        dx = 1

                    if ny < self.y_loc:
                        dy = -1
                    elif ny > self.y_loc:
                        dy = 1

                    move_res = stub.move(pokemonou_pb2.MoveInfo(name=pokemonou_pb2.Name(name=self.name, type="trainer"), 
                                                                emojiID=self.icon, 
                                                                oldloc=pokemonou_pb2.Location(x=self.x_loc, y=self.y_loc), 
                                                                newloc=pokemonou_pb2.Location(x=self.x_loc+dx, y=self.y_loc+dy)))

                    # Update the x and y coords
                    self.x_loc = move_res.x
                    self.y_loc = move_res.y

                    # Check if the Trainer can catch a Pokemon now
                    capture2_res = stub.capture(pokemonou_pb2.ClientInfo(name=self.name, emojiID=self.icon, xLocation=self.x_loc, yLocation=self.y_loc))


                # Check the status of the game
                status_res = stub.game_status(pokemonou_pb2.Name(name=self.name, type="trainer"))
                is_game_over = status_res.status == "over"

                time.sleep(1)

            # Once the game is over, output this trainer's pokedex
            pokedex_res = stub.show_pokedex(pokemonou_pb2.Name(name=self.name, type="trainer"))

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
    num_pkmn = int(sys.argv[2])

    # Determine which class the program is
    hostname = re.sub(r'[0-9]', '', socket.gethostname())

    if hostname == 'server':
        server = Server()
        server.serve(boardsize=boardsz, totalpkmn=num_pkmn)
    elif hostname == 'trainer':
        trainer = Trainer(my_name=socket.gethostname())
        trainer.run()
    elif hostname == 'pokemon':
        pokemon = Pokemon(my_name=socket.gethostname())
        pokemon.run()
    