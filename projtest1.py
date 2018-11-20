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


		# ==========================================
		# return angle_sum/count, angles
		return angle_sum/count, angles, angle


# need to iterate through each frame and associate with keypoints/json file?
# get_frame() function similar to get_window(), but return actual frame rather than keypoint
# include in posedata.py

# assuming that the output videos have not been processed into separate frames associated w/ its keypoints
def write_to_frame(video, angle, freq)
	# read in video
	cap = cv2.VideoCapture('OPvideo.avi') # capture output video; 0 instead of video name -> webcam
							# video?
	# used to write new video
	fourcc = cv2.VideoWriter_fourcc(*'XVID')	# define codec
	# define codec, create VideoWriter object; output stored in 'newvideo.avi' file
	out = cv2.VideoWriter('newvideo.avi', fourcc, 20.0, (640,480)) 
	# VideoWriter(filename, fourcc, fps, frameSize)

	# iterate through whole video
	while(cap.isOpened()): # while video opened?
 		ret, frame = cap.read()		# read in frame
		if ret == True:
			# display text and stuff on frame

			# if keypoints exist

            font = cv2.FONT_HERSHEY_SIMPLEX	# set font
			cv2.putText(frame, "angle: " + angle, (50,50), font, 2, (255,255,0), 2)


			# if angle >= angle_thresh
			# 	cv2.rectangle(img, pt1, pt2, color[, thickness[, lineType[, shift]]])
			# if freq >= freq_thresh
			# 	cv2.rectangle(img, pt1, pt2, color[, thickness[, lineType[, shift]]])
			

			out.write(frame)		# write new frame into the new file newvideo.avi
			cv2.imshow(frame) 	# displays the new frame, can delete

			if cv2.waitKey(1) & 0xFF == ord('q')	# press 'q' to exit
				break
		else:
			break
	cap.release() # release video capture object
	cv2.destroyAllWindows() # close frames


# ====================================================================
# utilizing cv2 package
# *** will have to retrieve frame of output video
# this function assumes we have parsed the frames and associated them with the keypoints the json
# 
# def write_to_frame1(video, angle, freq):
	# while 1: # sum up tilt angles for the current video
	# 	frame_pose = video.get_window()
	# 	if frame_pose == None:
	# 		break
	# 	else:
			
	# 		#cap = cv2.VideoCapture('video name')
	# 		#fourcc = cv2.VideoWriter_fourcc(*'XVID')
	# 		#out = cv2.VideoWriter('outputvideo', fourcc, 20.0, (640,480))


	# 		# frame_pose = video.get_frame() --> some function to retrieve the frame associated with the keypoints from video.get_window()

    #         font = cv2.FONT_HERSHEY_SIMPLEX	# set font
	# 		cv2.putText(frame_pose, "angle: " + angle, (50,50), font, 2, (255,255,0), 2)
	# 			# cv2.putText(img, text, org, fontFace, fontScale, 
	# 			# 	color[, thickness[, lineType[, bottomLeftOrigin]]])
	# 			# img = image
	# 			# text = text string to be drawn
	# 			# org = bottom left corner of the text string in the image
	# 			# font = structure
	# 			# fontFace = font type
	# 			# fontScale = font scale factor multiplied by base size of font type
	# 			# color = text color, thickness = thickness of text
	# 			# lineType --> = cv2.LINE_AA recommended for better look
	# 			# bottomLeftOrigin: true --> img data origin Bottom-left corner
	# 			# 					false --> top-left corner

	# 			# example: write OpenCV on image in while color
	# 				# cv2.putText(img,'OpenCV',(10,500),font,4,(255,255,255),2,cv2.LINE_AA)


	# 		# outputting a rectangle (output at certain freq/angles)
	# 		#if angle >= angle_thresh
	# 		cv2.rectangle(img, pt1, pt2, color[, thickness[, lineType[, shift]]])
	# 			# pt1 - vertex of rect, pt2 - vert. of rect. opposite to pt1
	# 			# color, thickness, lineType = same as above
	# 			# shift = # of fractional bits in the point coordinates
	# 			# pt1 top-left-most pt of rect; pt2 bottom-right-most pt
	# 				# these pts reference the keypts of wrist and elbows
	# 			# pt1 = (min(xKP1, xKP2), min(yKP1, yKP2)) --> (min(p1, p3), min(p2, p4))
	# 			# pt2 = (max(xKP1, xKP2), max(yKP1, yKP2)) --> (max(p1, p3), max(p2, p4))

	# 		#if freq >= freq_thresh
	# 		cv2.rectangle(img, pt1, pt2, color[, thickness[, lineType[, shift]]])
	# 			# pts in reference of topleft shoulder and bottomright hip points


	# 		out.write(frame_pose)	# write the new frame
	# 		cv2.imshow(frame_pose)	# display image in a window
	# 								# probably not what we're going to use here
	# 								# write back to new video?
			

	# 		ch = cv2.waitKey(1) # waits 1ms for any keyboard event
	# 		if ch == 27: # 27 = escape button? --> exit program?
	# 			break

	# else:
	# 	pass

def main():
	video_data = scan_json_directories2('../json_output/handwaving')
	for video in video_data:
		print(video.path + ":")

		# =============================================
		# average_angle, angles = calculate_average_angle(video)
		average_angle, angles, angle = calculate_frequency(video)

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
		
		# ========================================================
        write_to_frame(video, angle, freq)


if __name__ == "__main__":
    main()

