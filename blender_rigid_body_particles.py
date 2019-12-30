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

For obtaining location data from rigid body object at each keyframe:
obj = bpy.data.objects["Cube"]
print(obj.matrix_world.translation)



"""



def delete_all_objects_and_materials():
    """Delete all objects and materials. Run this
    at the beginning of the script to clear the environment."""
    # select all objects and delete them
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)
    # delete all physics bakes
    bpy.ops.ptcache.free_bake_all()
    # delete all materials
    for material in D.materials:
        material.user_clear()
        D.materials.remove(material)



def add_camera(loc=(0, 0, 20), rot=(0, 0, 0)):
    """Add a camera to the scene."""
    bpy.ops.object.camera_add(location=loc, rotation=rot)
    C.object.name = 'cam'
    C.scene.camera = D.objects['cam']



def boundary_plane(size, loc=(0, 0, 0), rot=(0, 0, 0),
    name=None, rigid_body_type='PASSIVE', mat=None):
    """Create bounding plane for rigid body simulation."""
    # create plane
    bpy.ops.mesh.primitive_plane_add(
        size=size, location=loc, rotation=rot)
    # name it
    if name:
        C.object.name = name
    # set material
    if mat:
        C.active_object.data.materials.append(mat)
    # make it a rigid object
    bpy.ops.rigidbody.objects_add()
    C.object.rigid_body.type = rigid_body_type
    # make collisions elastic
    C.object.rigid_body.restitution = 1
    C.object.rigid_body.friction = 0
    C.object.rigid_body.collision_margin = 0.01
    #C.object.rigid_body.mass = 100
    bpy.ops.object.modifier_add(type='SOLIDIFY')
    C.object.modifiers["Solidify"].thickness = 0.1
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Solidify")



def create_bounding_box(plane_size=5):
    """Create bounding box for rigid bodies by building 
    transparent cube from multiple planes."""
    # set location of each plane
    plane_locs = ((0, 0, -plane_size/2), (0, 0, plane_size/2),
        (-plane_size/2, 0, 0), (plane_size/2, 0, 0),
        (0, -plane_size/2, 0), (0, plane_size/2, 0))
    # set rotation of each plane
    plane_rots = ((0, 0, 0), (0, 0, 0),
        (0, np.pi/2, 0), (0, np.pi/2, 0),
        (np.pi/2, 0, 0), (np.pi/2, 0, 0))
    #set name of each plane
    plane_names = ('plane_low_z', 'plane_high_z',
        'plane_low_x', 'plane_high_x',
        'plane_low_y', 'plane_high_y',)
    # create transparent material
    mat = make_transparent_material()
    # create each plane
    for p in range(len(plane_locs)):
        boundary_plane(
            plane_size,
            loc=plane_locs[p],
            rot=plane_rots[p],
            name=plane_names[p],
            mat=mat)


def make_transparent_material(name='transparent'):
    """Create a transparent material."""
    mat = D.materials.new(name=name)
    mat.use_nodes = True
    mat.shadow_method = 'NONE'
    mat.blend_method = 'HASHED'
    mat.diffuse_color = (0, 0, 0, 0)
    mat.node_tree.nodes["Principled BSDF"].inputs[18].default_value = 0
    return mat


def make_gas_material(name='gas'):
    """Create a material for gas particles."""
    mat = D.materials.new(name=name)
    mat.use_nodes = True
    mat.diffuse_color = (0.3, 0.8, 0.8, 1)
    
    mat.node_tree.nodes["Principled BSDF"].inputs[
        0].default_value = (0.2, 0.8, 0.7, 1)

    mat.roughness = 1
    mat.shadow_method = 'NONE'
    return mat


def create_rigidbody_particle(loc=(0, 0, 0), radius=1, name=None,
    mass=None, mat=None):
    """Create a rigid body sphere to simulate a gas particle."""
    # create particle
    bpy.ops.mesh.primitive_uv_sphere_add(location=loc, radius=radius)
    # name particle
    if name:
        C.object.name = name
    bpy.ops.object.shade_smooth()
    # make it a rigid object with elastic collisions
    bpy.ops.rigidbody.objects_add()
    C.object.rigid_body.restitution = 1
    C.object.rigid_body.friction = 0
    C.object.rigid_body.linear_damping = 0
    C.object.rigid_body.angular_damping = 0
    C.object.display.show_shadows = False
    C.object.rigid_body.collision_margin = 0.01
    C.object.rigid_body.collision_shape = 'SPHERE'
    # change particle mass
    if mass:
        C.object.rigid_body.mass = mass
    # add material to particle
    if mat:
        C.active_object.data.materials.append(mat)
        
    bpy.ops.object.modifier_add(type='SOLIDIFY')
    C.object.modifiers["Solidify"].thickness = 0.05
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Solidify")




# ---------------------------- INITIALIZE ENVIRONMENT ------------------------

delete_all_objects_and_materials()

add_camera(loc=(14, -14, 6), rot=(np.pi/2.5, 0, np.pi/4))

# add light source
bpy.ops.object.light_add(type='SUN', radius=1.0, location=(0, 2, 5))
C.object.name = 'lamp'

# make background black
bg = D.worlds["World"].node_tree.nodes["Background"]
bg.inputs[0].default_value = (0, 0, 0, 0)

# set gravitational acceleration vector
C.scene.gravity = [0, 0, 0]


# ------------------------ INITIALIZE KEYFRAMES ------------------------------

# set start and end keyframes
start_kf, end_kf = 0, 250
C.scene.frame_start = start_kf
C.scene.frame_end = end_kf
# for animation, track current frame, specify desired number of key frames
current_kf = C.scene.frame_start
# set the scene to the current frame
C.scene.frame_set(current_kf)

# --------------------------- CREATE PARTICLES -------------------------------

create_bounding_box(plane_size=5)

# create gas particles
gas_particle_num = 200
mat = make_gas_material()
for i in range(gas_particle_num):
    create_rigidbody_particle(
        loc=(np.random.random(3)-0.5)/10,
        radius=0.001,
        mass=20,
        name='gas_particle_' + str(i).zfill(3),
        mat=mat)
particles = [p for p in D.objects if p.name.startswith('particle')]


# initialize keyframes for each particle
#[p.keyframe_insert(data_path='location', frame=current_kf) for p in particles]

#C.scene.rigidbody_world.constraints = D.collections["RigidBodyWorld"]



# -------------- Create bounding box using transparent planes ----------------

       



"""
- add starting velocities
- add shadlowless-material
- add plume of different shadowless material
- extend range of keyframes
- add depth of field
"""


'''
# increment the keyframe
current_kf += 1



# --------------- ANIMATE PARTICLES ------------------------------------------

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
.'''



# ------------------------------------------------------

C.scene.render.filepath = "/home/eric/Desktop/blender_render"
C.scene.render.image_settings.file_format = 'AVI_JPEG'
C.scene.render.image_settings.quality = 100
C.scene.rigidbody_world.steps_per_second = 300
C.scene.rigidbody_world.solver_iterations = 50

RENDER = True
if RENDER:
    bpy.ops.ptcache.bake_all(bake=True)
    bpy.ops.render.render('INVOKE_DEFAULT', animation=True)