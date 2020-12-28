# Conway's Game of Life
This is a program which performs the famous Conway's Game of Life.
The rules and some further information are provided on this website: https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life .

### How to use this program
All you need to do is to edit the config.config file in the config directory. 
In this file you can change:
- the symbol corresponding to dead cells
- the symbol corresponding to live cells
- the number of iterations
- the initial state

Afterwards you can run the python script. This will create a new directory where you can find a text file representation of the simulation and a directory which contains plots of every single state during the simulation. Furthermore, you'll also find a video file in the output directory which shows the whole simulation.

<b>NOTE:</b> you need ffmpeg to be installed. This is needed in order to create the video file. You can download this from the following website: https://ffmpeg.org/ .

I only tested this script on Ubuntu 18.04, it may be possible that it will fail on windows and MacOs. In this scenario you'll most likely need to adopt the part which executes the ffmpeg program, however, you can also set the video argument of the <code>run_game_of_life(video=False)</code> function to false. 
