## Development Schedule

10/28 - 10/30
    - Create initial protofile
    - Modify Dockerfile and docker-compose.yml from assignment 1 for this project
    - Write outline of some code in node.py

11/01
    - Test that all preliminary files (Dockerfile, docker-compose.yml, and protofile) all build correctly with some simple code
    - Start filling out logic of RPC functions in node.py

#### 11/03 - Protos and Interface Design Due

11/04 - 11/06
    - Finish logic of RPC functions in node.py
    - Start working on logic in functions and classes of node.py
    - Work on dynamically creating the board and pokemon
        - Work on outputs and emojis for trainers and pokemon

11/11 - 11/13
    - Complete node.py initial logic
    - Start testing on different inputs and ensure that project is functioning

#### 11/17 - First Version Logging Due

11/18 - 11/20
    - Fix any remaining bugs
    - Add more details to project

#### 12/01 - Submission Due



## Emoji Chooser
To initialize the board, I will take in an integer input of N, and using that, the server will create an array of size N x N. After this, whenever a Pokemon or Trainer is created, they will send a message to the server including their name and whether they are a trainer or pokemon. The server will then designate a spot for them on the board if it is not full by choosing two random numbers to correspond to coordinates.

I am currently still figuring out how to fully accomplish this, but I think in the docker-compose file, I will have it create a Server, 1 Trainer, and 1 Pokemon, and then based off how many trainers and pokemon are wanted, I will look at trying to have those machines create new ones.


## Protofile Functions

In the proto file, I separate the functions in the PokemonOU service by which machine will be calling them.


First are the services that the Server will be calling:
    - rpc Captured(Name) returns (Pokemon) {}
        This function has the server notify a Pokemon that they are captured. The server will input a name that will be checked, and then it will return the full Pokemon's information it can use to talk to the Pokemon.

    - rpc Moves() returns (MoveList) {}
        This function prints the complete list of moves that the Trainers and Pokemon have performed. This will include movement, captures, and any other actions that may be taken. The output MoveList will have an action that was performed, the location it was performed in, and the entity that performed that action.

    - rpc Board() returns (Board) {}
        This function simply will print an NxN representation of the board state. It will use each Trainer and Pokemon's emojis in the square in which they are residing, and any empty squares will be left empty.


Next, are the functions that both Trainers and Pokemon will be calling:
    - rpc Initialize(Name) returns (Emoji) {}
        This function is called whenever a Trainer machine or Pokemon machine is first created. The node will send their name and type to the server, and the server will then register the Trainer/Pokemon internally, and return an available emoji for them to use, which the machine will then keep track of.
    
    - rpc CheckBoard(Location) returns (LocationList) {}
        This function will have the entity input their location to the function, and it will then receive a list of locations back that are available for them to move to. Locations have both an integer x and y coordinate.

    - rpc Move(Move) returns (Move) {}
        This function will have the Trainer or Pokemon input the move they want to perform, and then the server will check if it can be executed. This could be a location move, or another action such as the Trainer capturing a Pokemon. The function will return the move data with a status to denote if it completed or not.

    - rpc ShowPath(Name) returns (LocationList) {}
        This function will have a trainer or pokemon input their "name" (NOTE: This may be changed to some sort of identifier later - maybe a hash of their emoji's unicode character like with Chord), and then the server will return a list of locations (x and y) of where they have been.


Next, are the functions that the Trainers will be calling
    - rpc Capture(Name) returns (Pokemon)
        This function will have the Trainer give the name or emoji identification of a Pokemon, then the Server will check if that Pokemon is "catchable", and will return the Pokemon's information and the Trainer will be able to check by their status if they were caught or not.

    - rpc ShowPokedex(Name) returns (Pokedex) {}
        This function has a Trainer input their name, and if they have caught any Pokemon, then it will also display all the pokemon that they have caught.


Lastly, are the functions that only the Pokemon will be calling
    - rpc ShowTrainerInfo(Name) returns (Trainer) {}
        This function takes the name of a Pokemon, then finds the designated trainer for that Pokemon, if it has one. It will return a Trainer object, but if the Pokemon has no trainer, the name will be "empty"


I expect once I start fully implementing the project in Python, I will find that there are more functions I will need to add, but these are the basic ones I know I will need.