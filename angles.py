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
RElbow = 3
RWrist = 4
RShoulder = 2

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

	cos_theta = dot_prod/(l1*l2)

	return math.degrees(math.acos(cos_theta))

def calculate_average_angle(video):
	angles = list()
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
				angle = calculate_angle(frame_pose,LHip,RHip,Neck,MHip)
				angle_sum += angle
				angles.append(angle)
			else:
				angles.append(0)
	if count == 0:
		return "Error, divide by zero"
	else:
		return angle_sum/count, angles

def calculate_frequency(video):
	angles = list()
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
				angle = calculate_angle(frame_pose,RShoulder,RWrist,Neck,MHip)
				angle_sum += angle
				angles.append(angle)
			else:
				angles.append(0)
	if count == 0:
		return "Error, divide by zero"
	else:
		return angle_sum/count, angles

def main():
	video_data = scan_json_directories2('../json_output/handwaving')
	for video in video_data:
		print(video.path + ":")
		# average_angle, angles = calculate_average_angle(video)
		average_angle, angles = calculate_frequency(video)
		print("Average angle (degrees):")
		print(average_angle)
		print("")


		# Read in data from file here
		length = len(angles)
		angles = np.subtract(angles,np.average(angles))
		# Create time data for x axis based on array length
		x = sy.linspace(0.04, length*0.04, num=length)

		# Do FFT analysis of array
		FFT = sy.fft(angles)
		# power = np.abs(FFT)
		freq = np.fft.fftfreq(len(FFT),d=0.04)
		plt.figure()
		plt.plot( freq, FFT)
		peakY = np.max(FFT) # Find max peak
		locY = np.argmax(FFT) # Find its location
		frqY = freq[locY] #
		print(frqY)
		plt.ioff()
		plt.show()
		


if __name__ == "__main__":
    main()







