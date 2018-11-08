import math  
from posedata import PoseData
from read_json import *

#[time][keypoints][x,y,c]

LHip = 12
RHip = 9
Neck = 1
MHip = 8

#create_2Dvector(p1,p2)
# inputs:
# 	p1: 2D tuple of point 1 of vector (a1,b1)
# 	p2: 2D tuple of point 2 of vector (a2,b2)
# Output: tuple representing vector for 2 given points
def create_2Dvector(p1,p2):
	return (p1[0]-p2[0],p1[1]-p2[1])

#Pose will be a time snip of [keypoints][x,y,c]
#	We want to first calculate the spine vector
#	and hip vector, followed by calculating the 
#	angle between the two to get the tilt of the person
def calculate_angle(pose):
	# pose = pose_list[0]
	# Create hip vector with LHip to RHip 
	# LHip --------------- RHip
	left_hip_point = (pose[LHip][0],pose[LHip][1])
	right_hip_point = (pose[RHip][0],pose[RHip][1])
	vector_hip = create_2Dvector(left_hip_point,right_hip_point)

	# Create spine vector with MHip to Neck
	# 	Neck		  Neck					  Neck
	# 	 |				\						/
	# 	 |				 \					   /
	#	 |		or 		  \ 		or		  /
	# 	 |     			   \				 /
	# 	 |					\				/
	# 	MHip			   MHip		      MHip
	neck_point = (pose[Neck][0],pose[Neck][1])
	mid_hip_point = (pose[MHip][0],pose[MHip][1])
	vector_spine = create_2Dvector(neck_point,mid_hip_point)

	#Calculate numerator and denominator
	dot_prod = vector_hip[0]*vector_spine[0]+vector_hip[1]*vector_spine[1]
	hip_length = math.sqrt(math.pow(vector_hip[0],2)+math.pow(vector_hip[1],2)) 
	spine_length = math.sqrt(math.pow(vector_spine[0],2)+math.pow(vector_spine[1],2)) 

	cos_theta = dot_prod/(hip_length*spine_length)

	return math.degrees(math.acos(cos_theta))

def calculate_average_tilt(video):
	angle_sum = 0
	count = 0
	while 1: # sum up tilt angles for the current video
		frame_pose = video.get_window()
		if frame_pose == None:
			break
		else:
			count += 1
			# print(calculate_angle(frame_pose))
			angle_sum += calculate_angle(frame_pose)
	if count == 0:
		return "Error, divide by zero"
	else:
		return angle_sum/count



def main():
	video_data = scan_json_directories2('../json_output/boxing')
	for video in video_data:
		print(video.path + ":")
		average_tilt = calculate_average_tilt(video)
		print("Average tilt (degrees):")
		print(average_tilt)
		print("")


if __name__ == "__main__":
    main()







