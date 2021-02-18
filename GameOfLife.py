"""
Author: Christopher Schicho
Project: Conway's Game of Life
Version: 0.0
"""

# NOTE: this script uses the ffmpeg software for creating the video file.
# you can download it from this website: https://ffmpeg.org/

# you can find the rules for this simulation on the following website:
# https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life

# you can edit the parameters of the simulation in the config.config file in the config directory

import os
import re
import tqdm
import shutil
import subprocess
import numpy as np
import matplotlib.pyplot as plt


class GameOfLife:

    def __init__(self, configpath="./config/config.config", outputpath="./output"):

        # read file content
        with open(configpath, "r") as file:
            file_content = file.read()

        # n_iterations
        # search for valid pattern
        match_iter = re.search('n_iterations:[ ]*(\d+\.\d+|\d+)[ ]*', file_content)

        if match_iter:
            try:
                # extract value of n_iterations and try to convert it to integer
                n_iterations = int(file_content[match_iter.start(): match_iter.end()].split(":")[1].strip())
            except:
                raise AttributeError("value n_iterations is not convertible to integer")
        else:
            raise AttributeError("value n_iterations is missing")

        # dead_symbol
        # search for valid pattern
        match_dead = re.search('dead_symbol:[ ]*".{1}"[ ]*', file_content)

        if match_dead:
            # extract the character which stands for a dead cell
            dead_symbol = file_content[match_dead.start(): match_dead.end()].split(":")[1].split('"')[1]
        else:
            raise AttributeError("dead_symbol is is missing or not a single character")

        # live_symbol
        # search for valid pattern
        match_live = re.search('live_symbol:[ ]*".{1}"[ ]*', file_content)

        if match_live:
            # extract the character which stands for an living cell
            live_symbol = file_content[match_live.start(): match_live.end()].split(":")[1].split('"')[1]
        else:
            raise AttributeError("live_symbol is is missing or not a single character")

        # init_state
        # pattern for checking the validity of the characters
        pattern = 'init_state:\s*"{1}(' + re.escape(dead_symbol) + "|" + re.escape(live_symbol) + '|\s)*"{1}'

        # search for valid pattern
        match_init = re.search('init_state:\s*"{1}(.|\s)*\n"{1}', file_content)

        if match_init:
            # search for invalid characters
            if re.search(pattern, file_content):
                # extract initial seed state content
                init_content = file_content[match_init.start(): match_init.end()].split("\n")[2:-1]

                # variables needed in the for-loop
                temp_init_content = []
                line_length = None

                for line in init_content:
                    if not line_length:
                        line_length = len(line)

                    if len(line) == line_length:
                        line = [char for char in line]
                        temp_init_content.append(line)
                    else:
                        raise ValueError("line lengths in initial seed state are not equal")

                init_state = np.array(temp_init_content)
                # change the representing of dead cells to 0 and living cells to 1
                init_state = np.array(init_state == live_symbol, dtype=np.int)

            else:
                raise ValueError("initial state seed contains invalid characters")
        else:
            raise AttributeError("initial state seed is missing")

        # variables and paths of the class GameOfLife
        self.outputpath = outputpath

        # make the output directory
        os.makedirs(self.outputpath, exist_ok=True)

        # make the plots folder in the output directory
        self.plots_folder = os.path.join(self.outputpath, "plots")
        # clean the plots folder
        shutil.rmtree(self.plots_folder, ignore_errors=True)
        os.makedirs(self.plots_folder, exist_ok=True)

        # create a state output file
        # if it exists, overwrite it
        self.outputfile = os.path.join(self.outputpath, "GameOfLife_States.txt")
        with open(self.outputfile, "w+") as file:
            file.write("")

        self.n_iterations = n_iterations
        self.current_iteration = 0
        self.dead_symbol = dead_symbol
        self.live_symbol = live_symbol
        self.init_state = init_state
        self.current_state = init_state


    def _get_next_state(self):
        """ calculates the next state """

        # limits of the array
        arr_shape = self.current_state.shape
        limit_rows = arr_shape[0] - 1
        limit_columns = arr_shape[1] - 1

        # next state array
        next_state = np.zeros(arr_shape, dtype=np.int)

        for row in range(arr_shape[0]):
            for column in range(arr_shape[1]):

                # extract cell's neighbours
                # define temporary neighbours array
                neighbours = np.zeros((3, 3), dtype=np.int)

                for row_shift in range(row - 1, row + 2):
                    for column_shift in range(column - 1, column + 2):
                        # check if row_shift is outside the boundaries
                        # check if column_shift is outside the boundaries
                        if row_shift < 0 or row_shift > limit_rows or \
                           column_shift < 0 or column_shift > limit_columns:
                            continue

                        # neighbour is alive
                        if self.current_state[row_shift][column_shift] == 1:
                            neighbours[row - row_shift + 1][column - column_shift + 1] = 1
                        # else:
                        # neighbour is dead

                # sum of alive neighbours
                neighbours[1][1] = 0
                neighbours_sum = neighbours.sum()

                # cell is alive
                if self.current_state[row][column] == 1:
                    # cell has two or three living neighbours
                    if neighbours_sum == 2 or neighbours_sum == 3:
                        next_state[row][column] = 1
                    # else:
                    # cell has fewer than two alive neighbours (underpopulation)
                    # cell has more than three alive neighbours (overpopulation)
                    # the cell is going to be dead in the next state

                # current cell is dead
                else:
                    # cell has exactly three alive neighbours (reproduction)
                    if neighbours_sum == 3:
                        next_state[row][column] = 1
                    # else:
                    # cell stays dead

        self.current_state = next_state


    def _write_state(self):
        """ appends the current state to a file """

        state_arr = self.current_state.astype(str)

        # replace representations
        state_arr[state_arr == "0"] = self.dead_symbol
        state_arr[state_arr == "1"] = self.live_symbol

        # append to output file
        with open(self.outputfile, "a") as file:
            np.savetxt(file, state_arr, delimiter="", fmt="%1.1c",
                       header=f"iteration: {self.current_iteration}", footer="\n")


    def _state_to_image(self):
        """ saves the current state as an image """

        img_path = os.path.join(self.plots_folder, f"state_{self.current_iteration:06}.png")

        # create the plot and save it
        fig, ax = plt.subplots()
        ax.imshow(np.asarray(self.current_state, dtype=np.uint8), cmap='gray', vmin=0, vmax=1)
        plt.axis('off')
        fig.savefig(img_path)
        plt.close(fig)


    def _states_to_video(self):
        """ makes a video out of the saved image files """

        # command for calling the ffmpeg program
        video_filename = "GameOfLife.mp4"
        ffmpeg_command = f'ffmpeg -r 10 -pattern_type glob -i \
                         "{os.path.join(self.outputpath, "plots", "*.png")}" -c:v libx264 -vprofile baseline \
                         -pix_fmt yuv420p -c:a aac -movflags faststart {os.path.join(self.outputpath, video_filename)}'

        # execute the ffmpeg command
        subprocess.call(ffmpeg_command, shell=True)


    def run_game_of_life(self, video=True):
        """
        :param video:bool whether a video should be created or not
        runs the game defined in the config file
        """

        # write initial state to file and save the image of it
        self._write_state()
        self._state_to_image()

        # calculate all single steps
        with tqdm.tqdm() as progressbar:
            while self.current_iteration < self.n_iterations:
                self.current_iteration += 1
                self._get_next_state()
                self._write_state()
                self._state_to_image()
                progressbar.update()

        # check whether the user requests a video or not
        if video:
            self._states_to_video()


"""
run the simulation
"""
if __name__ == "__main__":
    GameOfLife().run_game_of_life()