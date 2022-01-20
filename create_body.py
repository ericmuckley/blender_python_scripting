# This example assumes we have a mesh object selected

import bpy
from bpy import data as D
from bpy import context as C
import bmesh

import numpy as np

scene = bpy.context.scene



def delete_all_objects_and_materials():
    """
    Delete all objects and materials.
    Run this to clear the environment.
    """
    # select all objects and delete them
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)
    # delete all materials
    for material in D.materials:
        material.user_clear()
        D.materials.remove(material)
    # delete all physics bakes    
    bpy.ops.ptcache.free_bake_all()


def add_camera(loc=(0, 0, 20), rot=(0, 0, 0)):
    """Add a camera to the scene."""
    bpy.ops.object.camera_add(location=loc, rotation=rot)
    C.object.name = 'cam'
    C.scene.camera = D.objects['cam']


def set_background(rgb_alpha=(0, 0, 0, 0)):
    """Set the background color of the scene."""
    bg = D.worlds["World"].node_tree.nodes["Background"]
    bg.inputs[0].default_value = rgb_alpha



def make_material(rgb_alpha, name='mat'):
    """Create a material to apply to an object.
    Use it like this:
    mat = make_gas_material((0.8, 0.04, 0.05, 1))
    C.active_object.data.materials.append(mat)
    """
    mat = D.materials.new(name=name)
    mat.use_nodes = True
    mat_nodes = mat.node_tree.nodes["Principled BSDF"]
    mat.diffuse_color = rgb_alpha
    mat_nodes.inputs[0].default_value = rgb_alpha
    mat_nodes.inputs[5].default_value = 0
    mat.roughness = 1
    mat.shadow_method = "OPAQUE"
    return mat




    
delete_all_objects_and_materials()


# add light source
bpy.ops.object.light_add(type='SUN', radius=1, location=(5, 35, 15))
bpy.context.object.name = 'light'


add_camera(loc=(0, 0, 75), rot=(0, 0, 0))

set_background(rgb_alpha=(0, 0, 0, 0))




skin_mat = make_material((0.3, 0.2, 0.2, 1), name='skin_mat')

N_PIX = {
    "head-x": 8,
    "head-y": 9,
}

for hx in np.linspace(-N_PIX['head-x'], N_PIX['head-x'], num=N_PIX['head-x']*2+1):
    for hy in np.linspace(-N_PIX['head-y'], N_PIX['head-y'], num=N_PIX['head-y']*2+1):
        
        if abs(hx * hy) < 45:
            bpy.ops.mesh.primitive_cube_add(size=1, location=(hx, hy, 0))
            C.active_object.data.materials.append(skin_mat)
            


nose_coords = [
    (-1, -2),
    (0, -2),
    (1, -2),
    (0, -1),
    (0, 0),
    (0, 1),
]

for cc in nose_coords:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cc[0], cc[1], 1))
    C.active_object.data.materials.append(skin_mat)


eye_mat = make_material((1, 1, 1, 1), name='eye_mat')
eye_coords = [
    (-4, 3),
    (-2, 3),
    (2, 3),
    (4, 3),
]
for cc in eye_coords:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cc[0], cc[1], 1))
    C.active_object.data.materials.append(eye_mat)


pupil_mat = make_material((0, 0, 0, 1), name='pupil_mat')
pupil_coords = [
    (-3, 3),
    (3, 3),
]
for cc in pupil_coords:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cc[0], cc[1], 1))
    C.active_object.data.materials.append(pupil_mat)





mouth_mat = make_material((0.2, 0.05, 0.05, 1), name='mouth_mat')
mouth_coords = [
    (-2, -6),
    (-1, -6),
    (0, -6),
    (1, -6),
    (2, -6),
]
for cc in mouth_coords:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cc[0], cc[1], 1))
    C.active_object.data.materials.append(mouth_mat)


objs = [obj for obj in C.scene.objects if obj.type == "MESH"]

ctx = bpy.context.copy()

# one of the objects to join
ctx['active_object'] = objs[0]

ctx['selected_editable_objects'] = objs

bpy.ops.object.join(ctx)


obj = [obj for obj in C.scene.objects if obj.type == "MESH"][0]
obj.name = "body"
bpy.data.objects["body"].select_set(True)


obj.data.use_auto_smooth = 1
#obj.data.auto_smooth_angle = math.pi/4  # 45 degrees

bpy.ops.object.shade_smooth()

