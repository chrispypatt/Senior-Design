
import cv2  # need opencv package: cv2
import os
import math  
from posedata import PoseData
import numpy as np
from read_json import *
import matplotlib.pyplot as plt
import scipy as sy
import scipy.fftpack as fftpack
import pylab as pyl

#[time][keypoints][x,y,c]

LHip = 12
RHip = 9
Neck = 1
MHip = 8
RElbow = 6
RWrist = 4
RShoulder = 5

def write_to_frame(video, angles, freq, behaviors):
    fps = 25

    # read in video
    cap = cv2.VideoCapture(video.path + "/" + video.video_name + ".avi") 

    # define codec
    fourcc = cv2.VideoWriter_fourcc(*"XVID")

    # Get height and width of frame 
    fwidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    fheight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print('Frame size: {}x{}'.format(fwidth, fheight))

    # Set the position of the text elements and text parameters 
    behavior_pos = (10, 80) 
    angle_pos = (10, fheight - 120)
    freq_pos = (10, fheight - 40)
    font = cv2.FONT_HERSHEY_DUPLEX      # set font
    font_size = 4

    # define codec, create VideoWriter object; output stored in 'newvideo.avi' file
    out = cv2.VideoWriter(video.path +  "/" + video.video_name +'new.avi',\
                          fourcc, fps, (fwidth,fheight)) 

    count = 0
    while(True):
        # Read in frame. If no frame, break out of loop
        ret, frame = cap.read()	
        if not ret: 
            break
        
        # Write behavior classification
        cv2.putText(frame, "behavior: {}".format(behaviors[count]),\
                    behavior_pos, font, font_size, (255, 255, 0), 2)

        # Write angle, freq, and draw angle if behavior is hand waving
        if behaviors[count] == 'handwaving':
            # Write angle information 
            if count < len(angles):
                if angles[count] > 90.0:
                    cv2.putText(frame, "angle: %.2f" % angles[count],\
                                angle_pos, font, font_size, (0,0,255), 2)
                else:
                    cv2.putText(frame, "angle: %.2f" % angles[count],\
                                angle_pos, font, font_size, (255,255,0), 2)

            # Write frequency information 
            cv2.putText(frame, "freq: %.2f" % freq[count],\
                        freq_pos, font, font_size, (255,255,0), 2)



            pose = video.get_window() 
            if (pose != False and has_keypoint(frame, RElbow)\
                              and has_keypoint(frame, Neck)
                              and has_keypoint(frame, MHip)):
                # Draw neck to elbow line 
                cv2.line(frame,\
                         keypoint_int(pose, RElbow), keypoint_int(pose, Neck),\
                         (0, 0, 255), 2)
                
                # Draw neck to hip line 
                cv2.line(frame,\
                         keypoint_int(pose, Neck), keypoint_int(pose, MHip),\
                         (0,0,255), 2)

        # Write new frame to output and increment count 
        out.write(frame)
        count += 1

        # Stop transfer when 'q' is pressed  
        if (cv2.waitKey(50) & 0xFF)== ord('q'):	# press 'q' to exit
            break

        # Loop end

    cap.release() # release video capture object
    out.release()
    cv2.destroyAllWindows() # close frames


# Checks that the pose has a particular keypoint
def has_keypoint(pose, keypoint):
    return pose[keypoint][2] > 0


# Returns a tuple (int(x), int(y)) for keypoint with given index
def keypoint_int(pose, keypoint): 
    return (int(pose[keypoint][0]), int(pose[keypoint][1]))


#create_2Dvector(p1,p2)
# inputs:
# 	p1: 2D tuple of point 1 of vector (a1,b1)
# 	p2: 2D tuple of point 2 of vector (a2,b2)
# Output: tuple representing vector for 2 given points
def create_2Dvector(p1,p2):
    return (p1[0]-p2[0],p1[1]-p2[1])



#Pose will be a time snip of [keypoints][x,y,c]
#	angle of vectors (a1,a2) to (b1,b2)
def calculate_angle(pose, a1,a2,b1,b2):
    # pose = pose_list[0]
    # Create 1st vector

    p1 = (pose[a1][0],pose[a1][1])
    p2 = (pose[a2][0],pose[a2][1])
    vector_1 = create_2Dvector(p1,p2)

    p3 = (pose[b1][0],pose[b1][1])
    p4 = (pose[b2][0],pose[b2][1])
    vector_2 = create_2Dvector(p3,p4)

    #Calculate numerator and denominator
    dot_prod = vector_1[0]*vector_2[0]+vector_1[1]*vector_2[1]
    l1 = math.sqrt(math.pow(vector_1[0],2)+math.pow(vector_1[1],2)) 
    l2 = math.sqrt(math.pow(vector_2[0],2)+math.pow(vector_2[1],2)) 

    if (l1==0 or l2 ==0):
        return None
    else:
        cos_theta = dot_prod/(l1*l2)
        return math.degrees(math.acos(cos_theta))


def calculate_frequency(video):
    angles = list()
    all_angles = list()
    frequencies = list()
    frqY = 0
    angle_sum = 0
    count = 0
    while 1: # sum up tilt angles for the current video
        frame_pose = video.get_window()
        if frame_pose == None:
            break
        else:
            count += 1
            if frame_pose != False:
                # print(calculate_angle(frame_pose))
                angle = calculate_angle(frame_pose,RShoulder,RElbow,Neck,MHip)
                if angle == None: #reuse last angle if cant calculate one
                    angle = all_angles[-1]
                angle_sum += angle
                angles.append(angle)
                all_angles.append(angle)
                
            else:
                angles.append(0)

            if len(angles) >= 40:
                # Read in data from file here
                length = len(angles)
                angles = np.subtract(angles,np.average(angles))
                # Create time data for x axis based on array length
                x = sy.linspace(0.04, length*0.04, num=length)

                # Do FFT analysis of array
                FFT = sy.fft(angles)
                # power = np.abs(FFT)
                freq = np.fft.fftfreq(len(FFT),d=0.04)
                # plt.figure()
                # plt.plot( freq, FFT)
                peakY = np.max(FFT) # Find max peak
                locY = np.argmax(FFT) # Find its location
                frqY = abs(freq[locY]) 
                angles = list()
                # print(frqY)
                # plt.ioff()
                # plt.show()
            frequencies.append(frqY)
    video.pos = 0
    if count == 0:
        return "Error, divide by zero"
    else:
        return angle_sum/count, all_angles, frequencies


def main():
    video_data = scan_json_directories2('../json_output/handwaving')
    for video in video_data:
        print(video.path + ":")
        # average_angle, angles = calculate_average_angle(video)
        average_angle, angles, freqs = calculate_frequency(video)
        # print("Average angle (degrees):")
        # print(average_angle)
        print("")
        write_to_frame(video, angles, freqs)


if __name__ == "__main__":
    main()
