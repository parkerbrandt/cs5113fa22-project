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
