import os
import sys
from shutil import rmtree

#_ Function Definitions ________________________________________________________

def is_readable(path):
    return os.access(path, os.F_OK | os.R_OK)

def is_excutable(path): 
    return os.access(path, os.F_OK | os.X_OK)

# input_filename should have extension removed 
def make_output_path(output_dir, input_filename): 
    return output_dir + '/output_' + input_filename

# output_dir should already exist. 
# Calls itself recursively on any directories found in the input directory
def process_dir(script, input_dir, output_dir): 
    print("Scanning directory " + input_dir) 

    it = os.scandir(input_dir)
    for entry in it: 
        # Exclude hidden entries and make sure we have read permission
        if not entry.name.startswith('.') and is_readable(entry.path): 
            if entry.is_file(): 
                # Separate the name of the file and the extension
                filename, file_ext = os.path.splitext(entry.name)
                
                # Check if .avi file
                if file_ext == '.avi': 
                    print("Found video: " + entry.name)

                    # Make output directory path
                    output_path = make_output_path(output_dir, filename)
                    video_path = make_output_path(output_path,filename)

                    # Run openpose if output directory does not already
                    # exist. If it exists, we assume openpose has already
                    # been successfully run on input file 
                    if not os.path.isdir(output_path): 
                        print("Running openpose on " + entry.name)
                        print("Putting results in " + output_path)
                        os.mkdir(output_path)

                        # Execute openpose script on file, putting results in
                        # new output directory created for the file.
                        status = openpose(script, entry.path, output_path,video_path)
                       
                        # delete output directory if openpose failed 
                        if status != 0: 
                            print("Openpose unsuccessful")
                            print("Deleting " + output_path)
                            rmtree(output_path)
                    else: 
                        print(output_path + " already exists")
                        print("Skipping " + entry.name) 

            elif entry.is_dir(): 
                # Make subdirectory in output directory for subdirectory if
                # one does not already exist. 
                sub_output_dir = output_dir + '/' + entry.name
                if not os.path.isdir(sub_output_dir): 
                    os.mkdir(sub_output_dir)

                # recursively call process_dir on subdirectory
                process_dir(script, entry.path, sub_output_dir) 




# Output dir should exist and have write permission before calling
def openpose(script, input_file, output_dir, video_path): 
    print(output_dir+".avi")
    cmd = script + " --video  " + input_file + " --display 0" \
          + " --write_video " + video_path + ".avi --write_json " + output_dir  
    return os.system(cmd)



#__ Main Function ______________________________________________________________
def main():
    # Check number of arguments
    if len(sys.argv) < 4:
        print("Usage: openpose_all <openpose script> <input dir> <output dir>")
        sys.exit()

    # Get script arguments 
    script = sys.argv[1]
    input_dir = sys.argv[2]
    output_dir = sys.argv[3]

    # Check that script exists and execute permission
    if not is_excutable(script): 
        sys.exit("Openpose script path is invalid")

    # Check that input directory exists and has read permission
    if not is_readable(input_dir): 
        sys.exit("Input directory is invalid")

    # If output directory already exists. If it exists, make sure it is a
    # directory and has write permission. If it does not exist, make it. 
    if os.access(output_dir, os.F_OK): 
        if not os.path.isdir(output_dir):
            sys.exit("Output directory is not a directory")
        elif not os.access(output_dir, os.W_OK):
            sys.exit("Do not have write permission for output directory")
    else: 
        os.mkdir(output_dir)
        
    # Make paths absolute if relative since we will be changing the working
    # directory. 
    # Not changing working directory, but doing this anyway because convenient
    # way of eliminating trailing forward slash on directory names. 
    script = os.path.abspath(script)
    input_dir = os.path.abspath(input_dir)
    output_dir = os.path.abspath(output_dir)

    # Must make sure that current directory is openpose directory

    # Scan input directory for files and subdirectories, make output directories
    # and run openpose on video files in input directory
    process_dir(script, input_dir, output_dir)




if __name__ == "__main__":
    main()
