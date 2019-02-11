#!/bin/sh

user="patte539"
host="jupiter-2.cs.umn.edu"
password="AxaDlUfMUr+e"
remote_input_dir="/media/storage/chris/our_videos"

input_video_path="$(cd "$(dirname "$1")"; pwd)/$(basename "$1")"
input_video_dir="$(dirname "${input_video_path}")"
input_video_name="$(basename "$input_video_path")"
fps25_video_name="fps25_${input_video_name}"
fps25_video_path="${fps25_video_name}"
fps25_video_basename="$(echo "$fps25_video_name" | cut -f 1 -d '.')"
output_video_name="output_${fps25_video_basename}new.avi"
remote_output_dir="${remote_input_dir}/output_${fps25_video_basename}"
remote_output_video_path="${remote_output_dir}/${output_video_name}"
demo_script="cd ~/python/Senior-Design;time python3 main.py ${remote_input_dir}/${fps25_video_name}"

# Check to make sure the video exists. 
if [ ! -f "$input_video_path" ]; then
    echo "${input_video_path} doesn't exist"
    exit 1
fi

# Print variable values 
echo "Input path: ${input_video_path}"
echo "Input video name: $input_video_name"
echo "${fps25_video_name}"
echo "${fps25_video_path}"
echo "${fps25_video_basename}"
echo "Output video name: $output_video_name"
echo "${remote_output_dir}"
echo "${remote_output_video_path}"

# Reencode the video at 25 fps
ffmpeg -i "${input_video_path}" -r 25 -an "${fps25_video_path}"

# Transfer the video
echo "Transferring video to ${remote_input_dir} on patte539@jupiter-2.cs.umn.edu"
sshpass -p ${password} scp ${fps25_video_path} ${user}@${host}:${remote_input_dir}
if [ $? -eq 0 ]; then
    echo "Transfer successful"
else
    echo "Transfer failed. Terminating..."
    exit 1
fi


# Run program on the video
sshpass -p ${password} ssh -l ${user} ${host} "${demo_script}"
if [ $? -eq 0 ]; then
    echo "Remote command successful"
else
    echo "Remote command failed. Terminating..."
    exit 1
fi


# Get the output video from the remote host  
sshpass -p ${password} sftp ${user}@${host}:${remote_output_video_path} 
# sshpass -p ${password} sftp patte539@jupiter-2.cs.umn.edu ${remote_output_video_path} ${input_dir}
if [ $? -eq 0 ]; then
    echo "Output video transfer successful"
else
    echo "Output video transfer failed. Terminating..."
    exit 1
fi

