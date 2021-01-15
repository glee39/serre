import numpy as np
import cv2 as cv
import argparse
import random
import math
from scipy import ndimage

def get_args():
    parser = argparse.ArgumentParser()

    # get all script args
    _, all_arguments = parser.parse_known_args()
    double_dash_index = all_arguments.index('--')
    script_args = all_arguments[double_dash_index + 1: ]

    # add parser rules
    parser.add_argument('-n', '--side', help="side length per square (in pixels)")
    parser.add_argument('--legs', nargs='+', type=int)

    parsed_script_args, _ = parser.parse_known_args(script_args)

    return parsed_script_args

def drawLeg(upper_left, leg_len, orientation):
    if orientation == 0: # change to enum
        x_disp = 0
        y_disp = side_len
    else:
        x_disp = side_len
        y_disp = 0

    for i in range(leg_len):

        upper_right = (upper_left[0] + side_len, upper_left[1])
        lower_left = (upper_left[0], upper_left[1] + side_len)
        lower_right = (upper_left[0] + side_len, upper_left[1] + side_len)

        cv.rectangle(img, upper_left , lower_right, (128,128,128), 5)

        # fillPoly is creating a displacement in the middle leg of the shape
        # points = np.array([list(upper_left), list(upper_right), list(lower_right), list(lower_left)])
        # cv.fillPoly(img, np.int32([points]), (220, 220, 220))
        
        upper_left = (upper_left[0] + x_disp, upper_left[1] + y_disp)
    
    return upper_left

# get parameters from command line args
args = get_args()
side_len = int(args.side)
legs = args.legs

canvas_size = 500
img = np.zeros((canvas_size, canvas_size, 3), np.uint8)

# recheck buffer values to accommodate rotation?
y_buffer = (legs[0] + legs[2]) * side_len
x_buffer = legs[1] * side_len

start = (random.randint(0, canvas_size - x_buffer), random.randint(0, canvas_size - y_buffer))
leg1_end = drawLeg(start, legs[0], 0)
leg1_end = (leg1_end[0], leg1_end[1] - side_len)
leg2_end = drawLeg(leg1_end, legs[1], 1)
leg2_end = (leg2_end[0] - side_len, leg2_end[1])
drawLeg(leg2_end, legs[2], 0)

# find middle point
leg2_len = legs[1]
if leg2_len % 2 == 0:
    midpoint_x = leg1_end[0] + (leg2_len / 2) * side_len
else:
    midpoint_x = leg1_end[0] + (leg2_len // 2) * side_len + side_len / 2

midpoint_y = leg1_end[1] + side_len / 2

def rotate_about_center(src, angle, scale=1.):
    w = src.shape[1]
    h = src.shape[0]
    r_angle = np.deg2rad(angle) 

    # calculate new image width and height
    nw = (abs(np.sin(r_angle)*h) + abs(np.cos(r_angle)*w))*scale
    nh = (abs(np.cos(r_angle)*h) + abs(np.sin(r_angle)*w))*scale
    # ask OpenCV for the rotation matrix
    rot_mat = cv.getRotationMatrix2D((nw*0.5, nh*0.5), angle, scale)
    # calculate move from old center to new center combined with rotation
    rot_move = np.dot(rot_mat, np.array([(nw-w)*0.5, (nh-h)*0.5,0]))
    # update the translation part of the transform
    rot_mat[0,2] += rot_move[0]
    rot_mat[1,2] += rot_move[1]

    return cv.warpAffine(src, rot_mat, (int(math.ceil(nw)), int(math.ceil(nh))))

# rotation causes jagged edges
rot_angle = random.randint(0, 360)
rot_img = rotate_about_center(img, rot_angle)
# rot_img = ndimage.rotate(img, rot_angle)
rot_img[rot_img == 0] = 255

# img[img == 0] = 255
# cv.imwrite('test.png', img)
cv.imwrite('test.png', rot_img)