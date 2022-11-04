
def getInputParameters():

    gridsize = int(input('Size of grid: '))
    numT = int(input('Number of Trainers: '))
    numP = int(input('Number of Pokemon: '))
    return gridsize, numT, numP

def generateDockerComposeYML(numTrainers, numPokemon):

    version='version: \'3.7\''
    header='service:\n'

    dcfile=open('docker-compose.yml', 'w')

    # Create the server machine
    serverLines=['\tserver:', '\t\tbuild: .', '\t\thostname: server', '\t\tcontainer_name: Server', '\t\tnetworks:', '\t\t\t - default']
    dcfile.writelines(serverLines)

    # Create a new machine for each trainer
    for i in range(0, numTrainers):
        trainerLines=[]
        dcfile.writelines()

    # Create a new machine for each pokemon
    for i in range(0, numPokemon):
        pokemonLines=[]
        dcfile.writelines()

    # Add the network code at the bottom
    networkLines=['networks', '\tdefault:', '\t\tdriver: bridge']
    dcfile.writelines(networkLines)

    dcfile.close()

    return

if __name__ == '__main__':
    # Get the input parameters
    gridsize, numTrainers, numPokemon = getInputParameters()

    # Create the docker-compose file based off of these parameters
    generateDockerComposeYML(numTrainers, numPokemon)