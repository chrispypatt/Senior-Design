
import cv2  # need opencv package: cv2
import os
import math  
from posedata2 import PoseData
import numpy as np
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
    behavior_pos = (10, 100) 
    angle_pos = (10, fheight - 180)
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
            if angles[count] is None:
                cv2.putText(frame, "angle: -",\
                            angle_pos, font, font_size, (0,0,255), 2)
            elif angles[count] > 90.0:
                cv2.putText(frame, "angle: %.2f" % angles[count],\
                            angle_pos, font, font_size, (0,0,255), 2)
            else:
                cv2.putText(frame, "angle: %.2f" % angles[count],\
                            angle_pos, font, font_size, (255,255,0), 2)

            # Write frequency information 
            cv2.putText(frame, "freq: %.2f" % freq[count],\
                        freq_pos, font, font_size, (255,255,0), 2)

            # Draw lines 
            pose = video.get_frame_pose(count) 
            if (pose is not None and has_keypoint(pose, RElbow)\
                                 and has_keypoint(pose, Neck)
                                 and has_keypoint(pose, MHip)):
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
    frequencies = list()
    freq = 0
    angle = 0
    last_angle = 0

    # List of angle in each frame, if angle cannot be determined or no pose
    # found in frame, the angle will be None
    frame_angles = list()     

    # sum up tilt angles for the current video
    for i in range(0, video.num_frames):
        pose = video.get_frame_pose(i)
        if pose is not None and has_keypoint(pose, RShoulder)\
                            and has_keypoint(pose, RElbow)\
                            and has_keypoint(pose, Neck)\
                            and has_keypoint(pose, MHip): 

            angle = calculate_angle(pose,RShoulder,RElbow,Neck,MHip)
            if angle == None: #reuse last angle if cant calculate one
                angle = last_angle
                frame_angles.append(None)
            frame_angles.append(angle)
            
        else:
            angle = last_angle
            frame_angles.append(None)
        
        # Append the angle to angles
        angles.append(angle)
         
        if len(angles) > 0:
            # Why are we subtracting the average from each angle?
            # angles = np.subtract(angles,np.average(angles))

            # Use last 40 angles when more than 40
            if len(angles) > 40: 
                # Use last 40 angles for FFT
                FFT = sy.fft(np.array(angles[-40:]))
            else:
                FFT = sy.fft(np.array(angles))
            sample_frequencies = np.fft.fftfreq( len(FFT), d=0.04)
            freq = abs(sample_frequencies[np.argmax(FFT)]) 
        print('Frame {}, Frequency: {}'.format(i, freq))
        frequencies.append(freq)
        last_angle = angle

    return frame_angles, frequencies
