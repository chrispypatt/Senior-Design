import os
from collections import deque
import json


win_size = 1

class PoseData: 
    def __init__(self, json_path, normalize=False, derivative=False): 
        self.path = json_path
        self.normalize = normalize
        self.derivative = derivative
        self.files = get_files(json_path)
        self.pos = 0
        self.win_size = 0
        self.window = deque()
        self.last = None

    # Returns a list of keypoints where each element is a list of the keypoint
    # values for the past win_size frames. The global variable win_size is the
    # size that the time dimension should be for the window and self.win_size is
    # the current size of the window. If self.win_size equals win_size when the
    # function is called, then the keypoint data from the oldest frame is
    # popped from the window. Internally, the window is stored as a deque with
    # the first dimension being time. This deque will be converted to a list and
    # the keypoint and time dimensions will be swapped for the return value
    # (need a function for this). The main loop of the function continues
    # looping until self.win_size == win_size. In each iteration, it reads the
    # json file from the file array at position self.pos and then increments
    # self.pos. If read_json() returns valid data, it is appended to the window
    # and self.win_size is incremented. If read_json() returns None, then the
    # deque is cleared and self.win_size is reset to 0. This has the effect of
    # resetting the window whenever the person is lost from the frame. When
    # there aren't enough frames left to fill the window, None is returned.  
    def get_window(self):
        # If the window is full, pop the first value
        if self.win_size == win_size: 
            self.window.popleft()
            self.win_size -= 1

        while self.win_size < win_size: 
            # Check to make sure there is a frame to add to window
            if self.pos == len(self.files): 
                return None
            
            # Get the data from the next frame. 
            temp = read_json(self.files[self.pos])
            if temp == None: 
                self.clear_window()
            else: 
                self.window_append(temp)
            self.pos += 1

        return format_window(self.window) 
   
    def clear_window(self): 
        self.window.clear()
        self.win_size = 0
        if self.derivative: 
            self.last = None

    def window_append(self, keypoints):
        if self.normalize:
            keypoints = normalize_keypoints(keypoints)
        if self.derivative:
            keypoints = self.calc_derivative(keypoints)
        self.window.append(keypoints)
        self.win_size += 1


    # Calculates the change in position of each keypoint in the current frame
    # with respect to the position in the previous frame. If there is no
    # previous frame, the derivative at each keypoint will be 0. 
    # Not finished
    # In order to use this function it will require some changes to the
    # get_window() method since the window will now contain the derivatives of
    # the keypoints, but the keypoint positions for the current frame and last
    # frame are needed to calculate the derivative of the current frame. There
    # are two possible solutions to this problem. The first would be to pass the
    # function the current frame positions, and have the class maintain a 
    # previous frame position variable. With this solution, the previous frame
    # variable would have to be cleared whenever the window is cleared. The
    # second solution would be to maintain two windows, one with the keypoint
    # positions and a second with the keypoint derivatives. The returned window
    # would have to be set to the derivative window when self.derivative is
    # true. This solution would also require clearing the derivative window when
    # the window is cleared, so the first solution is probably more efficient. 
    def calc_derivative(self, keypoints):
        return keypoints


# Normalizes the position of each keypoint relative to the position of its
# parent.
# Not finished
# Question: what do we want to do about the keypoint we define to be the origin?
#   Should we set its position to be (0,0) or should we leave it as is?
def normalize_keypoints(keypoints): 
    return keypoints


# Converts self.window from a deque to a list and swaps the dimensions from 
# [time][keypoints][x,y,c] to [keypoints][time][x,y,c] 
def format_window(window): 
    return rotate_matrix(list(window))


def rotate_matrix(M):
    return [M[i][j] for i in range(len(M)) for j in range(len(M[0]))]


# Reads the json file with given path. Returns an array of keypoints where
# each element is a list of [x, y, c] values for the keypoint. This only
# reads the first person found in the list. If no person is found, None is
# returned. None is also returned if at least a minimum percentage of 
# keypoints are not found. This percentage should be a global variable so it
# can be changed for all object instances simultaneously
def read_json(path, percent=.90):
    data = []
    w, h = 3, 25
    count = 0
    poseExists = 0
    keypoints = [[0 for x in range(w)]for y in range(h)]    ## Generates 2D array to be filled with keypoints
    with open(path) as json_file:                           ## 'path' is assuming the user inputs the correct file path + json file name
        data = json.load(json_file)
    if data["people"]:
        for x in range (0,25):
            for y in range (0,2):
                keypoints[x][y] = data["people"][0]["pose_keypoints_2d"][count]
                if(keypoints[x][y]>0 & y<2):     #Increase poseExists if x,y are greater than 0. Does not check confidence value
                    poseExists = poseExists + 1
                count = count + 1
        if((poseExists/50)>percent):      
            return keypoints
        else:
            return None
    else:
        return None

# Get list of files in directory. Filter out any files which don't have 
# the .json extension and sort the files alphanumerically. Then prepend 
# the directory path to filenames  
def get_files(path): 
    # files = list(filter(is_json, os.listdir(path))).sort()
    files = list(filter(is_json, os.listdir(path)))
    files.sort()
    files = [path + "/" + name for name in files]
    return files

# Check if given filename has .json extension
def is_json(filename): 
    name, ext = os.path.splitext(filename)
    return bool(ext == '.json')

