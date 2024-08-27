from msilib.schema import PublishComponent
import obspython as obs
import os
import Hotkeys_Queue
import OBS_Viewer_Queue as vq
import Twitch_Connect as tc


########### VARIABLES ############

class Buttons:
    def __init__(self):
        self.playerOneCount = 0
        self.playerTwoCount = 0
        self.settings = obs.obs_data_create()
        self.maxGames = obs.obs_data_get_int(self.settings, "slider")
        self.joinQueue = "Type !join to enter queue"
        self.sourceOne = ""
        self.sourceTwo = ""
        self.sourceNext = ""
        self.sourceAlert = ""
        self.joinCode = ""
        self.noCode = "Give me a sec while I make the Arena."
        self.hide = True

b = Buttons()
h1 = Hotkeys_Queue.h()
h2 = Hotkeys_Queue.h()
h3 = Hotkeys_Queue.h()
h4 = Hotkeys_Queue.h()
h5 = Hotkeys_Queue.h()
h6 = Hotkeys_Queue.h()


########### QUEUE BUTTONS ############

def playerOne_pressed(props, prop):
    #Check if a new player needs to be selected
    b.playerOneCount = queue_player(props, prop, b.playerOneCount, "Player 1", b.sourceOne)

def playerTwo_pressed(props, prop):
    #Check if a new player needs to be selected
    b.playerTwoCount = queue_player(props, prop, b.playerTwoCount, "Player 2", b.sourceTwo)
    
#Function to cycle in the next player and update their count
def queue_player(props, prop, playerCount, playerNum, sourceName):
    if playerNum == "Player 1":
        p = "P1: "
    else:
        p = "P2: "

    if playerCount >= b.maxGames or os.stat(vq.get_file_path(playerNum + ".txt")).st_size == 0:            

        #Check if the queue is empty
        if os.stat(vq.get_file_path("Queue.txt")).st_size == 0:
            vq.select_player(playerNum) 
            text = p + b.joinQueue
            set_text(text, sourceName)
            print("The Queue is Empty.")
        else:
            vq.select_player(playerNum)   
            #Get Name of New Player
            openPlayer = open(vq.get_file_path(playerNum + '.txt'), 'r')
            player = openPlayer.readline()
            openPlayer.close()

            #Remove "\n" from end of string from file
            player = player.rstrip()
            player = player.replace(",", "", len(player))

            if b.joinCode:
                send_chat_message("@" + player + " You're Up! The Code is " + b.joinCode)
            else:
                send_chat_message("@" + player + ", " + b.noCode)

            print(p + player + ": 0")
            text = p + player + ": 0"
            playerCount = 0
            set_text(text, sourceName)

            #cycle "next player"
            nextPlayer_pressed(props, prop)
            
            #Play Alert
            sourceAlert = obs.obs_get_source_by_name(b.sourceAlert)
            settings = obs.obs_data_create()
            #Hide then show the source to restart video
            obs.obs_source_set_enabled(sourceAlert, False)
            obs.obs_source_update(sourceAlert, settings)
            obs.obs_source_set_enabled(sourceAlert, True)
            obs.obs_source_update(sourceAlert, settings)
            obs.obs_source_release(sourceAlert)

    #Increase the game count
    else:
        playerCount += 1
        openPlayer = open(vq.get_file_path(playerNum + '.txt'), 'r')
        player = openPlayer.readline()
        #Remove "\n" and "," from end of string from file
        player = player.rstrip()
        player = player.replace(",", "", len(player))
        #playerOne = playerOne.replace(",", "", len(playerOne))
        print(p + player + " : " + str(playerCount))
        text = p + player + ": " + str(playerCount)
        openPlayer.close()
        set_text(text, sourceName)

    return playerCount

#Sets a third text source to show if there is someone waiting in the queue
def nextPlayer_pressed(props, prop):
    #send_chat_message("It's a me")
    #Update the Player sources if empty and someone has joined the queue
    if os.stat(vq.get_file_path("Player 1.txt")).st_size == 0:
        playerOne_pressed(props, prop)
    elif os.stat(vq.get_file_path("Player 2.txt")).st_size == 0:
        playerTwo_pressed(props, prop)
    #Update the third text source when a new player is moved out of the queue
    elif os.stat(vq.get_file_path("Queue.txt")).st_size != 0:
        openQueue = open(vq.get_file_path('Queue.txt'), 'r')
        nextPlayer = openQueue.readline()
        nextPlayer = nextPlayer.rstrip()
        nextPlayer = nextPlayer.replace (",", "", len(nextPlayer))
        text = "Next: " + nextPlayer
        set_text(text, b.sourceNext)
        openQueue.close()
    else:
        #No players in queue
        text = "Next: !Join"
        set_text(text, b.sourceNext)

def post_code(props, prop):
    if b.joinCode:
        send_chat_message("The Arena Code is " + b.joinCode)
    else:
        print("There is no Arena Code")


########### QUEUE FUNCTIONS ############


#Used only as a Hotkey when someone uses the chat command to enter the queue
def player_waiting():
    #Check if a player is waiting in the queue
    if os.stat(vq.get_file_path("Player 1.txt")).st_size != 0 and os.stat(vq.get_file_path("Player 2.txt")).st_size != 0 and os.stat(vq.get_file_path("Queue.txt")).st_size != 0:
        send_chat_message("You have Joined the Queue. Please wait until it is your turn to be given the Arena ID.")

#Sets the text for a given source in obs
def set_text(text, sourceName):
    #Set a text source with new text
    source = obs.obs_get_source_by_name(sourceName)
    settings = obs.obs_data_create()
    obs.obs_data_set_string(settings, "text", str(text))
    obs.obs_source_update(source, settings)

    #Release
    obs.obs_data_release(settings)
    obs.obs_source_release(source)

def send_chat_message(text):
	tc.twitch.chat(text, False)

#Used as a hotkey to reset the count for the number of games played for either player to 0
def reset_count(playerNum, playerCount, sourceName):
    if playerNum == "Player 1":
        p = "P1: "
    else:
        p = "P2: "

    if os.stat(vq.get_file_path(playerNum + ".txt")).st_size != 0:
        playerCount = 0
        openPlayer = open(vq.get_file_path(playerNum + ".txt"), 'r')
        player = openPlayer.readline()
        #Remove "\n" and "," from end of string from file
        player = player.rstrip()
        player = player.replace(",", "", len(player))
        text = p + player + ": " + str(playerCount)
        openPlayer.close()
        set_text(text, sourceName)
    return playerCount


#creates a list of all the source to be selected for text source
def source_list(pList):
    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_id = obs.obs_source_get_unversioned_id(source)
            if (source_id == "text_gdiplus" or source_id == "text_ft2_source"):
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(pList, name, name)
        obs.source_list_release(sources)

#finds sources of type "ffmpeg_source"  (music or video)
def source_list_ffmpeg(pList):
    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_id = obs.obs_source_get_unversioned_id(source)
            if (source_id == "ffmpeg_source" ):
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(pList, name, name)
        obs.source_list_release(sources)



class setup:
    def hide_properties(props, prop, settings):
        setup.hide(props, b.hide)
        return True

    def initialise_hide(props):
        visible = False
        setup.hide(props, visible)

    def hide(props, visible):
        properties = ["channel", "user", "oauth", "sourceOne", "sourceTwo", "sourceNext", "sourceAlert"]
        for i in properties:
            gProp = obs.obs_properties_get(props, i)
            obs.obs_property_set_visible(gProp, visible)
        




########### HOTKEYS ############

def playerOne_hotkey(pressed):
    if pressed:
        playerOne_pressed(pressed, pressed)

def playerTwo_hotkey(pressed):
    if pressed:
        playerTwo_pressed(pressed, pressed)

def nextPlayer_hotkey(pressed):
    if pressed:
        nextPlayer_pressed(pressed, pressed)
        #Removed hotkey for this as it seemd redundant (yet to be tested)
        player_waiting()

def reset_count_one(pressed):
    if pressed:
        b.playerOneCount = reset_count("Player 1", b.playerOneCount, b.sourceOne)

def reset_count_two(pressed):
    if pressed:
        b.playerTwoCount = reset_count("Player 2", b.playerTwoCount, b.sourceTwo)


########### OBS SCRIPT FUNCTIONS ############

#description of programme for OBS
def script_description():
    return """<h1>Viewer Queue</h1> 
    <h3>Allow viewers to enter a queue to join in on the stream, up to two players at a time.</h3> \n
    ---------------------------------------------------------- \n
    <h4>First create and select the text sources you want each player to be displayed</h4> \n
    <h5>You can then set Hotkeys for each button below. "Next" will select and move players 
    along the queue. Then the "Player" buttons will also increase the game count.</h5>"""
    
#Runs when variables are changed by the user in OBS
def script_update(settings):
    #Haven't made a Source selector list for this text, this is just for me,
    #but can be used by creating a text source called "Queue ex".
    b.maxGames = obs.obs_data_get_int(settings, "slider")
    set_text("Join the Queue and Play up to " + str(b.maxGames) + " Games.", "Queue ex")

    #Update name of Text Sources so functions can find them once changed
    b.sourceOne = obs.obs_data_get_string(settings, "sourceOne")
    b.sourceTwo = obs.obs_data_get_string(settings, "sourceTwo")
    b.sourceNext = obs.obs_data_get_string(settings, "sourceNext")
    b.sourceAlert = obs.obs_data_get_string(settings, "sourceAlert")

    b.joinCode = obs.obs_data_get_string(settings, "code")

    b.hide = obs.obs_data_get_bool(settings, "hideBool")

    tc.twitch.channel = obs.obs_data_get_string(settings, "channel").lower()
    tc.twitch.nickname = obs.obs_data_get_string(settings, "user").lower()

    new_oauth = obs.obs_data_get_string(settings, "oauth").lower()
    if new_oauth != tc.twitch.password:
        tc.twitch.disconnect()  # Disconnect old oauth connection, if it exists
        tc.twitch.password = new_oauth

#Runs when the script is initiated 
def script_load(settings):
    h1.htkCopy = Hotkeys_Queue.Hotkey(playerOne_hotkey, settings, "Player 1")
    h2.htkCopy = Hotkeys_Queue.Hotkey(playerTwo_hotkey, settings, "Player 2")
    h3.htkCopy = Hotkeys_Queue.Hotkey(nextPlayer_hotkey, settings, "Next Player")
    h5.htkCopy = Hotkeys_Queue.Hotkey(reset_count_one, settings, "Reset P1 Count")
    h6.htkCopy = Hotkeys_Queue.Hotkey(reset_count_two, settings, "Reset P2 Count")

    #Check for timeout every second
    obs.timer_add(tc.check_connection, 1000)

    obs.obs_data_set_string(settings, "code", "")

def script_unload():
    #Remove timeout timer
	obs.timer_remove(tc.check_connection)  

def script_save(settings):
    h1.htkCopy.save_hotkey()
    h2.htkCopy.save_hotkey()
    h3.htkCopy.save_hotkey()
    h5.htkCopy.save_hotkey()
    h6.htkCopy.save_hotkey()

def script_properties():
    props = obs.obs_properties_create()

    hide = obs.obs_properties_add_bool(props, "hideBool", "Show Inputs")
    obs.obs_property_set_modified_callback(hide, setup.hide_properties)

    #Twitch Channel Identifiers
    obs.obs_properties_add_text(props, "channel", "Channel", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "user", "User", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "oauth", "Oauth", obs.OBS_TEXT_PASSWORD)
    
    #Text Source Lists
    listOne = obs.obs_properties_add_list(props, "sourceOne", "Player One Source", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    listTwo = obs.obs_properties_add_list(props, "sourceTwo", "Player Two Source", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    listNext = obs.obs_properties_add_list(props, "sourceNext", "Next Player Source", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    listAlert = obs.obs_properties_add_list(props, "sourceAlert", "Alert Source (optional)", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    obs.obs_property_set_long_description(listAlert, "Functions with videos or music")
    #Find the list of text Sources
    source_list(listOne)
    source_list(listTwo)
    source_list(listNext)
    source_list_ffmpeg(listAlert)

    #Text Box for Chat Message "send_chat_message()"
    arenaCode = obs.obs_properties_add_text(props, "code", "Arena Code", obs.OBS_TEXT_DEFAULT)
    #obs.obs_propert_set_default_string(arenaCode, "Hi")

    #Slider for number of games
    slider = obs.obs_properties_add_int_slider(props, "slider", "Number of Games", 1, 10, 1)
    obs.obs_property_set_long_description(slider, "Set max number of games until new player")  

    #Create Buttons
    #obs.obs_properties_add_button(props, "playerOneButton", "Player 1", playerOne_pressed)
    #obs.obs_properties_add_button(props, "playerTwoButton", "Player 2", playerTwo_pressed)
    #obs.obs_properties_add_button(props, "nextPlayerButton", "Next", nextPlayer_pressed)
    obs.obs_properties_add_button(props, "code_button", "Post Code", post_code)

    #Slider for number of games
    obs.obs_properties_add_int_slider(props, "slider", "Num of Games", 1, 10, 1)
    
    setup.initialise_hide(props)

    return props

def script_defaults(settings):
    obs.obs_data_set_default_int(settings, "slider", 5)

    #Make these reusable
    text = "P1: Type !join to enter queue"
    set_text(text, "Player 1")
    text = "P2: Type !join to enter queue"
    set_text(text, "Player 2")
    text = "next: !Join"
    set_text(text, "Next Player")

    #Clear Queue
    vq.clear_all()

    
