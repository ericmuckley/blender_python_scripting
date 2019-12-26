import numpy as np
import bpy
from bpy import data as D
from bpy import context as C

"""
#~ PYTHON INTERACTIVE CONSOLE 3.7.4 (default, Oct  8 2019, 15:23:02)
[GCC 6.3.1 20170216 (Red Hat 6.3.1-3)]
Command History:     Up/Down Arrow
Cursor:              Left/Right Home/End
Remove:              Backspace/Delete
Execute:             Enter
Autocomplete:        Ctrl-Space
Zoom:                Ctrl +/-, Ctrl-Wheel
Builtin Modules:     bpy, bpy.data, bpy.ops, bpy.props, bpy.types,
                     bpy.context, bpy.utils, bgl, blf, mathutils
Convenience Imports: from mathutils import *; from math import *
Convenience Variables: C = bpy.context, D = bpy.data

To debug a python script, run blender script from the command line:
blender --background --python blender_molecules00.py

"""

# enable rigid body world
#bpy.ops.rigidbody.world_add()


# ---------------------- INITIALIZE ENVIRONMENT ----------------------

# select all objects and delete them
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# delete all materials
for material in bpy.data.materials:
    material.user_clear()
    bpy.data.materials.remove(material)



# add light source
bpy.ops.object.light_add(type='SUN', radius=1.0, location=(0, 2, 2))
bpy.context.object.name = 'lamp'

# add camera
cam_pos = [0, 0, 30]
cam_rot = [0, 0, 0]
bpy.ops.object.camera_add(location=cam_pos, rotation=cam_rot)
bpy.context.object.name = 'cam'


# make background black
bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)

# set gravitational acceleration vector
bpy.context.scene.gravity = [0, 0, 0]

# enable rigid bodies in the world
#bpy.ops.rigidbody.world_add()


# -------------- INITIALIZE KEYFRAMES ------------------------------

# set start and end keyframes
bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = 250

# for animation, track current frame, specify desired number of key frames
current_kf = bpy.context.scene.frame_start
# set the scene to the current frame
bpy.context.scene.frame_set(current_kf)


# ----------------- CREATE PARTICLES -------------------------------

# set current position
x, y, z = 0, 0, 0

# set number of gas particles
gas_particle_num = 50


# loop over each gas particle
for i in range(gas_particle_num):

    # create gas particle
    bpy.ops.mesh.primitive_uv_sphere_add(
        location=np.random.random(3)-0.5,
        radius=0.1)

    # name particle
    bpy.context.object.name = 'particle_' + str(i).zfill(3)
    # set sphere rendering smooth
    bpy.ops.object.shade_smooth()
    # make sphere a rigid object
    bpy.ops.rigidbody.objects_add()


# get list of all particles
particles = [p for p in bpy.data.objects if p.name.startswith('particle')]

# initialize keyframes for each particle
#[p.keyframe_insert(data_path='location', frame=current_kf) for p in particles]



#bpy.context.scene.rigidbody_world.constraints = bpy.data.collections["RigidBodyWorld"]


# ---------------------- Create bounding box --------------------------------





def boundary_plane(size, loc=(0, 0, 0), rot=(0, 0, 0),
    name=None, rigid_body_type='PASSIVE'):
    """Create bounding plane for rigid body simulation."""
    # create plane
    bpy.ops.mesh.primitive_plane_add(
        size=size, location=loc, rotation=rot)
    # name it
    if name:
        bpy.context.object.name = name
    # make it a rigid object
    bpy.ops.rigidbody.objects_add()
    bpy.context.object.rigid_body.type = rigid_body_type
    


# create new transparent material 
mat_transparent = bpy.data.materials.new(name='transparent')
#mat_transparent.alpha = (0, 0 ,0)
#current.data.materials.append(mat)


plane_size = 3

plane_locs = (
    (0, 0, -plane_size/2), (0, 0, plane_size/2),
    (-plane_size/2, 0, 0), (plane_size/2, 0, 0),
    (0, -plane_size/2, 0), (0, plane_size/2, 0))
    
plane_rots = (
    (0, 0, 0), (0, 0, 0),
    (0, np.pi/2, 0), (0, np.pi/2, 0),
    (np.pi/2, 0, 0), (np.pi/2, 0, 0))

plane_names = (
    'plane_low_z', 'plane_high_z',
    'plane_low_x', 'plane_high_x',
    'plane_low_y', 'plane_high_y',)


for p in range(len(plane_locs)):
    boundary_plane(plane_size,
        loc=plane_locs[p],
        rot=plane_rots[p],
        name=plane_names[p])















'''
# increment the keyframe
current_kf += 1


# -------------- ANIMATE PARTICLES ------------------------------------------

for i in range(0, 250):
    
    # loop over each particle
    for p in particles:
        
        # get current location of particle and translate it
        current_location = p.location
        # get new location of particle
        translate_by = 0.5 * (np.random.random(3) - 0.5)
        # translate particle
        p.location = tuple(map(sum, zip(current_location, translate_by)))

        # insert new keyframe
        p.keyframe_insert(data_path='location', frame=current_kf)

    # increment the keyframe
    current_kf += 1
'''