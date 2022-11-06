"""
Gets the input values from the user
"""
def getInputParameters():
    gridsize = int(input('Size of grid: '))
    numT = int(input('Number of Trainers: '))
    numP = int(input('Number of Pokemon: '))
    return gridsize, numT, numP


"""
Generates a docker-compose.yml file

Creates 1 server machine, numT trainers, and numP pokemon with their own containers
Also creates a default network that each container can use 
"""
def generateDockerComposeYML(numT, numP):

    version='version: \'3.7\'\n'
    header='service:\n'

    with open('docker-compose.yml', 'w') as dcfile:
        # Write the necessary header information
        dcfile.write(version)
        dcfile.write(header)
        
        # Create the server machine
        serverLines=['  server:', '    build: .', '    hostname: server', '    container_name: Server', '    networks:', '       - default']
        for line in serverLines:
            dcfile.write(line + '\n')

        # Create a new machine for each trainer
        for i in range(0, numT):
            trainerLines=['  client' + str(i) +':', '    build: .', '    hostname: trainer' + str(i), '    container_name: Trainer' + str(i), '    networks:', '       - default']
            for line in trainerLines:
                dcfile.write(line + '\n')

        # Create a new machine for each pokemon
        for i in range(0, numP):
            pokemonLines=['  client' + str(i + numTrainers) +':', '    build: .', '    hostname: pokemon' + str(i), '    container_name: Pokemon' + str(i), '    networks:', '       - default']
            for line in pokemonLines:
                dcfile.write(line + '\n')

        # Add the network code at the bottom
        networkLines=['networks:', '  default:', '    driver: bridge']
        for line in networkLines:
            dcfile.write(line + '\n')

    return


"""
Start of Program Logic
"""
if __name__ == '__main__':
    # Get the input parameters
    gridsize, numTrainers, numPokemon = getInputParameters()

    # Create the docker-compose file based off of these parameters
    generateDockerComposeYML(numTrainers, numPokemon)

    # Call the main node.py file
    exec(open('node.py').read())