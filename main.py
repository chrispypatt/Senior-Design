import openpose_all
#import angles
#import pose_learn
import os



# Takes an input video path and returns a tuple of (output_dir, output_video)
# For example, if input_path = "/path/to/video.ext", then the return value
# will be: "/path/to/output_video", "/path/to/output_video/output_video.avi"
def make_output_paths(input_path): 
    input_dir = os.path.dirname(input_path)
    basename = os.path.basename(input_path)
    filename, file_ext = os.path.splitext(basename)
    output_path = '{}/output_{}'.format(input_dir, filename)
    output_video_path = '{}/output_{}.avi'.format(input_dir, filename)
    return output_path, output_video_path 
   




def main(): 
    return


if __name__ == "__main__":
    main()
