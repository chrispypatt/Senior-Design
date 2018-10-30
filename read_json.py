import os

json_dir = "/media/storage/chris/json_output"
running_dir = json_dir + "/running"
walking_dir = json_dir + "/walking"
jogging_dir = json_dir + "/jogging"
boxing_dir = json_dir + "/boxing"
handclapping_dir = json_dir + "/handclapping"
handwaving_dir = json_dir + "/handwaving"


# Directory is a directory which contains directories that contain the openpose
# json output for a video. 
def scan_json_directories2(directory): 
    video_data = []
    it = os.scandir(directory)
    for entry in it: 
        if entry.is_dir() and entry.name.startswith("output_"): 
            # Add to PoseData object for video to data array
            video_data.append(PoseData(entry.path))

    return video_data
            


