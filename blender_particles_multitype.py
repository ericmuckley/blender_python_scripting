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
    C.object.rigid_body.collision_margin = 0.1
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


def make_gas_material(rgb_alpha, name='gas'):
    """Create a material for gas particles."""
    mat = D.materials.new(name=name)
    mat.use_nodes = True
    mat_nodes = mat.node_tree.nodes["Principled BSDF"]
    mat.diffuse_color = rgb_alpha
    mat_nodes.inputs[0].default_value = rgb_alpha
    mat_nodes.inputs[5].default_value = 0
    mat.roughness = 1
    mat.shadow_method = 'NONE'
    return mat


def create_particle(loc=(0, 0, 0), rot=(0, 0, 0), radius=1, name=None,
    mat=None):
    """Create a sphere to simulate a gas particle."""
    bpy.ops.mesh.primitive_uv_sphere_add(
        location=loc,
        radius=radius)
    bpy.ops.object.shade_smooth()
    if name:
        C.object.name = name
    if mat:
        C.active_object.data.materials.append(mat)


def add_collision_properties(obj, mass=1):
    """Turn a mesh object into a rigid body for elastic collisions."""
    bpy.context.view_layer.objects.active = obj
    C.object.rigid_body.restitution = 1
    C.object.rigid_body.friction = 0
    C.object.rigid_body.linear_damping = 0
    C.object.rigid_body.angular_damping = 0
    C.object.display.show_shadows = False
    C.object.rigid_body.collision_margin = 0.1
    C.object.rigid_body.collision_shape = 'SPHERE'
    bpy.ops.object.modifier_add(type='SOLIDIFY')
    C.object.modifiers["Solidify"].thickness = 0.05
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Solidify")
    C.object.rigid_body.mass = mass


def set_background(rgb_alpha=(0, 0, 0, 0)):
    """Set the background color of the scene."""
    bg = D.worlds["World"].node_tree.nodes["Background"]
    bg.inputs[0].default_value = rgb_alpha


def render(filepath="/home/eric/Desktop/blender_render"):
    """Render the animation."""
    C.scene.render.filepath = filepath
    C.scene.render.image_settings.file_format = 'AVI_JPEG'
    C.scene.render.image_settings.quality = 100
    bpy.ops.ptcache.bake_all(bake=True)
    bpy.ops.render.render('INVOKE_DEFAULT', animation=True)


# ---------------------------- INITIALIZE ENVIRONMENT ------------------------

delete_all_objects_and_materials()

add_camera(loc=(30, -30, 13), rot=(np.pi/2.5, 0, np.pi/4))

# add light source
bpy.ops.object.light_add(type='SUN', radius=1.0, location=(10, -10, 10))
C.object.name = 'lamp'

set_background(rgb_alpha=(1, 1, 1, 1))

# set gravitational acceleration vector
C.scene.gravity = [0, 0, 0]

create_bounding_box(plane_size=10)

# ------------------------ INITIALIZE KEYFRAMES ------------------------------

# set start and end keyframes
start_kf, end_kf = 0, 500
C.scene.frame_start = start_kf
C.scene.frame_end = end_kf
# for animation, track current frame, specify desired number of key frames
current_kf = C.scene.frame_start
# set the scene to the current frame
C.scene.frame_set(current_kf)








# --------------------------- CREATE PARTICLES -------------------------------

# create gas particles
gas_particle_num = 50
mat = make_gas_material((0.8, 0.04, 0.05, 1))
for i in range(gas_particle_num):
    create_particle(
        loc=(np.random.random(3)-0.5),
        radius=0.001,
        name='gas_' + str(i).zfill(3),
        mat=mat)
particles = [p for p in D.objects if p.name.startswith('gas')]

# --------------- ANIMATE PARTICLES ------------------------------------------

# create initial keyframe state of each particle
for p in particles:
    C.view_layer.objects.active = p
    bpy.ops.rigidbody.object_add()
    C.object.rigid_body.type = 'ACTIVE'
    C.object.rigid_body.enabled = True
    C.object.rigid_body.kinematic = True
    kf_types = ('location', 'rigid_body.kinematic')
    [p.keyframe_insert(data_path=kft, frame=0) for kft in kf_types]
    add_collision_properties(p, mass=1)

# increment the keyframe and create new keyframe to add initial velocity
current_kf += 4

for p in particles:
    C.view_layer.objects.active = p
    current_location = p.location
    translate_by = 1 * (np.random.random(3) - 0.5)
    # translate particle
    p.location = tuple(map(sum, zip(current_location, translate_by)))
    bpy.context.object.rigid_body.kinematic = False
    kf_types = ('location', 'rigid_body.kinematic')
    [p.keyframe_insert(data_path=kft, frame=current_kf) for kft in kf_types]











# -------------------------------- CREATE PLUME ------------------------------

mat = make_gas_material((0, 0.02, 0.8, 1))
plume_locs = (
    (-1, -4, 0),
    (-0.5, -4, 0),
    (0, -4, 0),
    (0.5, -4, 0),
    (1, -4, 0),
    (-1, -4, 0.5),
    (-0.5, -4, 0.5),
    (0, -4, 0.5),
    (0.5, -4, 0.5),
    (1, -4, 0.5),
    (-1, -4, -0.5),
    (-0.5, -4, -0.5),
    (0, -4, -0.5),
    (0.5, -4, -0.5),
    (1, -4, -0.5))
    

for i in range(len(plume_locs)):
    create_particle(
        loc=plume_locs[i],
        radius=0.1,
        name='plume_' + str(i).zfill(3),
        mat=mat)

plumes = [p for p in D.objects if p.name.startswith('plume')]

for p in plumes:
    C.view_layer.objects.active = p
    bpy.ops.rigidbody.object_add()
    add_collision_properties(p, mass=10)

    # create initial keyframe state of each particle
    C.object.rigid_body.type = 'ACTIVE'
    C.object.rigid_body.enabled = True
    C.object.rigid_body.kinematic = True
    kf_types = ('location', 'rigid_body.kinematic')
    [p.keyframe_insert(data_path=kft, frame=100) for kft in kf_types]



    current_location = p.location
    translate_by = (0, 0.5, 0)
    # translate particle
    p.location = tuple(map(sum, zip(current_location, translate_by)))
    bpy.context.object.rigid_body.kinematic = False
    kf_types = ('location', 'rigid_body.kinematic')
    [p.keyframe_insert(data_path=kft, frame=105) for kft in kf_types]






# -------------------------- PREPARE RENDER ----------------------------------

# reset the starting and ending keyframes
C.scene.frame_start = start_kf
C.scene.frame_end = end_kf
# increase rigid body accuracy so objects don't pass through each other
C.scene.rigidbody_world.steps_per_second = 300
C.scene.rigidbody_world.solver_iterations = 50

#render()
