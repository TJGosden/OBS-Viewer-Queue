# OBS Viewer Queue
Allows stream viewers to enter a queue, where their names will then be displayed on screen. This programme was made for Smash Bros so there is also a counter that you can increment for each game that they play. It can also be used with streambots/programmes like "Mix It Up", to automatically cycle the queue and send messages in chat.

# How to use
Once downloaded, add the **"Queue_v3.py"** file to your OBS `Scripts` tabs which can be found under `Tools`. 

# Setup
![Settings](Queue_GUI.JPG)

- Channel: Twitch channel you want to post in.
- User: User you want to post as.
- Oauth: Your authorisation key, which can be found on [this site](https://twitchapps.com/tmi/)
- Test: By pressing the `Post Code` button, you can test whether you are connected to your stream chat. If so It should post a message with whatever you have written in "Arena Code".
- Sources: You can then select from a list of text sources, "One", "Two", and "Next", where the viewers in your queue will be displayed.
- Alert Source: You can then also select a video or audio source that will play every time a viewer is queued up as "P1" or "P2".
- Number of Games: Finally you can select the number of games you want to keep track of for each entrant. Once the count is reached, the next viewer will be cycled in.

# Hotkeys
The main controls for the programme are set in your `Hotkeys` which you should be able to find in `Settings`.
There are hotkeys to increment the count for both players and reset each count. As well as the "Next Player" hotkey which is used to queue up a viewer if none of the slots are filled; the main use of which is to be used alongside a viewer command i.e. !join, that will automatically queue them up. This is achieved by using a streambot or programme like "Mix It Up" to press the hotkey when the command is used.
