import numpy as np
import cv2 as cv
import argparse
import random
from random import randrange
import math
import os
# import xlwt 
# from xlwt import Workbook 
import openpyxl
from openpyxl import Workbook
import glob
import time


def get_args():
    parser = argparse.ArgumentParser()

    # get all script args
    _, all_arguments = parser.parse_known_args()
    double_dash_index = all_arguments.index('--')
    script_args = all_arguments[double_dash_index + 1: ]

    # add parser rules
    parser.add_argument('--vol', help="write how many stimuli you want to make")
    parsed_script_args, _ = parser.parse_known_args(script_args)

    return parsed_script_args

def get_rects(center, theta, side_len, orientation, all_points, all_centers):
    theta = np.radians(theta)
    c, s = np.cos(theta), np.sin(theta)
    R = np.matrix('{} {}; {} {}'.format(c, -s, s, c))

    # get coords relative to center
    p1_shift = [ - side_len / 2, - side_len / 2]
    p2_shift = [side_len / 2, - side_len / 2]
    p3_shift = [side_len / 2, side_len / 2]
    p4_shift = [ - side_len / 2, side_len / 2]
    
    # rotate coords about center
    p1_new = np.dot(p1_shift, R) + center
    p2_new = np.dot(p2_shift, R) + center
    p3_new = np.dot(p3_shift, R) + center
    p4_new = np.dot(p4_shift, R) + center

    # extract coords from np.dot output to neatly input into cv.line()
    p1 = (int(p1_new[0,0]), int(p1_new[0,1]))
    p2 = (int(p2_new[0,0]), int(p2_new[0,1]))
    p3 = (int(p3_new[0,0]), int(p3_new[0,1]))
    p4 = (int(p4_new[0,0]), int(p4_new[0,1]))
    
    all_points.extend([p1, p2, p3, p4])
    all_centers.append(center)

    if orientation == 1: # vertical leg
        new_center = (center[0] + side_len * np.sin(theta), center[1] + side_len * np.cos(theta))
    else: # horizontal leg
        theta = np.radians(np.degrees(theta) + 90)
        new_center = (center[0] + side_len * np.sin(theta), center[1] + side_len * np.cos(theta))

    return new_center

def translation(coord, canvas_size):
    x = coord[0]
    y = coord[1]
    translation = [0, 0]
    if x <= 0 or x >= canvas_size:
        x_trans = abs(x) if x <= 0 else canvas_size - x
        translation[0] = x_trans
    if y <= 0 or y >= canvas_size:
        y_trans = abs(y) if y <= 0 else canvas_size - y
        translation[1] = y_trans

    return translation

def make_img(rand_start, legs, theta, side_len):

    # set canvas size (change to parameter?)
    canvas_size = 64

    img = np.zeros((canvas_size, canvas_size, 3), np.uint8)

    all_points = []
    all_centers = []

    # set center for first leg's first square
    if rand_start:
        center = (random.randint(0, canvas_size), random.randint(0, canvas_size))
    else:
        # fix this
        center = (32,32)

    for i in range(legs[0]): #first leg, vertical
        center = get_rects(center, theta, side_len, 1, all_points, all_centers)
    center = all_centers[-1]
    for i in range(legs[1]+1): #second leg, horizontal
        center = get_rects(center, theta, side_len, 0, all_points, all_centers)
    for i in range(legs[2]): #third leg, vertical
        center = get_rects(center, theta, side_len, 1, all_points, all_centers)

    # using all the coordinates, find the translation necessary to keep the shape in frame
    translations = [translation(point, canvas_size) for point in all_points]
    max_x_trans = max([sub[0] for sub in translations], key = abs)
    max_y_trans = max([sub[1] for sub in translations], key = abs)

    all_points = [(point[0] + max_x_trans, point[1] + max_y_trans) for point in all_points]
    num_rects = int(len(all_points) / 4)
    for i in range(num_rects):
        corners = all_points[i * 4 : i * 4 + 4]
        # draw rectangle (dark gray)
        cv.line(img, corners[0], corners[1], (128,128,128), 1)
        cv.line(img, corners[1], corners[2], (128,128,128), 1)
        cv.line(img, corners[2], corners[3], (128,128,128), 1)
        cv.line(img, corners[3], corners[0], (128,128,128), 1)

        # fill in rectangle (light gray)
        # points = np.array([list(corners[0]), list(corners[1]), list(corners[2]), list(corners[3])])
        # cv.fillPoly(img, np.int32([points]), (220, 220, 220))

    # change black background to white
    img[img == 0] = 255

    return img

# get parameters from command line args
args = get_args()
num_stim = int(args.vol)

# image output path
# clear all images inside output folder if it already exists
out_path = os.path.abspath(os.getcwd()) + '/output/'
if not os.path.exists(out_path):
    os.makedirs(out_path)
else:
    files = glob.glob(out_path + '*')
    for f in files:
        os.remove(f)

start = time.time()

for i in range(num_stim):
    leg1 = randrange(1, 5)
    leg2 = randrange(5)
    leg3 = randrange(5) if leg2 != 0 else randrange(1,5)
    side_len = 4
    # rand_start = randrange(2)
    rand_start = 0
    rot_angle = randrange(360)

    # img = make_img(rand_start,[5, 5, 5], rot_angle, side_len)
    img = make_img(rand_start,[leg1, leg2, leg3], rot_angle, side_len)
    file_name = str(leg1) + "_" + str(leg2) + "_" + str(leg3) + "_" + str(rot_angle) + ".jpg"
    cv.imwrite(os.path.join(out_path , file_name), img)


end = time.time()
print("ELAPSED TIME FOR " + str(num_stim) + " STIMULI: " + str(end - start))

