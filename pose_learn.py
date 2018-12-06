import os
import math
from collections import deque
import json
import numpy as np
import random
from keras.utils import to_categorical
from keras.models import Sequential, load_model
from keras.layers import (Activation, Dense, Dropout, Flatten, Conv2D, 
                          MaxPooling2D)
from keras.losses import categorical_crossentropy
from keras.optimizers import Adam, SGD, Adadelta
import tensorflow as tf




#_ Global Constants ____________________________________________________________

labels = {'walking': 0,
          'jogging': 1,
          'boxing': 2,
          'handclapping': 3,
          'handwaving': 4,
          'running': 5}

# Add running once directory is fixed 
behaviors = ['walking', 'jogging', 'boxing', 'handclapping', 'handwaving',
             'running']

num_behaviors = 6

model_file = 'nonormal_model.h5'
normalize = False

#_ Predict Single Video ________________________________________________________

# Takes the directory containing the openpose json data for a single video and 
# returns a list containing a string describing the behavior predicted during
# each frame. 
def predict_single_video(json_dir):
    win_size = 12

    # Get the posedata object 
    pd = PoseData(json_dir, None)

    # Get all windows 
    windows = pd.get_all_windows(win_size)

    # Get the number of frames 
    num_frames = len(pd.files)

    # Load the model
    model = load_model(model_file)

    # Generate the X data set for the video
    X_set = prepare_X_set(windows)
    X_set = scale_Xset(X_set, 160/1920)

    # Predict using the X_set and loaded model to get the Y_set
    Y_set = model.predict(X_set, batch_size=128, verbose=0)

    # Make list containing tuples of the Y output and start frame for each
    # window using the list of windows and the Y set
    Y_windows = [(output, window[2]) for window, output in zip(windows, Y_set)] 

    # Make a list of num_frames numpy arrays of length 6, initialized to zero
    Y_sum = np.zeros((num_frames, num_behaviors))

    # Iterate through Y_windows. For each tuple, add the Y output vector to
    # win_size elements of Y_sum starting from the start index
    for window in Y_windows:
        start_frame = window[1]
        for i in range(start_frame, start_frame + win_size):
            Y_sum[i] += window[0]

    # Iterate through Y_sum. For each element, determine the index of the
    # maximum value (not sure how to break ties yet), and use this index to add
    # the behavior string (from behaviors) to a new list. If all elements are
    # zero, add an empty string to the list. 
    Y_behaviors = [behaviors[np.argmax(sum_out)]\
		   if np.sum(sum_out) > 0 else ''\
	           for sum_out in Y_sum] 
    
    # Return the behaviors list. Use to write the predicted behavior to the
    # output video. 
    return Y_behaviors 



#_ Keras _______________________________________________________________________ 


# Use as example, don't call directly 
def initialize_training(load_model=False):
    win_size = 12
    json_dir = '/media/storage/chris/json_output'
   
    if not load_model: 
        # Build the model 
        model = build_model(win_size)
    else:
        model = load_model(model_file)

    # Prepare the datasets 
    print('Preparing datasets')
    X_train, Y_train, X_test, Y_test = prepare_sets(json_dir, win_size)
    
    return model 

# Use as example, don't call directly 
def train_model(model, num_batches, num_epochs):     
    print('Training the model')
    model.fit(X_train, Y_train, validation_data=(X_test, Y_test),\
              batch_size=num_batches, epochs=num_epochs, verbose=2)

    loss, acc = model.evaluate(X_test, Y_test)
    print('Test loss: {}'.format(loss))
    print('Test Accuracy: {}'.format(acc))

    return model


def build_model(win_size): 
    k_size = (2, 2)

    # Create the model
    model = Sequential()
    
    # Add the model layers
    model.add(Conv2D(16, kernel_size=k_size, input_shape=(25, win_size, 3),
              data_format='channels_last'))
    model.add(Activation('relu'))
    model.add(Conv2D(16, kernel_size=k_size, data_format='channels_last')) 
    model.add(Activation('softmax'))
    model.add(MaxPooling2D(pool_size=k_size, data_format='channels_last'))
    #model.add(Dropout(0.25))
    model.add(Conv2D(32, kernel_size=k_size, data_format='channels_last')) 
    model.add(Activation('relu'))
    model.add(Conv2D(32, kernel_size=k_size, data_format='channels_last')) 
    model.add(Activation('softmax'))
    model.add(MaxPooling2D(pool_size=k_size, data_format='channels_last'))
    #model.add(Dropout(0.25))
    model.add(Flatten())
    model.add(Dense(256, activation='sigmoid'))
    #model.add(Dropout(0.5))
    model.add(Dense(256, activation='relu'))
    #model.add(Dropout(0.5))
    model.add(Dense(num_behaviors, activation='softmax'))

    # Compile the model
    model.compile(loss=categorical_crossentropy,
                  optimizer=Adadelta(), metrics=['accuracy'])
    return model


def print_layer_shape(model):
    arch = [(layer.input_shape, layer.output_shape) for layer in model.layers]
    for layer in arch:
        print('{}->{}'.format(layer[0], layer[1]))



#_ Data Preparation Functions  _________________________________________________

def prepare_sets(json_dir, win_size, test_size=0.2):
    # Get the list of all windows 
    win_list = get_all_win(json_dir, win_size)

    # Shuffle the list 
    random.shuffle(win_list)

    # Split the list 
    split_index = round(len(win_list) * (1 - test_size))
    train_set, test_set = split_list(win_list, split_index) 
   
    # Prepare X and Y subsets of the training and testing sets 
    X_train = prepare_X_set(train_set)
    Y_train = prepare_Y_set(train_set)
    X_test = prepare_X_set(test_set)
    Y_test = prepare_Y_set(test_set)

    return X_train, Y_train, X_test, Y_test


def prepare_X_set(training_set):
    if normalize:
        return np.array([normalize_window(window[0]) for window in training_set])
    else:
        return np.array([window[0] for window in training_set])


def prepare_Y_set(training_set): 
    Y_labels = np.array([labels[window[1]] for window in training_set])
    return to_categorical(Y_labels, num_classes=num_behaviors)
   

def split_list(alist, split_index):
    return alist[:split_index], alist[split_index:]


def get_all_win(json_dir, win_size):
    pd_list = get_all_pd(json_dir)
    win_list = [] 
    for pd in pd_list:
        win_list = win_list + pd.get_all_windows(win_size)
    return win_list


def get_all_pd(json_dir): 
    pd_list = []
    for behavior in behaviors:
        path = '{}/{}'.format(json_dir, behavior)
        pd_list = pd_list + scan_json_dir(path, behavior)
    return pd_list


def scan_json_dir(directory, behavior): 
    pd_list = []
    it = os.scandir(directory)
    for entry in it: 
        if entry.is_dir() and entry.name.startswith("output_"): 
            # Add to PoseData object for video to data array
            pd_list.append(PoseData(entry.path, behavior))
    return pd_list
 


#____ Window Normalization Functions ___________________________________________

def scale_Xset(Xset, scale_factor):  
    for i in range(0, len(Xset)):
        for j in range(0, len(Xset[i])):
            for k in range(0, len(Xset[i][j])):
                if Xset[i][j][k][2] != 0:
                    Xset[i][j][k][0] *= scale_factor
                    Xset[i][j][k][1] *= scale_factor
    return Xset


def normalize_window(window): 
    x_max, x_min, y_max, y_min = get_window_bounds(window)
    scale_factor = 500 / max(x_max - x_min, y_max - y_min)

    for i in range(0, len(window)):
        for j in range(0, len(window[i])):
            if window[i][j][2] != 0:
                window[i][j][0] = (window[i][j][0] - x_min) * scale_factor
                window[i][j][1] = (window[i][j][1] - y_min) * scale_factor

    return window


def get_window_bounds(window):
    first = True
    for keypoint in flatten_window(window):
        if keypoint[2] != 0:
            if first: 
                x_max = keypoint[0]
                x_min = keypoint[0]
                y_max = keypoint[1]
                y_min = keypoint[1]
                first = False
            else:
                x_max = max(x_max, keypoint[0])
                x_min = min(x_min, keypoint[0])
                y_max = max(y_max, keypoint[1])
                y_min = min(y_min, keypoint[1])

    return x_max, x_min, y_max, y_min


def flatten_window(window):
    win_size = window.shape[1]
    return window.reshape(25 * win_size, 3) 



#_ PoseData Class Definition ___________________________________________________
class PoseData: 
    def __init__(self, json_path, behavior): 
        self.path = json_path
        self.files = get_files(json_path)
        self.behavior = behavior
        self.pos = 0
        self.window = deque()

    # Returns a deque of  win_size keypoint numpy matricies. If the internal
    # window deque is empty when the method is called, the deque is filled with
    # the keypoint data from the first win_size json files in the directory. If
    # the the window is already win_size when the function is called, the oldest
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


