# Pokemon OU - CS 5113 Fall 2022
## By: Parker Brandt (ID: 113521131) 


### The Project

PokemonOU is a game inspired by the Pokemon franchise by Nintendo and Game Freak. Instead of having a user control a "Trainer" and run around attempting to capture Pokemon, machines are created instead to emulate a certain number of Trainers and Pokemon. The Pokemon run away from the Trainers, and attempt to avoid capture. The Trainers run towards the Pokemon, and if they are in the same spot as a Pokemon on the game board, they will have captured the Pokemon, which takes them off the board, and puts them in the Trainer's pokedex. Trainers and Pokemon are both represented by emojis. Trainers have "people" emojis, while Pokemon have "animal" emojis. The game ends once all the Pokemon have been captured by the Trainers at which point the Server will then output all of the actions that have occurred during the game.


### Demonstration

![Demo](media/parkerbrandt-cs5113fa22finalpres.mp4)


### Project Specific Parameters

Minimum Size of the Board = 20x20

Chosen Size of the Board = 25x25

Number of Pokemon (P) and Trainers (T)
    = 10 + num(paper D) + len('Parker')
    = 10 + 4 + 6
    = 20


### How to Run

First, navigate within the code/ directory by doing

`cd code/`

Then, to run PokemonOU, the first step is to run 'docker-generate.py' by issuing the command

`python docker-generate.py up`

This will prompt the user for information on the size of the grid, the number of trainers to create, and the number of pokemon to create. Once this is filled out, the script will automatically rewrite and adjust 'Dockerfile' and 'docker-compose.yml' in order to meet the specified requirements the user inputted.

NOTE: If 'up' is not specified int the above command, the code will not automatically run, and the script will only adjust 'Dockerfile' and 'docker-compose.yml'. If 'up' is not entered as a command-line argument, then also run.

`docker-compose up`


### How it Works

#### docker-generate.py

As mentioned in the "How to Run" section, 'docker-generate.py' asks the user for the size of the game board to create, the number of trainers, and the number of pokemon to create as well. Once this is done, the script rewrites 'docker-compose.yml' and 'Dockerfile' to account for the correct number of Trainers and Pokemon. 


#### node.py

This file holds all the actual logic for the machines that will be run. Houses classes for running the Server, Trainer, and Pokemon machines. When each machine runs the code, they will initially branch into their respective machine by checking what the hostname of the machine is. Once the code branches, it will perform one of three game loops:

##### Server class
    - The Server class creates the PokemonOUGame object, which handles receiving and responding to Client RPC requests, and handles logic.
    - PokemonOUGame Functions:</br>
        - actions() : (Only accessible by Server class) Will print out a list of every action that has taken place during the game.</br>
        - print_board() : (Only accessible by Server class) Will print out the game board in its current state, including using emojis as placeholders for Trainers and Pokemon on the board. Will erase the previous board's output to give the illusion of movement. Will also output action messages as they happen in the game. This function is called once per second by the server.</br>
        - game_status() : Checks if all pokemon have been captured, and if so, will change the game status to be "over"</br>
        - initialize_client() : Called by a Client when first launched, the Server will register the name and type (Trainer or Pokemon) within the Server, and then the server will give the client a location on the board, and an emoji</br>
        - check_board() : Returns the location of the nearest client of the other type, so a Pokemon can either run away, or a Trainer can run towards that client</br>
        - move() : A client will enter a location to move to, this function will ensure that the move is not an illegal move, and then will move the client to a legal spot, and show it on the board</br>
        - show_path() : Displays the entire path that a Trainer or Pokemon has taken from spawn to end of game</br>
        - capture() : Checks if a Pokemon is in the same spot as a Trainer, and if so, will capture it and remove it from the board</br>
        - show_pokedex() : Will display the pokemon that a trainer has caught over the course of the game</br>
        - captured() : Tells a Pokemon if they have been caught or not, and if so, they will end their machine
        - show_trainer_info() : Once a Pokemon is captured, will display the information of the Trainer that has captured them

#### Client classes
    - The Pokemon Class</br>
        - While the Pokemon is not captured, it will get the location of the nearest Trainer, then run in the opposite direction by one unit.


    - The Trainer Class</br>
        - While the game is not over, the Trainer will check if there is a Pokemon in the spot they are currently in, and if so, they capture it, otherwise they will move and attempt a capture again.

### File Structure

Base Level:</br>
    - README.md ->      This document.</br>
    - COLLABORATORS ->  Content used for help and information in the process of developing PokemonOU.</br>
</br>
code/:</br>
    - Dockerfile ->             The file that details what information must be loaded onto each machine instance.</br>
    - docker-compose.yml ->     The file that details each machine to be created with Docker, and its associated name.</br>
    - docker-generate.py ->     The Python file that modifies the docker files according to user input.</br>
    - node.py ->                The Python file that runs each machines' actual code and behavior.</br>
    - pokemonou.proto ->        The Protofile detailing gRPC message types and functions to be implemented.</br>
    - animal_emoji_list.txt ->  The list of valid animal emojis for Pokemon machines to use for their icon.</br>
    - people_emoji_list.txt ->  The list of valid people emojis for Trainer machines to use for their icon.</br>
    - requirements.txt ->       Any extra requirements that need to be downloaded when creating instances.</br>
</br>
media/:</br>
    - grid.gif ->       The GIF used for submission for milestone 3 displaying that the board was printing at the time of submission.</br>
    - README_old.md ->  The content found in the README previous to this version. Contains information about development schedule, protofile functions, and how emojis were chosen.</br>