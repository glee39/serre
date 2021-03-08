import os
import glob
import cv2
import numpy as np
import argparse
import random
from random import randrange
import re

def get_args():
    parser = argparse.ArgumentParser()

    # get all script args
    _, all_arguments = parser.parse_known_args()
    double_dash_index = all_arguments.index('--')
    script_args = all_arguments[double_dash_index + 1: ]

    # add parser rules
    parser.add_argument('--sample', help="1 = 2 of same image, 2 = same shape at diff rotation, 3 = diff shapes")
    parsed_script_args, _ = parser.parse_known_args(script_args)

    return parsed_script_args

def find_img(files, classes, same):
    if same == 1:
        for f in files:
            curr = re.split('[_ .]', f)
            if curr[0] == classes[0] and curr[1] == classes[1] and curr[2] == classes[2] and curr[3] != classes[3]:
                return f
    else:
        for f in files:
            curr = re.split('[_ .]', f)
            if curr[0] != classes[0] or curr[1] != classes[1] or curr[2] != classes[2]:
                return f

def main(sample_type, out_path):
    files = glob.glob(out_path + '*')
    num_files = len(files)

    if sample_type == 1:
        img = files[randrange(num_files)]
        img_mat = cv2.imread(img)
        return (img_mat, img_mat)
    elif sample_type == 2:
        img1 = files[randrange(num_files)]
        classes = re.split('[_ .]', img1)
        img2 = find_img(files, classes, 1)
        return (cv2.imread(img1), cv2.imread(img2))
    elif sample_type == 3:
        img1 = files[randrange(num_files)]
        classes = re.split('[_ .]', img1)
        img2 = find_img(files, classes, 0)
        return (cv2.imread(img1), cv2.imread(img2))

# get parameters from command line args
args = get_args()
sample_type = int(args.sample)

# access file names and search
out_path = os.path.abspath(os.getcwd()) + '/output/'
img1, img2 = main(sample_type, out_path)

cv2.imshow("1", img1)
cv2.waitKey(0)
cv2.imshow("2", img2)
cv2.waitKey(0)
