# Pokemon OU - CS 5113 Fall 2022
## By: Parker Brandt (ID: 113521131) 


### The Project

PokemonOU is a game inspired by the Pokemon franchise by Nintendo and Game Freak. Instead of having a user control a "Trainer" and run around attempting to capture Pokemon, machines are created instead to 


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

As mentioned in the "How to Run" section, 'docker-generate.py' asks the user for the size of the game board to create, the number of trainers, and the number of pokemon to create as well. Once this is done, the script rewrites 'docker-compose.yml'


#### node.py

This file 


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