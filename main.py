import openpose_all
import tensorflow as tf
import angles
import pose_learn
import os
from posedata2 import PoseData
import sys



# Takes an input video path and returns a tuple of (output_dir, output_video)
# For example, if input_path = "/path/to/video.ext", then the return value
# will be: "/path/to/output_video", "/path/to/output_video/output_video.avi"
def make_output_paths(input_path): 
    input_dir = os.path.dirname(input_path)
    basename = os.path.basename(input_path)
    filename, file_ext = os.path.splitext(basename)
    output_path = '{}/output_{}'.format(input_dir, filename)
    output_video_path = '{}/output_{}.avi'.format(output_path, filename)
    return output_path, output_video_path 
  

def run_openpose_on_video(video_path, output_path, output_video_path): 
    script = 'build/examples/openpose/openpose.bin'
    openpose_dir = '/home/patte539/Packages/openpose/'
    cwd = os.getcwd()
    os.chdir(openpose_dir)
    status = openpose_all.openpose(script, video_path, output_path,\
                                   output_video_path) 
    os.chdir(cwd)
    return status


def main(): 
    video_path = sys.argv[1]
   
    # Run openpose on the video if necessary
    output_path, output_video_path = make_output_paths(video_path)
    if not os.path.isdir(output_path):
        print("Running openpose on {}".format(video_path))
        status = run_openpose_on_video(video_path, output_path, output_video_path)
        if status == 0: 
            print("Openpose Successful")
        else:
            print("Openpose failed. Exiting...")
            return 1

    # Make a PoseData object 
    pd = PoseData(output_path)
   
    # Get the angles information
    print("Calculating angles")
    frame_angles, freqs = angles.calculate_frequency(pd)

    # Classify the video
    print("Classifying behaviors")
    with tf.device('/gpu:2'):
        behaviors = pose_learn.predict_single_video(output_path)

    # Write output to video
    print("Writing output to video")
    angles.write_to_frame(pd, frame_angles, freqs, behaviors)
    
    return 0


if __name__ == "__main__":
    main()
