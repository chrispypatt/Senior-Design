import os
from collections import deque
import json
import numpy as np



class PoseData: 
    def __init__(self, json_path, behavior=None): 
        self.path = json_path
        self.video_name = json_path.rsplit('/',1)[-1]
        self.files = get_files(json_path)
        self.behavior = behavior
        self.pos = 0
        self.window = deque()
        self.num_frames = len(self.files)

    # Takes an integer frame position and returns a numpy matrix of pose 
    # information with the format [keypoint][x, y, c]. 
    def get_frame_pose(self, frame): 
        # Make sure position is within range 
        if frame >= len(files):
            return None
        
        # Read the json file and return result
        return read_json(files[frame])

    # PoseData.get_window(win_size)
    # 
    # Returns a tuple of (window, behavior, start_frame, json_path) where window
    # is a 3D numpy array with the format [keypoints][time][x, y, c].
    #
    # The window is represented internally as a deque. If the internal
    # window deque is empty when the method is called, the deque is filled with
    # the keypoint data from the first win_size json files in the directory. If
    # the window is already win_size when the function is called, the oldest
    # set of keypoints is dropped and the data from the next json file is added
    # to the right side of the window. If the next json file contains no or
    # incomplete keypoint data, the entire window is thrown away and then
    # refilled with the keypoint data from the next contiguous set of win_size
    # valid json files. This means that each window may not by contiguous with
    # the previous or next window, but the sets of keypoint data within each
    # window is always contiguous.   
    def get_window(self, win_size):
        # If the window is full, pop the first value 
        while len(self.window) >= win_size: 
            self.window.popleft()

        while len(self.window) < win_size: 
            # Check to make sure there is a frame to add to window
            if self.pos == len(self.files): 
                self.pos = 0    # Reset once end is reached 
                return None
            
            # Get the data from the next frame. 
            temp = read_json(self.files[self.pos])
            if type(temp) is not np.ndarray: 
                self.window.clear()
            else: 
                self.window.append(temp)
            self.pos += 1
        
        start_frame = self.pos - win_size
        format_win = np.array(self.window).transpose((1, 0, 2))
        return (format_win, self.behavior, start_frame, self.path) 

    # Gets a list of all valid window tuples for a video
    def get_all_windows(self, win_size): 
        temp = self.get_window(win_size)
        window_list = []

        while temp is not None: 
            window_list.append(temp)
            temp = self.get_window(win_size)

        return window_list




#_ PoseData Class Helper Functions _____________________________________________

# Reads the json file with given path. Returns a numpy array of keypoints where
# each element is a numpy array of [x, y, c] values for the keypoint. This only
# reads the first person found in the list. If no person is found, None is
# returned. None is also returned if at least a minimum percentage of 
# keypoints are not found. This percentage is set using the percent_complete
# optional parameter. 
def read_json(filename, percent_complete=0.5):
    num_keypoints_found = 0

    with open(filename, 'r') as f:
        openpose_dict = json.load(f)

    people = openpose_dict['people']
    if len(people) < 1:
        return None

    keypoints = np.array(people[0]['pose_keypoints_2d']).reshape((25, 3)) 
    for point in keypoints:
        if point[2] != 0: 
            num_keypoints_found += 1

    if num_keypoints_found >= percent_complete * len(keypoints): 
        return keypoints 
    else:
        return None


# Get list of files in directory. Filter out any files which don't have 
# the .json extension and sort the files alphanumerically. Then prepend 
# the directory path to filenames  
def get_files(path): 
    files = list(filter(is_json, os.listdir(path)))
    files.sort()
    if files is not None: 
        files = [path + "/" + name for name in files]
    return files


# Check if given filename has .json extension
def is_json(filename): 
    name, ext = os.path.splitext(filename)
    return bool(ext == '.json')


