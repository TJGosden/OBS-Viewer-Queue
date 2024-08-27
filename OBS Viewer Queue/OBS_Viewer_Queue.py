import os
import re

#Get the file path in which the file "fileName" is stored.
def get_file_path(fileName):
    # Get the current directory (where the script is located)
    script_directory = os.path.dirname(os.path.abspath(__file__))
    # Name of the file you're searching for
    target_file_name = fileName

    # Construct the full path to the target file
    target_file_path = os.path.join(script_directory, target_file_name)
    #Create the folder "obs-countdown" if it doesn't already exist.
    if not os.path.exists(target_file_path):
        print(".txt File not found in the script directory.")
    return target_file_path

def remove_player_from_queue():
    openFile = open(get_file_path('Queue.txt'), "r")
    nextPlayer = openFile.readline()
    openFile.close                          #Need to close and reopen the file since it removes the first 2 lines instead of one later?
    openFile = open(get_file_path('Queue.txt'), "r")
    with openFile as filedata:
            inputFilelines = filedata.readlines()
            lineindex = 1
            with open(get_file_path('Queue.txt'), 'w') as filedata:
                for textline in inputFilelines:
                    if (lineindex != 1):
                        filedata.write(textline)
                    lineindex += 1
            filedata.close()
    openFile.close()
    return nextPlayer

##Check if there is a Player
def select_player(playerNum):
    player = open(get_file_path(playerNum + '.txt'), 'w')
    nextPlayer = remove_player_from_queue()
    player.write(nextPlayer)
    player.close()

def clear_all():
    playerOne = open(get_file_path('Player 1.txt'), 'w')
    playerTwo = open(get_file_path('Player 2.txt'), 'w')
    Queue = open(get_file_path('Queue.txt'), 'w')
    playerOne.close()
    playerTwo.close()
    Queue.close()