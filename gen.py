import subprocess
import numpy as np
import os
import argparse
import random
import bpy
from math import *
from bpy.props import *

def get_args():
  parser = argparse.ArgumentParser()
 
  # get all script args
  _, all_arguments = parser.parse_known_args()
  double_dash_index = all_arguments.index('--')
  script_args = all_arguments[double_dash_index + 1: ]
 
  # add parser rules
  parser.add_argument('-n', '--number', help="number of videos you want to generate")
  parser.add_argument('-m', '--save', help="output dir, do not include the slash at the end of the folder name")
  parsed_script_args, _ = parser.parse_known_args(script_args)

  return parsed_script_args
    
def setup(output_path):
    def reset_scene():
        for o in bpy.context.scene.objects:
            o.select_set(True)
        bpy.ops.object.delete()
        
    def add_camera(cam_location, cam_rotation):
        bpy.ops.object.camera_add(location=cam_location, rotation=(radians(cam_rotation[0]), radians(cam_rotation[1]), radians(cam_rotation[2])))
        bpy.context.scene.camera = bpy.data.objects['Camera']

    # empty scene of everything
    reset_scene()

    # set camera location / rotation and add to scene
    cam_location=(10, 0, 0)
    cam_rotation = (0, 90, 0)
    add_camera(cam_location, cam_rotation)

    bpy.context.scene.render.filepath = '//%s/blank.png' % (output_path)
    bpy.ops.render.render( write_still=True )

def rotate(obj, obj_rotation, count):
    '''
    INPUT -----
        obj : the sole object of the scene (currently a hot pink monkey head)
        obj_rotation : the  x, y, z values (degrees) of the rotation, each randomly selected from range 0 to 360
        count : determines whether it is the first or second image in the stimulus
    
    performs the rotation and saves the post-rotation image of the scene in the output folder
    '''
    obj.rotation_euler = (radians(obj_rotation[0]), radians(obj_rotation[1]), radians(obj_rotation[2]))
    
    # save as png
    bpy.context.scene.render.filepath = '//%s/image%d.png' % (output_path, count)
    bpy.ops.render.render( write_still=True )
    
    return

def createObject(obj_type):
    if obj_type == "MONKEY":
        bpy.ops.mesh.primitive_monkey_add()
    elif obj_type == "CONE":
        bpy.ops.mesh.primitive_cone_add()
    
    # color the object, just for fun
    obj = bpy.context.active_object
    mat = bpy.data.materials.new(name="NewColor")
    obj.data.materials.append(mat) #add the material to the object
    mat.diffuse_color = (0.8, 0.4, 0.8, 1) #change color

    return obj


def genImages():
    '''
    There are two options: 
        1) show one object appearing twice
        2) show two different objects appearing once each
    
    Currently, it is set up to randomly choose between the options

    Objects currently being used are monkey head and cone, both colored hot pink. The cone only appears
    if option 2 is chosen, but this design can (and probably should be changed). Default object is thus
    the iconic monkey head, also known as Suzanne.

    Object rotation details are described in rotate() func above
    '''

    # randomly choose between 2 objects or 1 object
    choice = bool(random.getrandbits(1))

    if choice: # option 1 (one object appears twice)
        obj = createObject('MONKEY')

        # set random rotation parameters (x, y, z) and do perform rotations of the object
        obj_rotation_1 = random.sample(range(1, 100), 3)
        rotate(obj, obj_rotation_1, 1)

        obj_rotation_2 = random.sample(range(1, 100), 3)
        rotate(obj, obj_rotation_2, 2)

        # get rid of curr object
        obj.select_set(True)
        bpy.ops.object.delete() 

    else:
        obj = createObject('MONKEY')
        obj_rotation_1 = random.sample(range(1, 100), 3)
        rotate(obj, obj_rotation_1, 1)

        # get rid of curr object
        obj.select_set(True)
        bpy.ops.object.delete() 

        # new object! In this case, cone!
        obj = createObject('CONE')
        obj_rotation_2 = random.sample(range(1, 100), 3)
        rotate(obj, obj_rotation_2, 2)

        # get rid of curr object
        obj.select_set(True)
        bpy.ops.object.delete() 


# generates entire video using specified time per image (in seconds)
def stitch(times, count):
    os.system("ffmpeg -y -loop 1 -i %s/blank.png -t %d %s/a.mp4" % (output_path, times[0], output_path))
    os.system("ffmpeg -y -loop 1 -i %s/image1.png -t %d %s/b.mp4" % (output_path, times[1], output_path))
    os.system("ffmpeg -y -loop 1 -i %s/blank.png -t %d %s/c.mp4" % (output_path, times[2], output_path))
    os.system("ffmpeg -y -loop 1 -i %s/image2.png -t %d %s/d.mp4" % (output_path, times[3], output_path))

    os.system("mencoder -ovc copy -o %s/out%d.mp4 %s/a.mp4 %s/b.mp4 %s/c.mp4 %s/d.mp4" \
        % (output_path, count, output_path, output_path, output_path, output_path))

    print("########## Your stimulus has been made ##########")


# get parameters from command line args
args = get_args()
num_vids = int(args.number)
output_path = args.save

# set up scene and create the blank image used for stimulus
setup(output_path)

# generate num_vids stimuli by generating rotated objects & stitching together a video with them
times = [1, 2, 1, 2]
count = 1
for i in range(num_vids):
    genImages()
    stitch(times, count)
    count += 1